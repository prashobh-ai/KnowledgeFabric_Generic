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
        shell = ROOT / "site" / "index.html"
        if shell.exists():
            dest_html = dest / "index.html"
            dest_html.write_text(shell.read_text(encoding="utf-8"), encoding="utf-8")
        logo = ROOT / "tenants" / t["slug"] / "brand" / "logo.svg"
        if logo.exists():
            (dest / "logo.svg").write_text(logo.read_text(encoding="utf-8"), encoding="utf-8")

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
        <img class="tlogo" src="tenants/{t['slug']}/brand/logo.svg" alt="" width="44" height="44"/>
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
.tlogo {{ border-radius:10px; }}
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
