"""Site assembly — tenant directory page and per-tenant app shells.

Each tenant gets its own copy of the application at site/t/<slug>/, pointed at
its own data. They share code but never share state: q-airlines and q-cruise are
separate builds and separate URLs, so a demo of one cannot leak the other.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(".")


def main():
    reg = yaml.safe_load((ROOT / "tenants/registry.yml").read_text())
    tenants = []
    for t in reg["tenants"]:
        cfg_path = ROOT / "tenants" / t["slug"] / "tenant.json"
        if not cfg_path.exists():
            continue
        cfg = json.loads(cfg_path.read_text())
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
        # Brand assets. The directory page previously pointed at
        # tenants/<slug>/brand/logo.svg — a path OUTSIDE site/, so every card
        # image 404'd once deployed. Assets that the site references must live
        # under site/.
        for kind in ("mark", "lockup"):
            src = ROOT / "site" / "brand" / f"{t['slug']}-{kind}.png"
            if src.exists():
                shutil.copy(src, dest / f"{kind}.png")
        generated = ROOT / "tenants" / t["slug"] / "brand" / "logo.svg"
        if generated.exists():
            (dest / "logo.svg").write_text(generated.read_text(encoding="utf-8"),
                                           encoding="utf-8")

        # tenant.json beside the app so the shell can brand itself at runtime
        # instead of being rebuilt per tenant.
        (dest / "data").mkdir(parents=True, exist_ok=True)
        (dest / "data" / "tenant.json").write_text(json.dumps(cfg, indent=1),
                                                   encoding="utf-8")

    if not tenants:
        raise SystemExit("no tenants resolved — run build_tenants first")

    (ROOT / "site" / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "site" / "data" / "tenants.json").write_text(
        json.dumps([{k: c[k] for k in ("slug", "name", "industry", "subtype", "tagline",
                                       "accent", "accent_2", "persona", "highlights")}
                    for c in tenants], indent=1))
    _write_directory(tenants)
    print(f"[OK] site/ assembled — {len(tenants)} tenants")


def _write_directory(tenants: list[dict]):
    cards = "\n".join(f"""
      <a class="tcard" href="t/{t['slug']}/" style="--a:{t['accent']};--b:{t.get('accent_2', t['accent'])}">
        <img class="tlogo" src="brand/{t['slug']}-mark.png" alt="" width="52" height="52" loading="lazy"/>
        <span class="tind">{t['industry']}</span>
        <h2>{t['name']}</h2>
        <p class="tsub">{t['subtype']}</p>
        <p class="ttag">{t['tagline']}</p>
        <span class="tgo">Open demonstration &rarr;</span>
      </a>""" for t in tenants)

    (ROOT / "site" / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Knowledge Fabric — Demonstration Tenants</title>
<style>
:root {{ color-scheme: dark; --ink:#F2F5FD; --ink2:#A2AECD; --bg:#0B1338; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
header {{ padding:clamp(2rem,6vw,4.5rem) clamp(1rem,5vw,4rem) 1.5rem; max-width:1200px; margin:0 auto; }}
h1 {{ font-size:clamp(1.9rem,1.2rem+3vw,3.2rem); margin:0 0 .5rem; letter-spacing:-.02em; }}
.lede {{ color:var(--ink2); max-width:60ch; margin:0 0 .5rem; }}
.note {{ color:#7B87A8; font-size:.82rem; max-width:64ch; }}
main {{ display:grid; gap:1rem; padding:1rem clamp(1rem,5vw,4rem) 4rem; max-width:1200px; margin:0 auto;
  grid-template-columns:repeat(auto-fill,minmax(270px,1fr)); }}
.tcard {{ display:flex; flex-direction:column; gap:.4rem; padding:1.3rem; border-radius:16px;
  text-decoration:none; color:inherit; background:rgba(255,255,255,.04);
  border:1px solid rgba(150,170,255,.18); transition:transform .22s cubic-bezier(.22,1,.36,1),border-color .22s; }}
.tcard:hover {{ transform:translateY(-3px); border-color:rgba(150,170,255,.45); }}
.tcard::before {{ content:""; height:3px; border-radius:3px; margin:-.4rem 0 .6rem;
  background:linear-gradient(90deg,var(--a),var(--b)); }}
.tlogo {{ border-radius:10px; background:#fff; padding:3px; }}
.tind {{ font-size:.62rem; letter-spacing:.12em; text-transform:uppercase; color:var(--ink2); }}
h2 {{ margin:.1rem 0 0; font-size:1.15rem; letter-spacing:-.01em; }}
.tsub {{ margin:0; font-size:.82rem; color:var(--ink2); }}
.ttag {{ margin:.3rem 0 .6rem; font-size:.85rem; color:#C3CBE6; }}
.tgo {{ margin-top:auto; font-size:.78rem; font-weight:600; color:var(--a); }}
footer {{ padding:0 clamp(1rem,5vw,4rem) 3rem; max-width:1200px; margin:0 auto;
  color:#7B87A8; font-size:.78rem; }}
</style></head><body>
<header>
  <h1>Knowledge Fabric</h1>
  <p class="lede">Every answer, traced to its source. Eleven demonstration tenants
  across nine industry subtypes — each with its own corpus, vocabulary, knowledge
  graph and question set.</p>
  <p class="note">Every tenant is fictional and every document synthetic. No client
  name, document or dataset appears anywhere in this build.</p>
</header>
<main>{cards}
</main>
<footer>A QualiZeal AI Center of Excellence demonstration. Prepared for evaluation purposes.</footer>
</body></html>
""", encoding="utf-8")


if __name__ == "__main__":
    main()
