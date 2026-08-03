"""Tenant factory tests — safety first, then structure."""
import json, re, sys
from pathlib import Path
import pytest, yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
ROOT = Path(__file__).resolve().parents[1]

# Names that must never appear in a published synthetic corpus. The list is
# deliberately broader than our own client list: a demo repository is public,
# and an accidental real-world name is a confidentiality incident whether or not
# the company is a customer.
FORBIDDEN = [
    "southwest", "nova biomedical", "statstrip", "statsensor", "pwc",
    "royal caribbean", "carnival corp", "msc cruises", "norwegian cruise",
    "epic systems", "cerner", "meditech ", "united airlines", "delta air",
    "american airlines", "lufthansa", "aetna", "cigna", "unitedhealth", "anthem",
    "pfizer", "astrazeneca", "medtronic", "guidewire", "temenos",
]


def registry():
    return yaml.safe_load((ROOT / "tenants/registry.yml").read_text())


def corpora():
    return sorted(ROOT.glob("tenants/*/docs/*.md"))


def test_corpus_exists():
    docs = corpora()
    assert len(docs) > 400, f"only {len(docs)} documents — run build_tenants"


def test_no_real_world_names_anywhere():
    """The single most important test in the repository."""
    offences = []
    for p in corpora():
        low = p.read_text().lower()
        for name in FORBIDDEN:
            if name in low:
                offences.append(f"{p.relative_to(ROOT)}: '{name}'")
    assert not offences, "real-world names in synthetic corpus:\n  " + "\n  ".join(offences[:10])


def test_every_document_declares_itself_synthetic():
    missing = [str(p.relative_to(ROOT)) for p in corpora()
               if "SYNTHETIC DOCUMENT" not in p.read_text()]
    assert not missing, f"{len(missing)} documents lack the synthetic banner: {missing[:5]}"


def test_every_tenant_resolves():
    for t in registry()["tenants"]:
        d = ROOT / "tenants" / t["slug"]
        assert (d / "tenant.json").exists(), f"{t['slug']}: no tenant.json"
        assert (d / "brand/logo.svg").exists(), f"{t['slug']}: no logo"
        assert (d / "questions.json").exists(), f"{t['slug']}: no questions"
        assert len(list((d / "docs").glob("*.md"))) >= 40, f"{t['slug']}: thin corpus"


def test_logos_are_distinct():
    logos = list(ROOT.glob("tenants/*/brand/logo.svg"))
    assert len({p.read_text() for p in logos}) == len(logos), "duplicate tenant logos"


def test_subtypes_are_configured_separately():
    """Two tenants sharing an industry must not share a generator. Reusing one
    subtype's configuration for another is the exact failure this repo exists
    to prevent."""
    by_industry = {}
    for t in registry()["tenants"]:
        by_industry.setdefault(t["industry"], []).append(t)
    for industry, ts in by_industry.items():
        if len(ts) < 2:
            continue
        subtypes = {t["subtype"] for t in ts}
        assert len(subtypes) == len(ts), f"{industry}: duplicate subtypes"
        gens = {(t["corpus"]["generator"], t["corpus"].get("profile")) for t in ts}
        assert len(gens) == len(ts), (
            f"{industry}: subtypes share a generator {gens} — they will produce "
            f"interchangeable corpora and the divergence demo collapses")


def test_healthcare_subtypes_genuinely_diverge():
    """The headline claim, asserted rather than trusted."""
    def terms(slug):
        txt = " ".join(p.read_text() for p in (ROOT / f"tenants/{slug}/docs").glob("*.md"))
        return set(re.findall(r"[a-z]{5,}", txt.lower()))
    a, b = terms("q-health"), terms("q-assure-claims")
    overlap = len(a & b) / len(a | b)
    assert overlap < 0.35, (
        f"provider and payer corpora share {overlap:.1%} of vocabulary — too "
        f"similar to demonstrate that subtype is the unit of reuse")


