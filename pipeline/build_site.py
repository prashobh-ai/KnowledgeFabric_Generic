"""Site assembly — tenant directory page and per-tenant app shells.

Each tenant gets its own copy of the application at site/t/<slug>/, pointed at
its own data. They share code but never share state: q-airlines and q-cruise are
separate builds and separate URLs, so a demo of one cannot leak the other.

Brand assets travel with the build. The directory page and every tenant shell
reference logos INSIDE site/ — the previous build linked the directory cards to
tenants/<slug>/brand/logo.svg, a path that does not exist under the served
root, so every card shipped with a broken image. Assets are copied in, never
linked out.
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(".")

# Preference order for the square mark shown on cards and navbars. mark.png is
# the processed real logo (pipeline/build_brand_assets.py); logo.svg is the
# generated geometric fallback so a tenant without artwork still ships whole.
MARK_CANDIDATES = ("mark.png", "logo.svg")


def _tenant_mark(slug: str) -> Path | None:
    for name in MARK_CANDIDATES:
        p = ROOT / "tenants" / slug / "brand" / name
        if p.exists():
            return p
    return None


def _question_count(slug: str) -> int:
    p = ROOT / "tenants" / slug / "questions.json"
    if not p.exists():
        return 0
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0
    if isinstance(data, dict):
        data = data.get("questions", [])
    return len(data) if isinstance(data, list) else 0


def main():
    reg = yaml.safe_load((ROOT / "tenants/registry.yml").read_text())
    tenants = []
    for t in reg["tenants"]:
        cfg_path = ROOT / "tenants" / t["slug"] / "tenant.json"
        if not cfg_path.exists():
            continue
        cfg = json.loads(cfg_path.read_text())
        cfg["question_count"] = _question_count(t["slug"])
        tenants.append(cfg)

        # App shell per tenant: shared code, tenant-scoped data.
        dest = ROOT / "site" / "t" / t["slug"]
        dest.mkdir(parents=True, exist_ok=True)
        for sub in ("js", "styles"):
            src = ROOT / "site" / sub
            if src.exists():
                shutil.copytree(src, dest / sub, dirs_exist_ok=True)
        # The shell is site/app.html, NOT site/index.html.
        #
        # This was a genuine bug: the previous version read the shell from
        # site/index.html and then wrote the directory page over the same file.
        # One run destroyed its own input, so every subsequent build copied the
        # DIRECTORY into each tenant folder. Every tenant URL rendered the
        # tenant list, and clicking through produced /t/q-airlines/t/q-retail/.
        # Input and output must never be the same path.
        shell = ROOT / "site" / "app.html"
        if not shell.exists():
            raise SystemExit(
                "site/app.html is missing — that file is the per-tenant "
                "application shell and the build cannot produce tenant pages "
                "without it.")
        (dest / "index.html").write_text(shell.read_text(encoding="utf-8"),
                                         encoding="utf-8")

        # Brand assets beside the app. logo.svg also stays at the tenant root
        # for anything that still points there.
        brand_src = ROOT / "tenants" / t["slug"] / "brand"
        brand_dest = dest / "brand"
        brand_dest.mkdir(parents=True, exist_ok=True)
        for name in ("mark.png", "lockup.png", "logo.svg"):
            f = brand_src / name
            if f.exists():
                shutil.copyfile(f, brand_dest / name)
        legacy_logo = brand_src / "logo.svg"
        if legacy_logo.exists():
            (dest / "logo.svg").write_text(
                legacy_logo.read_text(encoding="utf-8"), encoding="utf-8")

        # tenant.json beside the app so the shell can brand itself at runtime
        # instead of being rebuilt per tenant.
        (dest / "data").mkdir(parents=True, exist_ok=True)
        (dest / "data" / "tenant.json").write_text(json.dumps(cfg, indent=1),
                                                   encoding="utf-8")

    if not tenants:
        raise SystemExit("no tenants resolved — run build_tenants first")

    vendored = ROOT / "site" / "vendor" / "vis-network.min.js"
    if not vendored.exists():
        raise SystemExit(
            "site/vendor/vis-network.min.js is missing — the tenant shells "
            "load the graph library from there (deliberately not a CDN, so a "
            "demo works on locked-down or offline networks).")

    # Directory-page marks, served from inside site/.
    site_brand = ROOT / "site" / "brand"
    site_brand.mkdir(parents=True, exist_ok=True)
    for c in tenants:
        mark = _tenant_mark(c["slug"])
        if mark:
            shutil.copyfile(mark, site_brand / f"{c['slug']}{mark.suffix}")
            c["mark_href"] = f"brand/{c['slug']}{mark.suffix}"
        else:
            c["mark_href"] = ""

    (ROOT / "site" / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "site" / "data" / "tenants.json").write_text(
        json.dumps([{k: c[k] for k in ("slug", "name", "industry", "subtype", "tagline",
                                       "accent", "accent_2", "persona", "highlights")}
                    for c in tenants], indent=1))
    _write_directory(tenants)
    print(f"[OK] site/ assembled — {len(tenants)} tenants")


# --------------------------------------------------------------------------
# Directory page.
#
# The page has one job: let a presenter pick the tenant that matches the
# prospect in the room, quickly, and look credible while doing it. Structure
# carries the pitch — tenants are grouped by INDUSTRY so the two aviation and
# two healthcare builds sit side by side, which is the repository's whole
# argument (the subtype, not the industry, is the unit of reuse) made visible.
# All counts are computed from the build, never typed in.
# --------------------------------------------------------------------------

def _write_directory(tenants: list[dict]):
    e = html.escape

    groups: dict[str, list[dict]] = {}
    for t in tenants:
        groups.setdefault(t["industry"], []).append(t)

    n_docs = sum(t.get("corpus", {}).get("documents", 0) for t in tenants)
    n_q = sum(t.get("question_count", 0) for t in tenants)

    def card(t: dict, show_industry: bool = False) -> str:
        docs = t.get("corpus", {}).get("documents", 0)
        qs = t.get("question_count", 0)
        eyebrow = (f'<span class="tind">{e(t["industry"])}</span>'
                   if show_industry else "")
        mark = (f'<img src="{e(t["mark_href"])}" alt="" width="46" height="46" '
                f'decoding="async"/>' if t.get("mark_href")
                else f'<span class="tmark-fallback">{e(t["name"][2:3] or "Q")}</span>')
        return f"""
      <a class="tcard" href="t/{e(t['slug'])}/"
         style="--a:{e(t['accent'])};--b:{e(t.get('accent_2', t['accent']))}">
        <span class="tmark">{mark}</span>
        <div class="tid">
          {eyebrow}<h3 class="tname">{e(t['name'])}</h3>
          <p class="tsub">{e(t['subtype'])}</p>
        </div>
        <p class="ttag">{e(t['tagline'])}</p>
        <div class="tfoot">
          <span class="tdata">{docs} documents&ensp;&middot;&ensp;{qs} questions</span>
          <span class="tgo">Open demo <span class="tgo-arrow">&rarr;</span></span>
        </div>
      </a>"""

    paired = {i: ts for i, ts in groups.items() if len(ts) > 1}
    singles = [t for i, ts in groups.items() if len(ts) == 1 for t in ts]

    def section(ind: str, ts: list[dict]) -> str:
        return f"""
    <section class="igroup" aria-label="{e(ind)}">
      <header class="igroup-head">
        <h2 class="igroup-name">{e(ind)}</h2>
        <span class="igroup-count">{len(ts)} subtypes &middot; separate builds</span>
        <span class="igroup-rule" aria-hidden="true"></span>
      </header>
      <div class="igroup-grid">{''.join(card(t) for t in ts)}
      </div>
    </section>"""

    sections = "\n".join(section(i, ts) for i, ts in paired.items())
    if singles:
        label = "More industries" if paired else "Industries"
        sections += f"""
    <section class="igroup" aria-label="{label}">
      <header class="igroup-head">
        <h2 class="igroup-name">{label}</h2>
        <span class="igroup-count">{len(singles)} tenants &middot; one subtype each</span>
        <span class="igroup-rule" aria-hidden="true"></span>
      </header>
      <div class="igroup-grid">{''.join(card(t, show_industry=True) for t in singles)}
      </div>
    </section>"""

    (ROOT / "site" / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Knowledge Fabric — Demonstration Tenants</title>
<meta name="description" content="Eleven fully synthetic demonstration tenants for Knowledge Fabric, prepared by the QualiZeal AI Center of Excellence."/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23142E66'/%3E%3Ctext x='16' y='22.5' font-family='Georgia,serif' font-size='18' font-weight='700' text-anchor='middle' fill='white'%3EQ%3C/text%3E%3Ccircle cx='24.5' cy='8' r='2.6' fill='%23D6273B'/%3E%3C/svg%3E"/>
<style>
:root {{
  color-scheme: dark;
  --bg: #070D26;
  --bg-2: #0B1338;
  --ink: #F2F5FD;
  --ink-2: #A5B1D2;
  --ink-3: #7C89AF;
  --mono: #8FA0CE;
  --hairline: rgba(151, 170, 255, 0.14);
  --hairline-2: rgba(151, 170, 255, 0.30);
  --chip: #FAFBFD;
  --ease: cubic-bezier(0.22, 1, 0.36, 1);
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font: 16px/1.6 Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
/* Quiet atmosphere: a dot grid and two soft glows — the same weather as the
   tenant app, at a fraction of its intensity. */
.atmo {{ position: fixed; inset: 0; pointer-events: none; z-index: 0; }}
.atmo::before {{
  content: ""; position: absolute; inset: 0;
  background-image: radial-gradient(rgba(160, 178, 255, 0.10) 1px, transparent 1px);
  background-size: 26px 26px;
  mask-image: radial-gradient(ellipse 90% 65% at 50% 0%, #000 30%, transparent 78%);
}}
.atmo::after {{
  content: ""; position: absolute; inset: 0;
  background:
    radial-gradient(560px 340px at 12% -6%, rgba(64, 112, 255, 0.16), transparent 68%),
    radial-gradient(640px 380px at 88% -10%, rgba(200, 64, 96, 0.10), transparent 70%),
    linear-gradient(180deg, var(--bg-2) 0%, var(--bg) 42%);
  z-index: -1;
}}
.wrap {{ position: relative; z-index: 1; max-width: 1180px; margin: 0 auto;
        padding: 0 clamp(1.1rem, 4.5vw, 3.2rem); }}

/* ---------------- masthead ---------------- */
header.masthead {{ padding: clamp(2.6rem, 7vw, 5.2rem) 0 clamp(1.4rem, 3vw, 2rem); }}
.eyebrow {{
  font: 500 0.66rem/1 "JetBrains Mono", monospace; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--mono); margin: 0 0 1.1rem;
}}
.eyebrow b {{ color: var(--ink-2); font-weight: 500; }}
h1 {{
  margin: 0; font-size: clamp(2.3rem, 1.4rem + 3.6vw, 4rem); font-weight: 800;
  letter-spacing: -0.03em; line-height: 1.02;
}}
.serifline {{
  display: block; margin-top: 0.35rem;
  font: italic 400 clamp(1.25rem, 0.9rem + 1.6vw, 1.9rem)/1.25 "Instrument Serif", Georgia, serif;
  color: var(--ink-2); letter-spacing: 0.002em;
}}
.lede {{ max-width: 62ch; margin: 1.25rem 0 0; color: var(--ink-2);
        font-size: 1.02rem; line-height: 1.7; }}
.synthetic-note {{
  display: inline-flex; align-items: baseline; gap: 0.55rem;
  margin: 1.35rem 0 0; padding: 0.55rem 0.85rem;
  border: 1px solid var(--hairline); border-radius: 10px;
  color: var(--ink-3); font-size: 0.8rem; line-height: 1.5; max-width: 66ch;
  background: rgba(255, 255, 255, 0.025);
}}
.synthetic-note::before {{
  content: ""; width: 7px; height: 7px; border-radius: 50%; flex: none;
  background: #47D6A6; box-shadow: 0 0 0 3px rgba(71, 214, 166, 0.16);
  transform: translateY(-1px);
}}

/* ---------------- computed stats strip ---------------- */
.stats {{
  display: flex; flex-wrap: wrap; gap: 0.4rem 2.2rem;
  margin: clamp(1.6rem, 3.5vw, 2.4rem) 0 0; padding: 0.95rem 0 0;
  border-top: 1px solid var(--hairline);
  font: 500 0.72rem/1.5 "JetBrains Mono", monospace; letter-spacing: 0.06em;
  color: var(--mono);
}}
.stats b {{ color: var(--ink); font-weight: 500; }}

/* ---------------- industry groups ---------------- */
main {{ padding: clamp(1.2rem, 3vw, 2rem) 0 4.5rem; }}
.igroup {{ margin-top: clamp(1.9rem, 4vw, 2.8rem); }}
.igroup-head {{ display: flex; align-items: baseline; gap: 0.8rem; margin: 0 0 0.95rem; }}
.igroup-name {{
  margin: 0; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--ink-2); white-space: nowrap;
}}
.igroup-count {{
  font: 500 0.66rem/1 "JetBrains Mono", monospace; letter-spacing: 0.08em;
  color: var(--ink-3); white-space: nowrap; transform: translateY(-1px);
}}
.igroup-rule {{ flex: 1; height: 1px; background: linear-gradient(90deg, var(--hairline), transparent); }}
.igroup-grid {{
  display: grid; gap: 0.95rem;
  grid-template-columns: repeat(auto-fill, minmax(min(310px, 100%), 1fr));
}}

/* ---------------- tenant card ---------------- */
.tcard {{
  position: relative; display: grid;
  grid-template-columns: auto 1fr; grid-template-rows: auto auto 1fr;
  gap: 0.35rem 0.95rem; align-items: center;
  padding: 1.15rem 1.25rem 1.05rem 1.45rem;
  border-radius: 16px; text-decoration: none; color: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.022));
  border: 1px solid var(--hairline);
  transition: transform 0.28s var(--ease), border-color 0.28s var(--ease),
              box-shadow 0.28s var(--ease);
}}
/* Accent rail — the tenant's own palette, standing at the left edge. */
.tcard::before {{
  content: ""; position: absolute; left: -1px; top: 14px; bottom: 14px; width: 3px;
  border-radius: 3px; background: linear-gradient(180deg, var(--a), var(--b));
  opacity: 0.85; transition: top 0.28s var(--ease), bottom 0.28s var(--ease);
}}
.tcard:hover, .tcard:focus-visible {{
  transform: translateY(-3px);
  border-color: color-mix(in srgb, var(--a) 55%, var(--hairline-2));
  box-shadow: 0 14px 34px -18px color-mix(in srgb, var(--a) 55%, transparent),
              0 3px 12px rgba(3, 7, 24, 0.5);
}}
.tcard:hover::before, .tcard:focus-visible::before {{ top: 9px; bottom: 9px; }}
.tcard:focus-visible {{ outline: 2px solid var(--a); outline-offset: 3px; }}

/* The real logo, on the light chip it was drawn for. */
.tmark {{
  grid-row: 1; display: grid; place-items: center;
  width: 62px; height: 62px; border-radius: 15px; background: var(--chip);
  box-shadow: inset 0 0 0 1px rgba(15, 29, 74, 0.10),
              0 4px 14px -6px rgba(3, 7, 24, 0.55);
}}
.tmark img {{ display: block; width: 46px; height: 46px; object-fit: contain; }}
.tmark-fallback {{
  font: 700 1.5rem/1 Georgia, serif; color: #142E66;
}}
.tid {{ grid-row: 1; min-width: 0; }}
.tind {{ display: block; font: 500 0.58rem/1 "JetBrains Mono", monospace;
        letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-3);
        margin: 0 0 0.3rem; }}
.tname {{ margin: 0; font-size: 1.14rem; font-weight: 700; letter-spacing: -0.014em; }}
.tsub {{ margin: 0.14rem 0 0; font-size: 0.79rem; color: var(--ink-2); line-height: 1.4; }}
.ttag {{ grid-column: 1 / -1; margin: 0.35rem 0 0.15rem; font-size: 0.86rem;
        color: #C6CEE8; line-height: 1.55; }}
.tfoot {{
  grid-column: 1 / -1; align-self: end;
  display: flex; align-items: baseline; justify-content: space-between; gap: 1rem;
  padding-top: 0.6rem; border-top: 1px solid var(--hairline);
}}
.tdata {{ font: 400 0.66rem/1 "JetBrains Mono", monospace; letter-spacing: 0.04em;
         color: var(--ink-3); white-space: nowrap; }}
.tgo {{ font-size: 0.76rem; font-weight: 600; color: var(--a); white-space: nowrap; }}
.tgo-arrow {{ display: inline-block; transition: transform 0.28s var(--ease); }}
.tcard:hover .tgo-arrow, .tcard:focus-visible .tgo-arrow {{ transform: translateX(3px); }}

/* ---------------- footer ---------------- */
footer {{ padding: 0 0 3.2rem; color: var(--ink-3); font-size: 0.78rem;
         border-top: 1px solid var(--hairline); padding-top: 1.4rem; }}

@media (max-width: 560px) {{
  .tcard {{ padding: 1rem 1rem 0.95rem 1.2rem; }}
  .tmark {{ width: 52px; height: 52px; border-radius: 13px; }}
  .tmark img {{ width: 38px; height: 38px; }}
  .stats {{ gap: 0.3rem 1.4rem; }}
}}
@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
  .tcard, .tcard::before, .tgo-arrow {{ transition: none; }}
}}
</style></head><body>
<div class="atmo" aria-hidden="true"></div>
<div class="wrap">
<header class="masthead">
  <p class="eyebrow"><b>QualiZeal</b> &middot; AI Center of Excellence &middot; Demonstration platform</p>
  <h1>Knowledge Fabric
    <span class="serifline">Every answer, traced to its source.</span>
  </h1>
  <p class="lede">{len(tenants)} demonstration tenants across {len(groups)} industries —
  each with its own corpus, brand, domain vocabulary, knowledge graph and question
  set. Pick the tenant that matches the room.</p>
  <p class="synthetic-note">Every tenant is fictional and every document synthetic.
  No client name, document or dataset appears anywhere in this build.</p>
  <div class="stats">
    <span><b>{len(tenants)}</b> tenants</span>
    <span><b>{len(groups)}</b> industries</span>
    <span><b>{n_docs}</b> synthetic documents</span>
    <span><b>{n_q}</b> seeded questions</span>
  </div>
</header>
<main>{sections}
</main>
<footer>A QualiZeal AI Center of Excellence demonstration. Prepared for evaluation purposes.</footer>
</div>
</body></html>
""", encoding="utf-8")


if __name__ == "__main__":
    main()
