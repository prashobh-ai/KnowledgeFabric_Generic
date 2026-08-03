"""Typed knowledge graph — domain-driven, not hard-coded.

The previous implementation carried a medical-device gazetteer in the source: an
ANALYTES dictionary, PRODUCT_ALIASES regexes for StatStrip and BioProfile, edge
types named for FDA clearances. That works for exactly one corpus. Point it at an
airline and it finds nothing, because nothing in a task card looks like a blood
analyte.

Here the domain is supplied, not assumed. Each domain pack declares:

    entity_patterns   {kind: regex}       what an entity of this kind looks like
    edge_rules        [(from, to, type)]  which kinds may link, and how

and the engine is generic. Adding a vertical is a data change.

WHY THE EDGES MATTER MORE THAN THE NODES
    Co-occurrence graphs are easy and nearly useless: they say two things
    appeared near each other, which in a large corpus is almost everything. A
    typed edge says something specific — this directive GOVERNS this task card,
    this policy AUTHORISES this pathway — and that is what supports a multi-hop
    answer a reviewer can follow.

    So edges form only between kinds the domain says may legitimately link. A
    pair that co-occurs with no declared rule produces no edge. The graph stays
    sparse and meaningful rather than dense and decorative.
"""
from __future__ import annotations

import re
from collections import defaultdict


class DomainGraphSpec:
    """Everything the graph needs to know about one domain."""

    def __init__(self, entity_patterns: dict, edge_rules: list):
        self.entity_patterns = {k: re.compile(v) for k, v in entity_patterns.items()}
        self.edge_rules = edge_rules

    def allowed_edge(self, kind_a: str, kind_b: str):
        for src, dst, etype in self.edge_rules:
            if (kind_a, kind_b) in ((src, dst), (dst, src)):
                return etype
        return None

    def extract(self, text: str, limit_per_kind: int = 6):
        found = []
        for kind, pattern in self.entity_patterns.items():
            seen = set()
            for m in pattern.finditer(text):
                value = (m.group(1) if m.groups() else m.group(0)).strip()
                if not value or len(value) > 90:
                    continue
                key = value.lower()
                if key in seen:
                    continue
                seen.add(key)
                found.append((kind, value))
                if len(seen) >= limit_per_kind:
                    break
        return found


class KnowledgeGraph:
    def __init__(self, spec: DomainGraphSpec):
        self.spec = spec
        self._nodes = {}
        self.nodes = []
        self._edges = {}

    def node(self, kind, name):
        name = (name or "").strip()
        if not name:
            return None
        key = (kind, name.lower())
        if key in self._nodes:
            nid = self._nodes[key]
            self.nodes[nid]["mentions"] += 1
            return nid
        nid = len(self.nodes)
        self._nodes[key] = nid
        self.nodes.append({"id": nid, "kind": kind, "name": name, "mentions": 1,
                           "chunks": [], "sources": [], "doc_types": []})
        return nid

    def observe(self, nid, chunk_id, source_type, doc_type=""):
        if nid is None:
            return
        n = self.nodes[nid]
        if len(n["chunks"]) < 60 and chunk_id not in n["chunks"]:
            n["chunks"].append(chunk_id)
        if source_type and source_type not in n["sources"]:
            n["sources"].append(source_type)
        if doc_type and doc_type not in n["doc_types"]:
            n["doc_types"].append(doc_type)

    def edge(self, a, b, etype, evidence=None):
        if a is None or b is None or a == b:
            return
        key = (a, b, etype)
        e = self._edges.get(key)
        if e is None:
            e = {"source": a, "target": b, "type": etype, "weight": 0, "evidence": []}
            self._edges[key] = e
        e["weight"] += 1
        if evidence is not None and len(e["evidence"]) < 12 and evidence not in e["evidence"]:
            e["evidence"].append(evidence)

    def ingest(self, records, chunk_ids):
        for rec, cid in zip(records, chunk_ids):
            doc_type = (rec.metadata or {}).get("doc_type", "")
            entities = self.spec.extract(rec.text)
            # Entities the connector already resolved are trusted over anything
            # the patterns find in free text.
            for kind, value in (rec.entities or []):
                if kind and value:
                    entities.append((kind, value))

            ids = []
            for kind, value in entities:
                nid = self.node(kind, value)
                self.observe(nid, cid, rec.source_type, doc_type)
                if nid is not None:
                    ids.append((kind, nid))

            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    ka, na = ids[i]
                    kb, nb = ids[j]
                    etype = self.spec.allowed_edge(ka, kb)
                    if etype:
                        self.edge(na, nb, etype, cid)

    def finalize(self, max_edges: int = 4000):
        # An entity appearing in several DOCUMENT TYPES is what makes a
        # cross-document answer possible. Flag it so the UI can say so.
        cross = 0
        for n in self.nodes:
            n["cross_document"] = len(n["doc_types"]) >= 2
            if n["cross_document"]:
                cross += 1

        edges = sorted(self._edges.values(), key=lambda e: -e["weight"])[:max_edges]
        keep = {e["source"] for e in edges} | {e["target"] for e in edges}

        degree = defaultdict(int)
        for e in edges:
            degree[e["source"]] += 1
            degree[e["target"]] += 1
        for n in self.nodes:
            n["degree"] = degree.get(n["id"], 0)

        by_type = defaultdict(int)
        for e in edges:
            by_type[e["type"]] += 1

        return {
            "nodes": [n for n in self.nodes if n["id"] in keep or n["mentions"] > 2],
            "edges": edges,
            "node_types": sorted({n["kind"] for n in self.nodes}),
            "edge_types": sorted(by_type.keys()),
            "stats": {"node_count": len(self.nodes), "edge_count": len(edges),
                      "cross_document_entities": cross, "edges_by_type": dict(by_type)},
        }


def build_knowledge_graph(records, chunk_ids, spec: DomainGraphSpec):
    kg = KnowledgeGraph(spec)
    kg.ingest(records, chunk_ids)
    return kg.finalize()
