"""Synthetic corpus engine.

Generates document sets that read as real to a practitioner while containing
nothing real. No client name, document, or dataset is used anywhere.

WHY BUILD THIS RATHER THAN COLLECT PUBLIC DOCUMENTS
    Public corpora exist for most of these domains, but they are the wrong
    shape for a demo. They are inconsistent in format, licensed unevenly, and —
    fatally — they do not cross-reference each other. A knowledge graph has
    nothing to bridge if every document is about something different.

    Generated corpora let us guarantee the one property the demo depends on:
    the same identifier appears in documents of different types, written in
    different registers, by different notional authors. That is what produces a
    real cross-document link rather than a coincidental keyword overlap.

THE THREADING MODEL
    Each domain declares a SPINE entity — the identifier a practitioner
    actually navigates by:

        aviation             aircraft registration + ATA chapter
        healthcare provider  care pathway + clinical policy number
        healthcare payer     medical policy number + procedure code
        pharma               study identifier
        devices              device model + clearance number
        banking              obligation reference + control identifier
        insurance            policy form number
        maritime             vessel + equipment tag
        retail               article number + vendor identifier
        quality              requirement identifier

    Spine values are drawn from a fixed pool per tenant and deliberately reused
    across document types, so retrieval genuinely has to cross documents to
    answer a question. That is the behaviour we are demonstrating, and it has to
    be true rather than staged.

DETERMINISM
    Everything derives from one seed. Two builds of the same tenant produce
    byte-identical corpora, so a demo shown on Tuesday is the demo shown on
    Friday, and a regression in retrieval is never confused with a change in
    the data.
"""
from __future__ import annotations

import hashlib
import random
import textwrap
from dataclasses import dataclass, field
from pathlib import Path


# --------------------------------------------------------------------------- model
@dataclass
class SynthDoc:
    """One generated document, ready to be written to disk."""
    filename: str
    title: str
    doc_type: str
    body: str
    spine: dict = field(default_factory=dict)   # identifiers threaded into this doc
    meta: dict = field(default_factory=dict)


@dataclass
class DomainPack:
    """Everything domain-specific lives here. The engine stays generic."""
    key: str
    spine_fields: dict            # field name -> list of literal values or a callable
    doc_types: list               # list of dicts: name, count_share, sections, uses_spine
    vocabulary: dict              # named term pools used inside section bodies
    regulations: list             # (citation, short description)
    systems: list                 # enterprise systems named in the text
    roles: list                   # job titles used as notional authors/approvers
    question_seeds: list          # realistic practitioner questions, for the bank


# --------------------------------------------------------------------------- helpers
def stable_rng(seed: int, *parts: str) -> random.Random:
    """A deterministic RNG keyed on the seed plus a label, so each document
    stream is independent and reproducible regardless of generation order."""
    h = hashlib.sha256(("|".join(parts)).encode()).hexdigest()[:12]
    return random.Random(seed + int(h, 16))


def wrap(text: str, width: int = 92) -> str:
    out = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
        elif para.lstrip().startswith(("- ", "* ", "|", "#")):
            out.append(para)
        else:
            out.extend(textwrap.wrap(para, width=width) or [""])
    return "\n".join(out)


def pick(rng: random.Random, seq, n: int = 1):
    if n == 1:
        return rng.choice(seq)
    return rng.sample(seq, min(n, len(seq)))