@pytest.mark.parametrize("slug", [t["slug"] for t in yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "tenants/registry.yml").read_text())["tenants"]])
def test_identifiers_thread_across_document_types(slug):
    """Without this, the knowledge graph has nothing genuine to bridge."""
    cfg = json.loads((ROOT / f"tenants/{slug}/tenant.json").read_text())
    from pipeline.build_tenants import load_pack
    from pipeline.synth.engine import CorpusEngine

    reg = registry()
    t = next(x for x in reg["tenants"] if x["slug"] == slug)
    pack = load_pack(t["corpus"]["generator"])
    seed = t["corpus"].get("seed", reg["defaults"]["seed"])
    pool = CorpusEngine(pack, seed, t["name"]).build_spine_pool()
    primary = list(pack.spine_fields)[0]
    values = {str(r[primary]) for r in pool}

    spread = {}
    for p in (ROOT / f"tenants/{slug}/docs").glob("*.md"):
        txt = p.read_text()
        m = re.search(r"\*\*Document type:\*\* (.+?)  ", txt)
        if not m:
            continue
        for v in values:
            if v in txt:
                spread.setdefault(v, set()).add(m.group(1))

    assert spread, f"{slug}: no spine value appears in any document"
    avg = sum(len(s) for s in spread.values()) / len(spread)
    assert avg >= 3.0, (
        f"{slug}: spine '{primary}' spans only {avg:.1f} document types on average — "
        f"cross-document retrieval will have nothing to demonstrate")


def test_build_is_deterministic():
    """A demo shown on Tuesday must be the demo shown on Friday."""
    from pipeline.build_tenants import load_pack
    from pipeline.synth.engine import CorpusEngine
    reg = registry()
    t = reg["tenants"][0]
    pack = load_pack(t["corpus"]["generator"])
    seed = reg["defaults"]["seed"]
    a = CorpusEngine(pack, seed, t["name"]).generate(20)
    b = CorpusEngine(pack, seed, t["name"]).generate(20)
    assert [d.body for d in a] == [d.body for d in b], "generation is not deterministic"


# =============================================================================
# Site assembly — the failure that shipped a directory page as every tenant
# =============================================================================

def test_app_shell_is_separate_from_the_directory_page():
    """build_site must never read and write the same file.

    The original version read the per-tenant shell from site/index.html and then
    wrote the tenant directory over that same path. One run destroyed its own
    input, so every later build copied the DIRECTORY into each tenant folder.
    Every tenant URL rendered the tenant list, and clicking through produced
    /t/q-airlines/t/q-retail/ — a 404.
    """
    shell = ROOT / "site" / "app.html"
    assert shell.exists(), "site/app.html missing — no per-tenant shell to copy"
    src = (ROOT / "pipeline" / "build_site.py").read_text()
    assert 'ROOT / "site" / "app.html"' in src, "build_site no longer reads app.html"
    body = src[src.index("def main"):]
    assert 'shell = ROOT / "site" / "index.html"' not in body, (
        "build_site reads the shell from its own output path again")


def test_app_shell_is_the_application_not_the_directory():
    shell = (ROOT / "site" / "app.html").read_text()
    for element in ["composer-input", "answer-stage-text", "galaxy"]:
        assert element in shell, f"app shell missing '{element}'"
    assert "Demonstration Tenants" not in shell, "app shell is the directory page"


@pytest.mark.parametrize("slug", [t["slug"] for t in yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "tenants/registry.yml").read_text())["tenants"]])
def test_each_tenant_page_is_the_application(slug):
    page = ROOT / f"site/t/{slug}/index.html"
    if not page.exists():
        pytest.skip("site not assembled")
    html = page.read_text()
    assert "composer-input" in html, f"{slug}: page is not the application"
    assert "Demonstration Tenants" not in html, f"{slug}: page is the directory"
    assert (ROOT / f"site/t/{slug}/data/tenant.json").exists(), f"{slug}: no identity file"
    assert (ROOT / f"site/t/{slug}/js/main.js").exists(), f"{slug}: no application code"


def test_module_versions_are_consistent():
    """Two import specifiers that differ only by query string instantiate the
    module TWICE. State set on one copy — the tenant focus vocabulary, the
    trained intent model — is invisible to the other, silently."""
    import re
    versions = set()
    for p in (ROOT / "site/js").glob("*.js"):
        versions.update(re.findall(r"\.js\?v=(\d+)", p.read_text()))
    assert len(versions) <= 1, (
        f"mixed module versions {sorted(versions)} — modules will be "
        f"instantiated more than once and module-level state will not be shared")


def test_build_site_is_idempotent():
    """Running the build twice must produce the same site, not a broken one."""
    import subprocess, sys as _s
    before = (ROOT / "site/t/q-airlines/index.html").read_text() \
        if (ROOT / "site/t/q-airlines/index.html").exists() else None
    if before is None:
        pytest.skip("site not assembled")
    subprocess.run([_s.executable, "-m", "pipeline.build_site"], cwd=ROOT,
                   capture_output=True, check=True)
    after = (ROOT / "site/t/q-airlines/index.html").read_text()
    assert before == after, "build_site is not idempotent"
    assert "composer-input" in after, "second run destroyed the tenant page"
