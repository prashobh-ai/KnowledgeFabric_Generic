"""Tenant-aware fabric build.

    python -m pipeline.build_index --tenant q-airlines

Reads one tenant's corpus, produces one tenant's index. Every tenant is an
independent build with its own vocabulary, graph specification and intent model,
which is what lets a single Actions matrix produce /t/q-airlines/ and
/t/q-cruise/ from the same code without either knowing the other exists.

Pipeline:
    documents -> normalise -> chunk -> BM25 (lexical)
                                    -> LSA  (semantic)
                                    -> typed knowledge graph (domain-specified)
                                    -> facets
              -> site/t/<slug>/data/index.json + semantic.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from .bm25_index import build_bm25_index
from .chunker import Chunk, tokenize
from .connectors.documents import DocumentConnector
from .docmeta import resolve as resolve_date
from .domain_graph import spec_for
from .graph import build_knowledge_graph
from .semantic import build_semantic_index
from .textnorm import analyse, build_vocabulary, chunk_quality, normalize

TARGET_CHARS = 700


def records_to_chunks(records):
    chunks, aligned, cid = [], [], 0
    doc_ids, buffer, buf_key = {}, [], None

    def doc_id_for(name):
        if name not in doc_ids:
            doc_ids[name] = len(doc_ids)
        return doc_ids[name]

    def flush():
        nonlocal buffer, cid
        if not buffer:
            return
        first = buffer[0]
        text = "\n\n".join(r.text for r in buffer)
        name = first.metadata.get("document_name") or first.title
        chunks.append(Chunk(chunk_id=cid, document_id=doc_id_for(name), document_name=name,
                            page=first.page, section_path=list(first.section_path),
                            paragraph_indices=[r.metadata.get("paragraph_index", 0) for r in buffer],
                            text=text, paragraph_excerpt=first.text[:200], tokens=tokenize(text)))
        aligned.append(first)
        cid += 1
        buffer = []

    for rec in records:
        key = (rec.metadata.get("document_name"), tuple(rec.section_path), rec.page)
        if buf_key is not None and key != buf_key:
            flush()
        buf_key = key
        buffer.append(rec)
        if sum(len(r.text) for r in buffer) >= TARGET_CHARS:
            flush()
    flush()
    return chunks, aligned


def build_facets(records):
    facets = defaultdict(lambda: defaultdict(int))
    for r in records:
        facets["source_type"][r.source_type] += 1
        for key in ("doc_type", "domain", "owner", "year"):
            v = (r.metadata or {}).get(key)
            if v:
                facets[key][str(v)] += 1
    return {k: dict(sorted(v.items(), key=lambda kv: -kv[1])[:60]) for k, v in facets.items()}


def build(tenant_slug: str, root: Path = Path(".")) -> dict:
    tdir = root / "tenants" / tenant_slug
    cfg = json.loads((tdir / "tenant.json").read_text())
    out_dir = root / "site" / "t" / tenant_slug / "data"

    print("=" * 70)
    print(f"  {cfg['name']} — {cfg['industry']} / {cfg['subtype']}")
    print("=" * 70)

    print("\n[1/7] Ingesting")
    records = list(DocumentConnector(tdir / "docs").fetch())
    print(f"      {len(records)} records from {cfg['corpus']['documents']} documents")

    print("\n[2/7] Normalising")
    vocab = build_vocabulary([r.text for r in records])
    repaired = 0
    for r in records:
        cleaned = normalize(r.text, vocab)
        if cleaned != r.text:
            repaired += 1
        r.text = cleaned
    print(f"      lexicon {len(vocab)} words · {repaired} records repaired")

    print("\n[3/7] Chunking")
    chunks, aligned = records_to_chunks(records)
    print(f"      {len(chunks)} chunks")

    print("\n[4/7] Lexical index")
    bm25 = build_bm25_index(chunks)
    print(f"      vocab={len(bm25['vocab'])} avgdl={bm25['avgdl']:.1f}")

    print("\n[5/7] Semantic index")
    semantic = build_semantic_index([c.text for c in chunks])
    if semantic.get("enabled"):
        print(f"      dims={semantic['dims']} variance={semantic['explained_variance']:.1%}")
    else:
        print(f"      disabled: {semantic.get('reason')}")

    print("\n[6/7] Knowledge graph")
    spec = spec_for(cfg["corpus"]["generator"], cfg["corpus"].get("profile"))

    # The graph must see the WHOLE chunk, not the paragraph the chunk started
    # from. `aligned` holds one representative record per chunk for metadata
    # purposes, and its .text is only that first paragraph — so a document that
    # cites another in its second paragraph produced no edge at all. Give the
    # graph the merged text while keeping the representative's metadata.
    from copy import copy
    graph_records = []
    for rec, ch in zip(aligned, chunks):
        g = copy(rec)
        g.text = ch.text
        graph_records.append(g)

    graph = build_knowledge_graph(graph_records, [c.chunk_id for c in chunks], spec)
    gs = graph["stats"]
    print(f"      {gs['node_count']} nodes · {gs['edge_count']} edges · "
          f"{gs['cross_document_entities']} cross-document entities")
    for et, n in sorted(gs["edges_by_type"].items(), key=lambda kv: -kv[1])[:6]:
        print(f"        {et:24} {n}")

    print("\n[7/7] Assembling")
    chunk_to_doc = {c.chunk_id: c.document_id for c in chunks}
    entities = []
    for n in graph["nodes"]:
        docs_for = sorted({chunk_to_doc[c] for c in n["chunks"] if c in chunk_to_doc})
        entities.append({
            "id": n["id"], "name": n["name"], "canonical": n["name"].lower(),
            "kind": n["kind"], "mention_count": n["mentions"], "mentions": n["mentions"],
            "count": n["mentions"], "chunk_ids": n["chunks"], "chunks": n["chunks"],
            "document_ids": docs_for, "doc_types": n["doc_types"],
            "cross_source": n["cross_document"], "cross_document": n["cross_document"],
            "degree": n.get("degree", 0),
        })

    relationships = [{"source": e["source"], "target": e["target"], "weight": e["weight"],
                      "kind": e["type"], "type": e["type"], "evidence_chunks": e["evidence"]}
                     for e in graph["edges"]]

    idx_of = {c.chunk_id: i for i, c in enumerate(chunks)}
    chunk_entities = [[] for _ in chunks]
    for n in graph["nodes"]:
        for ch in n["chunks"]:
            i = idx_of.get(ch)
            if i is not None and n["id"] not in chunk_entities[i]:
                chunk_entities[i].append(n["id"])

    docs_meta, head = {}, {}
    for c, rec in zip(chunks, aligned):
        head.setdefault(c.document_name, "")
        if len(head[c.document_name]) < 4000:
            head[c.document_name] += " " + c.text
    for c, rec in zip(chunks, aligned):
        d = docs_meta.setdefault(c.document_name, {
            "id": c.document_id, "name": c.document_name,
            "source_type": rec.source_type, "source_system": rec.source_system,
            "domain": cfg["subtype"], "doc_type": (rec.metadata or {}).get("doc_type", ""),
            "url": "", "page_count": 1, "chunk_count": 0,
            **{f"date_{k}": v for k, v in resolve_date(
                source_path=Path(rec.metadata["source_path"]) if (rec.metadata or {}).get("source_path") else None,
                text=head.get(c.document_name, "")).items()},
        })
        d["chunk_count"] += 1

    serialized, kinds = [], defaultdict(int)
    for i, (c, rec) in enumerate(zip(chunks, aligned)):
        infos = analyse(c.text, vocab)
        for si in infos:
            kinds[si.kind] += 1
        serialized.append({
            "id": c.chunk_id, "document_id": c.document_id, "document_name": c.document_name,
            "page": c.page, "section_path": c.section_path,
            "paragraph_indices": c.paragraph_indices, "text": c.text,
            "paragraph_excerpt": c.paragraph_excerpt, "entities": chunk_entities[i],
            "source_type": rec.source_type, "source_system": rec.source_system,
            "url": "", "meta": rec.metadata, "quality": chunk_quality(infos),
            "sents": [{"o": s.offset, "l": s.length, "k": s.kind, "q": s.quality} for s in infos],
        })
    total = sum(kinds.values())
    print(f"      sentences {total} · usable prose {kinds.get('prose',0)} "
          f"({kinds.get('prose',0)/max(total,1):.0%})")

    index = {
        "version": "3.0", "generator": "knowledge-fabric/multi-tenant",
        "tenant": {k: cfg[k] for k in ("slug", "name", "industry", "subtype",
                                       "tagline", "persona", "accent", "accent_2",
                                       "highlights")},
        "documents": list(docs_meta.values()), "chunks": serialized,
        "entities": entities, "relationships": relationships,
        "graph": {"node_types": graph["node_types"], "edge_types": graph["edge_types"],
                  "stats": gs},
        "facets": build_facets(aligned), "bm25": bm25,
        "retrieval": {"modes": ["lexical", "semantic", "hybrid"],
                      "default": "hybrid" if semantic.get("enabled") else "lexical",
                      "fusion": "reciprocal_rank_fusion", "rrf_k": 60},
        "stats": {"document_count": len(docs_meta), "chunk_count": len(chunks),
                  "entity_count": len(entities), "relationship_count": len(relationships),
                  "vocab_size": len(bm25["vocab"]), "source_count": 1,
                  "record_count": len(records),
                  "cross_source_products": gs["cross_document_entities"],
                  "semantic_enabled": bool(semantic.get("enabled"))},
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False,
                                                   separators=(",", ":")))
    (out_dir / "semantic.json").write_text(json.dumps(semantic, separators=(",", ":")))
    qs = json.loads((tdir / "questions.json").read_text())
    (out_dir / "questions.json").write_text(json.dumps(qs, indent=1))

    i_mb = (out_dir / "index.json").stat().st_size / 1024 / 1024
    s_mb = (out_dir / "semantic.json").stat().st_size / 1024 / 1024
    print(f"\n[OK] site/t/{tenant_slug}/data — {i_mb + s_mb:.2f} MB total")
    print("=" * 70)
    return index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--root", type=Path, default=Path("."))
    args = ap.parse_args()
    build(args.tenant, args.root)


if __name__ == "__main__":
    main()