# --------------------------------------------------------------------------- engine
class CorpusEngine:
    def __init__(self, pack: DomainPack, seed: int, tenant_name: str):
        self.pack = pack
        self.seed = seed
        self.tenant = tenant_name
        # Document numbers are index-derived, so two tenants sharing a domain
        # pack would issue the same series — Q-Airlines and Q-AeroTech both
        # opening at ADCR-2024-0100. Offsetting the series per tenant keeps
        # every organisation's numbering its own, deterministically.
        self.id_offset = (seed % 7919) % 400

    # ---- spine pool -----------------------------------------------------
    def build_spine_pool(self, size: int = 14) -> list[dict]:
        """A fixed cast of identifiers reused across the corpus. Size matters:
        too many and no identifier recurs often enough to bridge documents; too
        few and every document looks like every other one. Around a dozen gives
        each identifier 4-6 appearances across different document types."""
        rng = stable_rng(self.seed, self.pack.key, "spine")
        pool = []
        for i in range(size):
            row = {}
            for field_name, source in self.pack.spine_fields.items():
                row[field_name] = source(rng, i) if callable(source) else pick(rng, source)
            pool.append(row)
        return pool

    # ---- generation -----------------------------------------------------
    def generate(self, total: int) -> list[SynthDoc]:
        """Two passes, because documents must be able to cite each other.

        A single pass can thread the SPINE across document types — the same tail
        number in a directive, a task card and a technical log. That alone gives
        a graph nodes but almost no typed edges, because nothing says WHICH
        directive the task card closes.

        Real operational documents cite each other by number. So: pass one
        allocates every document's identifier and indexes them by spine value;
        pass two renders bodies with those identifiers available, letting a task
        card name the directive it closes and an engineering order name the
        service bulletin it implements. That is what produces CLOSES and
        IMPLEMENTS edges rather than a co-occurrence cloud.
        """
        spine_pool = self.build_spine_pool()
        shares = [dt.get("count_share", 1.0) for dt in self.pack.doc_types]
        total_share = sum(shares)

        # ---- pass 1: allocate identifiers ---------------------------------
        plan = []
        for dt, share in zip(self.pack.doc_types, shares):
            n = max(1, round(total * share / total_share))
            for i in range(n):
                rng = stable_rng(self.seed, self.pack.key, dt["name"], str(i))
                spine = spine_pool[(i * 3 + hash(dt["name"]) % 7) % len(spine_pool)]
                ctx = self._context(dt, spine, rng, i)
                doc_id = dt.get("id", lambda c: f"DOC-{c['idx']:04d}")(ctx)
                plan.append({"dt": dt, "spine": spine, "rng": rng, "idx": i,
                             "ctx": ctx, "id": doc_id})

        # Index identifiers by document type and by spine value, so a renderer
        # can ask for "a directive concerning this aircraft".
        by_type: dict[str, list] = {}
        by_type_spine: dict[tuple, list] = {}
        primary = list(self.pack.spine_fields)[0]
        for p in plan:
            by_type.setdefault(p["dt"]["name"], []).append(p["id"])
            key = (p["dt"]["name"], str(p["spine"].get(primary)))
            by_type_spine.setdefault(key, []).append(p["id"])

        self._xref = {"by_type": by_type, "by_type_spine": by_type_spine,
                      "primary": primary}

        # ---- pass 2: render with cross-references available -----------------
        docs = []
        for p in plan:
            p["ctx"]["ref"] = self._ref_fn(p["spine"], p["id"])
            docs.append(self._render_planned(p))
        return docs[:total]

    def _ref_fn(self, spine: dict, self_id: str):
        """ref('Maintenance Task Card') -> an identifier of that type, preferring
        one that shares this document's spine value so the citation is coherent."""
        xr = self._xref
        primary = xr["primary"]

        def ref(doc_type_name: str) -> str:
            same = [i for i in xr["by_type_spine"].get(
                (doc_type_name, str(spine.get(primary))), []) if i != self_id]
            if same:
                return same[0]
            any_ = [i for i in xr["by_type"].get(doc_type_name, []) if i != self_id]
            return any_[0] if any_ else ""
        return ref

    def _context(self, dt: dict, spine: dict, rng: random.Random, idx: int) -> dict:
        pack = self.pack
        # Real operational documents name people. So do these — but every
        # identity is invented, paired with a fictional staff reference, and
        # never carries an email address, telephone number or national
        # identifier. See pipeline/domain_graph.py for the pool and the scanner.
        from ..domain_graph import person
        owner_role = pick(rng, pack.roles)
        appr_role = pick(rng, pack.roles)
        owner = person(rng, owner_role)
        approver = person(rng, appr_role)

        ctx = {
            "tenant": self.tenant,
            "role": owner_role,
            "approver": appr_role,
            "owner_person": owner["display"],
            "approver_person": approver["display"],
            "system": pick(rng, pack.systems),
            "system_2": pick(rng, pack.systems),
            "reg": pick(rng, pack.regulations),
            "rng": rng,
            "idx": idx + self.id_offset,
            "seq": idx,
            **spine,
        }
        for name, pool in pack.vocabulary.items():
            ctx[name] = pick(rng, pool)
            ctx[f"{name}_list"] = pick(rng, pool, min(4, len(pool)))
        ctx["ref"] = lambda _name: ""       # replaced in pass two
        return ctx

    def _render_planned(self, p: dict) -> SynthDoc:
        dt, ctx, idx = p["dt"], p["ctx"], p["idx"]
        doc_id = p["id"]
        title = dt["title"](ctx)
        sections = []
        for sec_name, sec_fn in dt["sections"]:
            body = sec_fn(ctx)
            sections.append(f"## {sec_name}\n\n{wrap(body)}")

        header = (
            f"# {title}\n\n"
            f"**Document number:** {doc_id}  \n"
            f"**Document type:** {dt['name']}  \n"
            f"**Owner:** {ctx['owner_person']}  \n"
            f"**Approved by:** {ctx['approver_person']}  \n"
            f"**Revision:** {chr(65 + idx % 6)}  \n"
            f"**Effective:** {2024 + idx % 3}-{1 + idx % 12:02d}-{1 + idx % 27:02d}  \n"
        )
        body = header + "\n" + "\n\n".join(sections) + "\n"

        slug = "".join(ch if ch.isalnum() else "_" for ch in title)[:70].strip("_")
        return SynthDoc(
            filename=f"{doc_id}_{slug}.md",
            title=title,
            doc_type=dt["name"],
            body=body,
            spine=dict(p["spine"]),
            meta={"doc_id": doc_id, "domain": self.pack.key, "owner": ctx["role"]},
        )


# --------------------------------------------------------------------------- writer
DISCLAIMER = """<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

"""


def write_corpus(docs: list[SynthDoc], out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    for existing in out_dir.glob("*.md"):
        existing.unlink()

    by_type: dict[str, int] = {}
    spine_hits: dict[str, set] = {}
    for d in docs:
        (out_dir / d.filename).write_text(DISCLAIMER + d.body, encoding="utf-8")
        by_type[d.doc_type] = by_type.get(d.doc_type, 0) + 1
        for k, v in d.spine.items():
            spine_hits.setdefault(k, set()).add(str(v))

    return {
        "documents": len(docs),
        "by_type": by_type,
        "spine_values": {k: len(v) for k, v in spine_hits.items()},
        "bytes": sum(len((out_dir / d.filename).read_text()) for d in docs),
    }
