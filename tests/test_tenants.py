"""Tenant factory tests — safety first, then structure."""
import json, re, sys
from collections import Counter
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


@pytest.fixture(scope="session")
def assembled_site():
    """Assemble the site once, then assert against THAT.

    These tests previously read whatever happened to be in site/t/ — which in a
    fresh checkout is stale generated output from an earlier commit, not the
    result of this build. That made the corpora stage fail on files the publish
    stage was about to replace, blocking the whole pipeline over a false alarm.
    Generated output is never a fixture; generate it.
    """
    import subprocess, sys as _s
    if not (ROOT / "tenants" / registry()["tenants"][0]["slug"] / "tenant.json").exists():
        pytest.skip("tenants not built — run build_tenants first")
    r = subprocess.run([_s.executable, "-m", "pipeline.build_site"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        pytest.fail(f"build_site failed:\n{r.stdout}\n{r.stderr}")
    return ROOT / "site"


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
        assert len(list((d / "docs").glob("*.md"))) >= 40, f"{t['slug']}: thin corpus"


def test_logos_are_distinct():
    marks = sorted(ROOT.glob("site/assets/brand/q-*-mark.png"))
    assert len(marks) >= 11, f"only {len(marks)} tenant marks in site/assets/brand"
    assert len({p.read_bytes() for p in marks}) == len(marks), "duplicate tenant marks"


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
    """The headline claim, asserted rather than trusted.

    Measured on domain-distinctive vocabulary, not raw text. Raw overlap cannot
    express this claim: every pair of tenants shares 54-60% of its 5+ letter
    vocabulary, including pairs with nothing in common (airlines vs bank,
    55.8%), because both documents are written in English and share the control
    header, the trailing sections and the person-name pool. 81% of the terms
    provider and payer had in common were shared by all eleven tenants. The old
    form asserted raw overlap < 0.35, which no pair of tenants could ever reach
    — it was unsatisfiable rather than strict.

    Stripping vocabulary common to nearly every tenant leaves the domain signal,
    and that discriminates sharply. Provider vs payer scores 15.6%; rebuild the
    payer corpus from the provider's pack — the precise failure this test exists
    to catch — and it scores 99.6%. The raw measure moved only 60.4% -> 97.6%
    and failed the threshold either way.
    """
    def terms(slug):
        txt = " ".join(p.read_text() for p in (ROOT / f"tenants/{slug}/docs").glob("*.md"))
        return set(re.findall(r"[a-z]{5,}", txt.lower()))

    slugs = [t["slug"] for t in registry()["tenants"]]
    vocab = {s: terms(s) for s in slugs}

    seen = Counter()
    for s in slugs:
        seen.update(vocab[s])
    # Present in nearly every tenant: scaffolding and ordinary English, not domain.
    boilerplate = {w for w, n in seen.items() if n >= len(slugs) - 2}

    a = vocab["q-health"] - boilerplate
    b = vocab["q-assure-claims"] - boilerplate
    assert a and b, "no domain-distinctive vocabulary survived — check the corpora"
    overlap = len(a & b) / len(a | b)
    assert overlap < 0.35, (
        f"provider and payer corpora share {overlap:.1%} of their domain-distinctive "
        f"vocabulary — too similar to demonstrate that subtype is the unit of reuse")


@pytest.mark.parametrize("slug", [t["slug"] for t in yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "tenants/registry.yml").read_text())["tenants"]])
def test_identifiers_thread_across_document_types(slug):
    """Without this, the knowledge graph has nothing genuine to bridge.

    Asserts the domain's DECLARED spine (pack.spine — the tail number, the care
    pathway, the vessel), not whichever identifier happens to score best. That
    distinction matters: before the spine was declared, every kind was sampled
    uniformly and the identifier each tenant advertises threading on was the one
    that threaded least.
    """
    from pipeline import packs as packlib

    spine = packlib.get(slug).spine
    assert spine, f"{slug}: pack declares no spine kind"

    docs = json.loads((ROOT / f"tenants/{slug}/fabric/documents.json").read_text())
    spread = {}
    for doc in docs:
        for inst in doc.get("instances") or []:
            if inst.split(":", 1)[0] == spine:
                spread.setdefault(inst, set()).add(doc["type"])

    assert spread, f"{slug}: spine '{spine}' appears in no document"
    avg = sum(len(s) for s in spread.values()) / len(spread)
    assert avg >= 3.0, (
        f"{slug}: spine '{spine}' spans only {avg:.1f} document types on average — "
        f"cross-document retrieval will have nothing to demonstrate")


