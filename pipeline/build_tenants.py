"""Tenant builder.

    python -m pipeline.build_tenants              # every tenant
    python -m pipeline.build_tenants q-airlines   # one tenant

For each tenant in tenants/registry.yml this produces:

    tenants/<slug>/docs/          the synthetic corpus
    tenants/<slug>/brand/logo.svg a generated mark
    tenants/<slug>/tenant.json    resolved configuration for the site
    tenants/<slug>/questions.json seeded questions for the demo bank

Everything is deterministic from the registry seed, so a rebuild produces an
identical result. That matters more than it sounds: a demo shown on Tuesday must
be the demo shown on Friday, and a change in retrieval behaviour must never be
confusable with a change in the underlying data.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

import yaml

from .synth.engine import CorpusEngine, write_corpus

REGISTRY = Path("tenants/registry.yml")

PACK_MODULES = {
    "aviation": "pipeline.synth.pack_aviation",
    "healthcare_provider": "pipeline.synth.pack_healthcare_provider",
    "healthcare_payer": "pipeline.synth.pack_healthcare_payer",
}


def load_pack(generator: str, profile: str | None = None):
    if generator in PACK_MODULES:
        mod = importlib.import_module(PACK_MODULES[generator])
        # A pack may expose profiles so that two subtypes in the same industry
        # produce genuinely different corpora rather than interchangeable ones.
        if profile and hasattr(mod, "for_profile"):
            return mod.for_profile(profile)
        return mod.PACK
    from .synth.packs_extra import PACKS
    if generator in PACKS:
        return PACKS[generator]
    raise KeyError(f"no domain pack for generator '{generator}'")


# --------------------------------------------------------------------------- logos
# Generated rather than sourced. A tenant needs a mark that reads at 24px in a
# navbar and does not look like clip art; nine of them need to look like one
# family. Both are easier to guarantee from a common geometry than from stock
# assets, and it keeps the repository free of third-party licensed imagery.
GLYPHS = {
    "tail":   "M16 34 L24 12 L28 12 L26 34 Z M12 34 L20 26 L20 34 Z",
    "wrench": "M28 12a7 7 0 0 0-9 9l-9 9 4 4 9-9a7 7 0 0 0 9-9l-5 5-4-4z",
    "pulse":  "M8 24 h6 l3-8 l5 16 l4-10 l3 2 h7",
    "shield": "M24 10 l12 5 v9c0 7-5 12-12 14c-7-2-12-7-12-14v-9z",
    "flask":  "M20 10 v9 L12 33 a2 2 0 0 0 2 3 h20 a2 2 0 0 0 2-3 L28 19 v-9 z",
    "device": "M14 14 h20 a2 2 0 0 1 2 2 v16 a2 2 0 0 1-2 2 H14 a2 2 0 0 1-2-2 V16 a2 2 0 0 1 2-2 z M18 22 h12 M18 27 h7",
    "vault":  "M12 12 h24 v24 H12 z M24 24 m-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0-12 0 M24 14 v4 M24 30 v4",
    "umbrella": "M24 10 c9 0 15 7 15 13 H9 c0-6 6-13 15-13 z M24 23 v10 a4 4 0 0 1-8 0",
    "anchor": "M24 12 m-3 0 a3 3 0 1 0 6 0 a3 3 0 1 0-6 0 M24 16 v20 M16 24 h16 M12 30 c0 6 6 8 12 8 s12-2 12-8",
    "basket": "M10 20 h28 l-3 15 H13 z M17 20 l4-9 M31 20 l-4-9",
    "check":  "M12 25 l8 8 l16-18",
}


def make_logo(slug: str, name: str, accent: str, accent_2: str, glyph: str) -> str:
    path = GLYPHS.get(glyph, GLYPHS["check"])
    gid = f"g-{slug}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"
     width="48" height="48" role="img" aria-label="{name}">
  <defs>
    <linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent_2}"/>
    </linearGradient>
  </defs>
  <rect width="48" height="48" rx="11" fill="url(#{gid})"/>
  <path d="{path}" fill="none" stroke="#fff" stroke-width="2.4"
        stroke-linecap="round" stroke-linejoin="round" opacity="0.95"/>
</svg>
"""