def test_build_is_deterministic():
    """A demo shown on Tuesday must be the demo shown on Friday."""
    from pipeline import packs as packlib
    from pipeline.build_tenants import PEAK_MONTH, seed_for
    from pipeline.docgen import DocumentBuilder

    slug = registry()["tenants"][0]["slug"]
    pack, seed, peak = packlib.get(slug), seed_for(slug), PEAK_MONTH.get(slug, 6)
    a = DocumentBuilder(pack, seed, peak_month=peak).build_corpus(20)
    b = DocumentBuilder(pack, seed, peak_month=peak).build_corpus(20)
    assert [d["body"] for d in a] == [d["body"] for d in b], "generation is not deterministic"
    assert [d["filename"] for d in a] == [d["filename"] for d in b], (
        "filenames are not stable — every rebuild will churn the whole corpus")


# =============================================================================
# Site assembly — the failure that shipped a directory page as every tenant
# =============================================================================

def test_the_directory_is_not_copied_into_the_tenant_routes(assembled_site):
    """build_site must never read and write the same file.

    The original version read the per-tenant shell from site/index.html and then
    wrote the tenant directory over that same path. One run destroyed its own
    input, so every later build copied the DIRECTORY into each tenant folder.
    Every tenant URL rendered the tenant list, and clicking through produced
    /t/q-airlines/t/q-retail/ — a 404.

    The shell mechanism is gone: build_site renders every page from a template
    and reads nothing out of site/. So assert the property the shell existed to
    protect, rather than the mechanism that used to protect it — this keeps
    catching the regression however the page is produced.
    """
    landing = (assembled_site / "index.html").read_text()
    assert 'id="domains"' in landing, "landing page is no longer the directory"
    for t in registry()["tenants"]:
        page = (assembled_site / "demo" / t["slug"] / "index.html").read_text()
        assert page != landing, f"{t['slug']}: tenant route is a copy of the directory"
        assert 'id="domains"' not in page, f"{t['slug']}: tenant route is the directory"



@pytest.mark.parametrize("slug", [t["slug"] for t in yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "tenants/registry.yml").read_text())["tenants"]])
def test_each_tenant_page_is_the_application(slug, assembled_site):
    page = assembled_site / "demo" / slug / "index.html"
    assert page.exists(), f"{slug}: build_site produced no page"
    html = page.read_text()
    assert f'data-tenant="{slug}"' in html, f"{slug}: page is not bound to its tenant"
    assert 'id="q"' in html, f"{slug}: page has no ask box — it is not the application"
    assert "assets/js/app.js" in html, f"{slug}: no application code"
    assert 'id="domains"' not in html, f"{slug}: page is the directory"
    assert (assembled_site / "data" / slug / "tenant.json").exists(), f"{slug}: no identity file"


def test_module_versions_are_consistent():
    """Two import specifiers that differ only by query string instantiate the
    module TWICE. State set on one copy — the tenant focus vocabulary, the
    trained intent model — is invisible to the other, silently."""
    import re
    versions = set()
    for p in (ROOT / "site/assets/js").glob("*.js"):
        versions.update(re.findall(r"\.js\?v=(\d+)", p.read_text()))
    assert len(versions) <= 1, (
        f"mixed module versions {sorted(versions)} — modules will be "
        f"instantiated more than once and module-level state will not be shared")


def test_build_site_is_idempotent(assembled_site):
    """Running the build twice must produce the same site, not a broken one."""
    import subprocess, sys as _s
    page = assembled_site / "demo/q-airlines/index.html"
    before = page.read_text()
    subprocess.run([_s.executable, "-m", "pipeline.build_site"], cwd=ROOT,
                   capture_output=True, check=True)
    after = page.read_text()
    assert before == after, "build_site is not idempotent"
    assert 'id="q"' in after, "second run destroyed the tenant page"


# =============================================================================
# Brand assets and hero layout
# =============================================================================

def test_every_tenant_has_brand_assets():
    """A missing mark shows as a broken image on the directory card — the first
    thing a reviewer sees."""
    missing = []
    for t in registry()["tenants"]:
        for kind in ("mark", "lockup"):
            if not (ROOT / "site" / "assets" / "brand" / f"{t['slug']}-{kind}.png").exists():
                missing.append(f"{t['slug']}-{kind}.png")
    assert not missing, f"brand assets missing: {missing}"


def test_brand_assets_are_referenced_from_inside_site():
    """The directory previously pointed at tenants/<slug>/brand/logo.svg, a path
    OUTSIDE site/. It resolved locally and 404'd on every deployment."""
    src = (ROOT / "pipeline" / "build_site.py").read_text()
    assert 'src="tenants/' not in src, (
        "the directory page references a path outside site/ — it will 404 once deployed")
    assert 'brand/{t[' in src or "brand/" in src, "no brand asset reference at all"


def test_brand_assets_are_not_oversized():
    """Eleven marks load on the directory page at once."""
    for p in (ROOT / "site" / "assets" / "brand").glob("*-mark.png"):
        kb = p.stat().st_size / 1024
        assert kb < 90, f"{p.name} is {kb:.0f} KB — too heavy for a card thumbnail"