# --------------------------------------------------------------------------- build
def build_tenant(t: dict, defaults: dict, only: str | None = None) -> dict | None:
    slug = t["slug"]
    if only and slug != only:
        return None

    root = Path("tenants") / slug
    pack = load_pack(t["corpus"]["generator"], t["corpus"].get("profile"))

    # Seed per tenant, not per run. Two tenants sharing a domain pack would
    # otherwise generate the same identifier sequences — Q-Airlines and
    # Q-AeroTech producing the same task card numbers, which is both a leaky
    # abstraction and a bad story ("these are two different organisations"
    # falls apart the moment someone reads the document numbers). Derived from
    # the slug so it stays deterministic.
    seed = t["corpus"].get("seed", defaults["seed"]) + (
        int(hashlib.sha256(slug.encode()).hexdigest()[:8], 16) % 100000)
    n = t["corpus"].get("documents", defaults["corpus_target"])

    docs = CorpusEngine(pack, seed, t["name"]).generate(n)
    stats = write_corpus(docs, root / "docs")

    (root / "brand").mkdir(parents=True, exist_ok=True)
    (root / "brand" / "logo.svg").write_text(
        make_logo(slug, t["name"], t["accent"], t.get("accent_2", t["accent"]),
                  t.get("logo", "check")), encoding="utf-8")

    # Seed questions: the pack's practitioner questions, plus questions built
    # from this tenant's own spine values so at least some are guaranteed
    # answerable from the generated corpus.
    spine_pool = CorpusEngine(pack, seed, t["name"]).build_spine_pool()
    seeded = list(pack.question_seeds)
    primary = list(pack.spine_fields)[0]
    for row in spine_pool[:6]:
        seeded.append(f"What does the documentation say about {row[primary]}?")
    (root / "questions.json").write_text(json.dumps(seeded, indent=1), encoding="utf-8")

    config = {
        "slug": slug,
        "name": t["name"],
        "industry": t["industry"],
        "subtype": t["subtype"],
        "tagline": t["tagline"],
        "persona": t.get("persona", ""),
        "accent": t["accent"],
        "accent_2": t.get("accent_2", t["accent"]),
        "logo": f"tenants/{slug}/brand/logo.svg",
        "highlights": t.get("highlights", []),
        "builder": defaults["builder"],
        "stage": defaults["stage"],
        "corpus": {
            "generator": t["corpus"]["generator"],
            "profile": t["corpus"].get("profile"),
            "documents": stats["documents"],
            "document_types": stats["by_type"],
            "spine_fields": list(pack.spine_fields),
            "spine_values": stats["spine_values"],
            "bytes": stats["bytes"],
            "synthetic": True,
        },
        "domain": {
            "regulations": [r[0] for r in pack.regulations],
            "systems": pack.systems,
            "roles": pack.roles,
        },
    }
    (root / "tenant.json").write_text(json.dumps(config, indent=1), encoding="utf-8")
    return config


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    reg = yaml.safe_load(REGISTRY.read_text())
    defaults = reg["defaults"]

    print("=" * 72)
    print("  TENANT BUILD — synthetic corpora, logos, configuration")
    print("=" * 72)

    built = []
    for t in reg["tenants"]:
        cfg = build_tenant(t, defaults, only)
        if cfg:
            built.append(cfg)
            c = cfg["corpus"]
            print(f"\n  {cfg['name']:18} {cfg['industry']} / {cfg['subtype']}")
            print(f"  {'':18} {c['documents']:>3} docs · {len(c['document_types'])} types · "
                  f"{c['bytes']:,} bytes · spine {c['spine_fields']}")

    if built:
        index = [{k: c[k] for k in ("slug", "name", "industry", "subtype", "tagline",
                                    "accent", "accent_2", "logo", "persona", "highlights")}
                 for c in built]
        Path("site/data").mkdir(parents=True, exist_ok=True)
        Path("site/data/tenants.json").write_text(json.dumps(index, indent=1), encoding="utf-8")

    total_docs = sum(c["corpus"]["documents"] for c in built)
    total_bytes = sum(c["corpus"]["bytes"] for c in built)
    print("\n" + "-" * 72)
    print(f"  {len(built)} tenants · {total_docs} synthetic documents · {total_bytes:,} bytes")
    print(f"  every document fictional · no client data used")
    print("=" * 72)


if __name__ == "__main__":
    main()
