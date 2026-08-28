"""Assemble the static site.

    python -m pipeline.build_site

Routes produced:

    site/demos/index.html          the demonstrations directory, all eleven tenants
    site/kit/index.html            the presenter kit — how to run the meeting
    site/demo/<slug>/index.html    one tenant demonstration
    site/data/<slug>/*.json        that tenant's fabric artefacts
    site/data/<slug>/docs/*.md     the corpus, fetched by the document viewer

Hand-written and never touched by this script:

    site/index.html                the walkthrough — the hand-written landing page
    site/assets/                   stylesheet, brand marks, vendored JS, logos
    site/deck/                     the twelve-slide deck, rendered in-browser
    site/downloads/                the .pptx, the .docx and the diagrams

The route segment is `demo`, not `t` — a URL is part of the interface, and
`/demo/q-airlines/` tells a reader what they are about to open while `/t/…`
tells them nothing.

Everything under site/ except assets/ is generated. Do not hand-edit.
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
TENANTS = ROOT / "tenants"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Sora:wght@400;600;700;800&'
    'family=Manrope:wght@400;500;600;700;800&'
    'family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'
)

# The QualiZeal mark, rebuilt as inline SVG: the blue ring with the red
# ascending stroke through it. Inline so it renders before any network round
# trip and inherits currentColor in the dark theme.
# The authentic QualiZeal mark, extracted from ppt/media in the delivery deck
# rather than approximated in SVG. The hand-drawn version had the wrong ring
# geometry and both brand colours wrong.
def logo(base: str = "", size: int = 30) -> str:
    return (f'<img src="{base}assets/brand/qualizeal-icon.png" alt="QualiZeal" '
            f'height="{size}" width="{size}" decoding="async">')


FIELD = ('<div class="field"><span class="drift a"></span>'
         '<span class="drift b"></span><span class="drift c"></span></div>')


def head(title: str, desc: str, base: str, accent: str = "#0B66E1") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="{base}assets/brand/favicon.png" type="image/png">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
{FONTS}
<link rel="stylesheet" href="{base}assets/css/fabric.css">
<style>:root{{--accent:{accent}}}</style>
</head>
<body>
{FIELD}
"""


def topbar(base: str, links: list[tuple[str, str]], active: str = "") -> str:
    nav = "".join(
        f'<a href="{h}"{" class=\'on\'" if t == active else ""}>{html.escape(t)}</a>'
        for t, h in links
    )
    return f"""
<header class="topbar">
  <div class="wrap topbar-in">
    <a class="brand" href="{base}index.html">
      {logo(base, 32)}
      <span class="brand-text">
        <span class="brand-wordmark">QUALI<em>ZEAL</em></span>
        <span class="sub">Knowledge Fabric · AI Center of Excellence</span>
      </span>
    </a>
    <nav class="navlinks">{nav}</nav>
  </div>
</header>
"""


FOOTER_TPL = """
<footer>
  <div class="wrap">
    <div class="row between" style="align-items:flex-start;gap:2rem">
      <div>
        <div class="row" style="gap:.6rem;margin-bottom:.6rem">%LOGO%
          <strong class="brand-wordmark" style="font-size:1rem">QUALI<em>ZEAL</em></strong></div>
        <p class="note">Every tenant, document, person and identifier in this
        demonstration is fictional. Standards, code systems and regulations are
        cited as public reference. Identifiers are drawn from ranges reserved
        for documentation and testing, so they are well-formed and cannot
        resolve to a real record.</p>
      </div>
      <div class="tiny muted mono" style="text-align:right">
        QualiZeal AI Center of Excellence<br>Synthetic demonstration build
      </div>
    </div>
  </div>
</footer>
</body></html>
"""


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

def build_index(registry: dict) -> str:
    t = registry["totals"]
    tiles = []
    for x in registry["tenants"]:
        c = x["counts"]
        rgb = tuple(int(x["accent"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        tiles.append(f"""
      <a class="card tile tilt rise" href="../demo/{x['slug']}/"
         style="--accent:{x['accent']};--accent-rgb:{rgb[0]},{rgb[1]},{rgb[2]}">
        <div class="sheen"></div>
        <div class="card-pad">
          <div class="top">
            <img class="tile-logo" src="../assets/brand/{x['slug']}-lockup.png"
                 alt="{html.escape(x['slug'])}" loading="lazy" decoding="async">
          </div>
          <span class="ind">{html.escape(x['industry'])}</span>
          <span class="nm">{html.escape(x['tenant'])}</span>
          <p class="small muted" style="margin:0">{html.escape(x['tagline'])}</p>
          <div class="facts">
            <div><b>{c['documents']}</b>documents</div>
            <div><b>{c['entities']}</b>entities</div>
            <div><b>{c['relationships']}</b>edges</div>
            <div><b>{x['health']}</b>health</div>
          </div>
          <div class="go">Open demonstration
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
              <path d="M5 12h13M13 6l6 6-6 6"/></svg>
          </div>
        </div>
      </a>""")

    links = [("Home", "../"), ("Solution fit", "../configurator/"),
             ("Admin", "../admin/")]

    return head(
        "Knowledge Fabric · Demonstrations",
        "Eleven industry knowledge fabrics. Citation-grounded answers, a live "
        "entity graph, and knowledge health measured directly from the corpus.",
        "../", "#0B66E1"
    ) + topbar("../", links) + f"""
<main>

  <section style="padding-top:clamp(3rem,7vh,6rem)">
    <div class="wrap">
      <div class="grid" style="grid-template-columns:minmax(320px,1.02fr) minmax(320px,1fr);align-items:center;gap:3.2rem">
        <div>
          <div class="eyebrow rise">Demonstrations</div>
          <h1 class="rise" style="font-size:clamp(2.3rem,4.4vw,3.9rem)">Eleven industries.<br><span class="grad">Pick yours, ask it anything.</span></h1>
          <p class="lede rise" style="margin-top:1.5rem">
            Full synthetic corpora — ask a question, open the citation.
          </p>
          <div class="row rise" style="margin-top:2rem">
            <a class="btn" href="#domains">
              Explore the domains
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                <path d="M12 5v13M6 13l6 6 6-6"/></svg>
            </a>
            <a class="btn btn-ghost" href="#how">How it works</a>
          </div>
          <div class="grid g4 rise" style="margin-top:3rem;gap:1.6rem">
            <div class="stat"><div class="n" data-to="{t['documents']}">0</div><div class="l">Documents</div></div>
            <div class="stat"><div class="n" data-to="{t['passages']}">0</div><div class="l">Cited passages</div></div>
            <div class="stat"><div class="n" data-to="{t['entities']}">0</div><div class="l">Entities</div></div>
            <div class="stat"><div class="n" data-to="{t['relationships']}">0</div><div class="l">Relationships</div></div>
          </div>
        </div>

        <div class="stage rise" style="aspect-ratio:1/.92;min-height:400px">
          <canvas id="heroGalaxy"></canvas>
          <div class="stage-ui">
            <div class="stage-hint">Drag to orbit · scroll to zoom</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section id="domains">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">The domains</div>
        <h2 class="rise">Built from how each industry documents itself.</h2>
        <p class="lede rise" style="margin-top:1rem">
          Fictional tenants on real scaffolding — ATA, HL7 FHIR, X12, PCAOB,
          MARPOL, GS1, ISO 29119.
        </p>
      </div>
      <div class="grid g3">{''.join(tiles)}</div>
    </div>
  </section>

  <section id="how">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">How it works</div>
        <h2 class="rise">No model writes the answer.</h2>
        <p class="lede rise" style="margin-top:1rem">
          The demonstration runs entirely from static files. That constraint is
          the point: with no generation step, there is nothing that can invent a
          citation. Every sentence in an answer is lifted unmodified from an
          indexed paragraph, and the citation resolves to that paragraph.
        </p>
      </div>
      <div class="grid g4">
        <div class="card tilt rise"><div class="sheen"></div><div class="card-pad">
          <span class="badge">01</span>
          <h3 style="margin:.9rem 0 .5rem">Index to the paragraph</h3>
          <p class="small">Documents are split into addressable passages —
          document, section, paragraph — so a citation points somewhere
          specific enough to verify in seconds.</p>
        </div></div>
        <div class="card tilt rise"><div class="sheen"></div><div class="card-pad">
          <span class="badge">02</span>
          <h3 style="margin:.9rem 0 .5rem">Derive the graph</h3>
          <p class="small">Entities and relationships come from document
          structure, not inference. Every edge traces to a field in a specific
          document, so "why are these connected?" has a real answer.</p>
        </div></div>
        <div class="card tilt rise"><div class="sheen"></div><div class="card-pad">
          <span class="badge">03</span>
          <h3 style="margin:.9rem 0 .5rem">Quote, never paraphrase</h3>
          <p class="small">Ranking blends lexical score, field weighting and
          graph activation. The answer is assembled from the source sentences
          themselves.</p>
        </div></div>
        <div class="card tilt rise"><div class="sheen"></div><div class="card-pad">
          <span class="badge red">04</span>
          <h3 style="margin:.9rem 0 .5rem">Decline when weak</h3>
          <p class="small">Below the confidence threshold the system returns an
          explicit non-answer. A plausible paragraph built from weak matches is
          worse than nothing.</p>
        </div></div>
      </div>
    </div>
  </section>

  <section id="provenance">
    <div class="wrap-narrow">
      <div class="card rise"><div class="card-pad" style="padding:2.2rem">
        <div class="eyebrow">Provenance and safety</div>
        <h2 style="font-size:clamp(1.5rem,2.6vw,2.1rem)">Synthetic by construction,
          realistic by scaffolding.</h2>
        <p style="margin-top:1.2rem">
          No client data was used to build any part of this. Company names,
          people, sites, dates and events are invented. What is real is the
          structure: the standards each industry is governed by, the document
          types it produces, and the shape of its identifiers.
        </p>
        <p>
          Identifiers are generated from ranges the issuing authorities reserve
          for documentation and testing — RFC 5737 address blocks, RFC 2606
          domains, ISO 3166 user-assigned country codes, ICAO
          <code class="mono">ZZZZ</code>, GS1 restricted-circulation prefixes,
          never-issued number ranges. They pass check-digit validation and
          cannot resolve to a real record.
        </p>
        <p style="margin:0">
          Corpora are also statistically shaped rather than uniformly random:
          document volume follows each industry's seasonal cycle, code frequency
          follows a long tail, and revision dates decay toward the present the
          way a live document set does.
        </p>
      </div></div>
    </div>
  </section>

</main>
{FOOTER_TPL.replace('%LOGO%', logo('', 24)).replace('</body></html>', '')}
<script src="assets/vendor/three.min.js"></script>
<script src="assets/js/galaxy.js"></script>
<script>
(function(){{
  var io = new IntersectionObserver(function(es){{
    es.forEach(function(e){{ if(e.isIntersecting){{ e.target.classList.add('in'); io.unobserve(e.target); }} }});
  }}, {{threshold:.12, rootMargin:'0px 0px -8% 0px'}});
  document.querySelectorAll('.rise').forEach(function(el){{ io.observe(el); }});

  document.querySelectorAll('.tilt').forEach(function(el){{
    el.addEventListener('pointermove', function(e){{
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', ((e.clientX-r.left)/r.width*100)+'%');
      el.style.setProperty('--my', ((e.clientY-r.top)/r.height*100)+'%');
    }});
  }});

  var co = new IntersectionObserver(function(es){{
    es.forEach(function(e){{
      if(!e.isIntersecting) return;
      var el = e.target, to = +el.dataset.to, t0 = performance.now();
      (function step(t){{
        var k = Math.min(1,(t-t0)/1600), v = 1-Math.pow(1-k,3);
        el.textContent = Math.round(to*v).toLocaleString();
        if(k<1) requestAnimationFrame(step);
      }})(t0);
      co.unobserve(el);
    }});
  }}, {{threshold:.5}});
  document.querySelectorAll('[data-to]').forEach(function(el){{ co.observe(el); }});

  // Hero graph: a composite built from every tenant's hub entities, so the
  // landing page shows the whole fabric rather than one domain's slice.
  fetch('../data/overview.json').then(function(r){{return r.json();}}).then(function(g){{
    if(!window.THREE) return;
    var gx = new Galaxy(document.getElementById('heroGalaxy'), {{
      maxNodes: window.innerWidth < 760 ? 220 : 420, autorotate: 0.0009
    }});
    gx.setGraph(g, '#0B66E1');
    window.addEventListener('resize', function(){{ gx.resize(); }});
  }});
}})();
</script>
</body></html>
"""


# ---------------------------------------------------------------------------
# Presenter kit
#
# One page a salesperson or a sponsor can open cold: the two ways to present,
# the eleven demonstrations, every file worth sending, and the talk track.
# The point is that nobody has to ask the author how to run the meeting.
# ---------------------------------------------------------------------------

# Files under site/downloads/, committed rather than generated. Sizes are read
# from disk at build time so the page can never advertise a stale figure.
DOWNLOADS = [
    ("Knowledge-Fabric-Overview.pptx", "PowerPoint",
     "Overview deck — 12 slides",
     "The editable deck. Send it when the meeting expects an attachment, or "
     "when someone needs to lift a slide into their own pack.",
     "Same twelve slides as the browser deck, with fade transitions set."),
    ("Knowledge-Fabric-Capability-Overview.docx", "Word",
     "Capability overview — 11 pages",
     "The written record. The leave-behind for people who read rather than "
     "watch, and the attachment that survives being forwarded.",
     "Covers capability, coverage, value, deployment and delivery."),
    ("knowledge-fabric-architecture.jpg", "Image · 3800 px",
     "Reference architecture",
     "The five zones and the loop that returns unanswered questions to the "
     "content pipeline. Drops into a proposal or a whiteboard session.",
     "Print quality. Also slide 5 of the deck."),
    ("knowledge-fabric-answer-workflow.jpg", "Image · 3800 px",
     "Answer workflow",
     "The six stages, with the two gates and the clarify-back loop drawn out. "
     "Use it when the question is \"but how does it actually answer?\"",
     "Print quality. Pairs with slide 4."),
]

# The talk track. Section, and the single point to make there — lifted from
# how the walkthrough is meant to be driven, so a presenter who has never
# seen it delivered still knows where to slow down.
TALK = [
    ("Hero", "The loom weaves itself on load. Vertical threads are source "
     "documents, horizontal threads are questions, each knot is a citation. "
     "Let it finish before you speak."),
    ("The problem", "The right answer already exists — it is unreachable in "
     "time. Not a wrong answer: a slow one, or a confident one taken from a "
     "superseded revision."),
    ("How it works", "Six stages. Pause on stages 2 and 4 — permissions "
     "before searching, evidence before writing. Those are the two gates, "
     "and they are the argument."),
    ("Clarify-back", "The differentiator. Most systems refuse or invent. "
     "This one asks one question and retries, and logs what was missing."),
    ("Architecture", "Five zones, and the violet loop at the bottom that "
     "returns unanswered questions as a ranked content backlog."),
    ("Capabilities → Value", "Scan, don't read aloud. Let the client stop "
     "you where they care — that is the discovery."),
    ("Delivery", "Four phases, each ending in something they can judge for "
     "themselves. Phase 2 is the one they will ask about."),
    ("Close", "Five things most systems don't do. Leave this on screen "
     "while you talk about next steps."),
]

AGENDA = [
    ("0–2 min", "Open the walkthrough", "Let the hero animation finish. One "
     "sentence: answers drawn only from documents you have already approved."),
    ("2–6 min", "The problem, in their words", "Scroll to the problem "
     "section and ask which of the five they recognise. Stop talking."),
    ("6–14 min", "How an answer is produced", "Walk the six stages. Slow at "
     "the two gates, then the clarify-back loop."),
    ("14–22 min", "Open a demonstration", "Pick the domain closest to their "
     "industry. Ask their question, not a rehearsed one. Open a citation."),
    ("22–28 min", "Delivery and portability", "Four phases; nothing in the "
     "stack is a lock-in. This is the leadership conversation."),
    ("28–30 min", "Close and leave-behind", "Send the deck and the "
     "capability overview from this page before you leave the room."),
]

SAY = [
    ("Say", "Every answer is traced to the document, page and paragraph it "
     "came from."),
    ("Say", "The demonstrations run on synthetic corpora built from real "
     "industry standards — ATA chapters, HL7 FHIR, X12, PCAOB, GS1, ISO 29119."),
    ("Say", "Model, vector store, embedding and identity provider are all "
     "deployment choices. None of them is the product."),
    ("Don't", "Don't present the demonstration corpora as a customer "
     "deployment or a case study. Every tenant, person and document in them "
     "is invented."),
    ("Don't", "Don't quote commercial figures, savings percentages or "
     "timelines beyond the phase durations shown. None are published here, "
     "and none should be improvised."),
    ("Don't", "Don't name a client. The material is generic by construction "
     "so that it can be shown to anyone."),
]


def _size(name: str) -> str:
    p = SITE / "downloads" / name
    if not p.exists():
        return "—"
    mb = p.stat().st_size / 1024 / 1024
    return f"{mb:.1f} MB" if mb >= 1 else f"{p.stat().st_size / 1024:.0f} KB"


def build_kit(registry: dict) -> str:
    t = registry["totals"]

    domains = "".join(
        f"""<a class="chip" href="../demo/{x['slug']}/">
              <span class="dot" style="background:{x['accent']}"></span>
              {html.escape(x['industry'])}</a>"""
        for x in registry["tenants"])

    files = "".join(f"""
      <div class="card rise">
        <div class="card-pad" style="display:flex;flex-direction:column;height:100%">
          <span class="tiny mono muted">{html.escape(kind)} · {_size(name)}</span>
          <h3 style="font-size:1.05rem;margin:.35rem 0 .55rem">{html.escape(title)}</h3>
          <p class="small" style="margin:0 0 .7rem">{html.escape(what)}</p>
          <p class="tiny muted" style="margin:0 0 1.1rem">{html.escape(note)}</p>
          <a class="btn btn-ghost btn-sm" href="../downloads/{name}" download
             style="margin-top:auto;align-self:flex-start">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 stroke-width="2.4" stroke-linecap="round"><path d="M12 4v12M6 11l6 6 6-6"/>
              <path d="M4 20h16"/></svg>
            Download</a>
        </div></div>""" for name, kind, title, what, note in DOWNLOADS)

    talk = "".join(f"""
      <tr>
        <td class="mono tiny" style="white-space:nowrap;vertical-align:top;
            color:var(--qz-blue);padding:.5rem 2rem .5rem 0">{html.escape(s)}</td>
        <td class="small" style="padding:.5rem 0">{html.escape(p)}</td>
      </tr>"""
        for s, p in TALK)

    agenda = "".join(f"""
      <div class="card rise"><div class="card-pad" style="padding:1.2rem 1.4rem">
        <span class="tiny mono muted">{html.escape(when)}</span>
        <h3 style="font-size:1rem;margin:.4rem 0 .5rem">{html.escape(what)}</h3>
        <p class="tiny muted" style="margin:0">{html.escape(how)}</p>
      </div></div>""" for when, what, how in AGENDA)

    rules = "".join(f"""
      <li style="display:flex;gap:.9rem;padding:.7rem 0;border-bottom:1px solid var(--line)">
        <span class="badge{' red' if k == "Don't" else ' green'}"
              style="flex:none">{html.escape(k)}</span>
        <span class="small">{html.escape(v)}</span></li>""" for k, v in SAY)

    links = [("Present", "#present"), ("Demonstrations", "#demos"),
             ("Qualify", "#qualify"), ("Downloads", "#downloads"),
             ("Run the meeting", "#runbook"), ("Ground rules", "#rules")]

    return head(
        "Presenter kit · Knowledge Fabric",
        "Everything needed to present Knowledge Fabric without a briefing: "
        "the live walkthrough, the deck, eleven demonstrations, every "
        "downloadable file and the talk track.",
        "../", "#0B66E1"
    ) + topbar("../", links) + f"""
<script>window.GATE_BASE="../";</script>
<script src="../assets/js/gate.js"></script>
<main>

  <section style="padding-top:clamp(2.6rem,6vh,5rem)">
    <div class="wrap">
      <div class="eyebrow rise">Presenter kit</div>
      <h1 class="rise" style="font-size:clamp(2.1rem,4vw,3.4rem);max-width:20ch">
        Everything you need to <span class="grad">run the meeting</span>.</h1>
      <p class="lede rise" style="margin-top:1.4rem">
        Two ways to present, eleven live demonstrations, four files to send
        afterwards and the talk track that goes with them. Nothing here needs
        a briefing first, and nothing here is tied to one client — the whole
        kit is generic by construction, so it can be shown to anyone.
      </p>
      <div class="grid g4 rise" style="margin-top:2.6rem;gap:1.6rem">
        <div class="stat"><div class="n" data-to="2">0</div><div class="l">Ways to present</div></div>
        <div class="stat"><div class="n" data-to="11">0</div><div class="l">Live demonstrations</div></div>
        <div class="stat"><div class="n" data-to="4">0</div><div class="l">Files to send</div></div>
        <div class="stat"><div class="n" data-to="{t['documents']}">0</div><div class="l">Documents behind them</div></div>
      </div>
    </div>
  </section>

  <section id="present">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Present</div>
        <h2 class="rise">Two ways in. Pick by the room, not by habit.</h2>
        <p class="lede rise" style="margin-top:1rem">
          Both open in a browser and need nothing installed. The walkthrough
          is a conversation; the deck is a deck.
        </p>
      </div>
      <div class="grid g2">
        <a class="card tilt rise" href="../"><div class="sheen"></div>
          <div class="card-pad" style="padding:2rem">
            <span class="badge">Live walkthrough</span>
            <h3 style="margin:1rem 0 .6rem;font-size:1.4rem">Scroll-driven, one page</h3>
            <p class="small">Built to be driven in front of a client instead
            of sending a deck. It opens with a seventy-second film in which
            the fabric introduces itself, the six stages advance as you
            scroll, and in the architecture section the audience watches a
            live question make the whole journey — held at the evidence gate,
            clarified, then answered with citations. A left rail jumps
            anywhere when somebody wants to skip ahead.</p>
            <p class="tiny muted" style="margin-top:.9rem">Best for discovery
            calls and technical audiences · 20–30 minutes · keyboard navigable</p>
            <div class="go" style="margin-top:1.2rem">Open the walkthrough
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   stroke-width="2.4" stroke-linecap="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg>
            </div>
          </div></a>

        <a class="card tilt rise" href="../deck/"><div class="sheen"></div>
          <div class="card-pad" style="padding:2rem">
            <span class="badge">Overview deck</span>
            <h3 style="margin:1rem 0 .6rem;font-size:1.4rem">Twelve slides, in the browser</h3>
            <p class="small">The same twelve slides as the PowerPoint,
            rendered natively — no PowerPoint installed, no fonts to go
            missing on a borrowed laptop. Slides build as they open, and the
            architecture slide runs the animated answer journey live. Arrow
            keys to advance, <b>G</b> for the overview, <b>F</b> for full
            screen, <b>Ctrl+P</b> for a clean PDF.</p>
            <p class="tiny muted" style="margin-top:.9rem">Best for leadership
            and procurement · 15–25 minutes · projector-safe</p>
            <div class="go" style="margin-top:1.2rem">Open the deck
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   stroke-width="2.4" stroke-linecap="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg>
            </div>
          </div></a>
      </div>
    </div>
  </section>

  <section id="demos">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Demonstrate</div>
        <h2 class="rise">Open the domain closest to the room.</h2>
        <p class="lede rise" style="margin-top:1rem">
          Eleven full corpora — {t['documents']} documents, {t['passages']}
          cited passages, {t['entities']} entities. Ask a real question rather
          than a rehearsed one, then open the citation it returns: the
          paragraph it quoted is right there, which is the whole point.
        </p>
      </div>
      <div class="row rise" style="flex-wrap:wrap;gap:.6rem">{domains}</div>
      <div class="card rise" style="margin-top:2rem"><div class="card-pad">
        <p class="small" style="margin:0"><b>If nothing matches their
        industry</b>, open the closest regulated one and say so. The
        scaffolding — document types, approval chains, code systems — is what
        transfers, not the industry label.</p>
      </div></div>
    </div>
  </section>

  <section id="qualify">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Qualify</div>
        <h2 class="rise">Turn their constraints into their architecture.</h2>
        <p class="lede rise" style="margin-top:1rem">
          When the room starts asking "would this work for us?", open the solution-fit
          questionnaire together. Nine choices — their name first, then domain, cloud,
          sign-in, models, index, roles, telemetry, scope — and the page composes the
          architecture we would propose, drawn with the vendors' own marks, lists what
          ships, states the limitations out loud, and hands them the demonstration
          closest to their world. Every combination has a prepared answer; the takeaway
          is two print-locked PDFs addressed to the client by name — the architecture
          drawing and a written proposal.
        </p>
      </div>
      <a class="card tilt rise" href="../configurator/" style="display:block"><div class="sheen"></div>
        <div class="card-pad" style="display:flex;align-items:center;justify-content:space-between;gap:2rem;padding:2rem">
          <div>
            <span class="badge">Solution fit</span>
            <h3 style="margin:.9rem 0 .5rem;font-size:1.35rem">Nine questions. Their fabric, addressed to them.</h3>
            <p class="small" style="margin:0">Rule-based, honest and shareable — the
            limitations panel is the part prospects remember.</p>
          </div>
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="var(--qz-blue)"
            stroke-width="2.4" stroke-linecap="round" style="flex:none"><path d="M5 12h13M13 6l6 6-6 6"/></svg>
        </div></a>
    </div>
  </section>

  <section id="downloads">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Send</div>
        <h2 class="rise">Four files. Send them from the room.</h2>
        <p class="lede rise" style="margin-top:1rem">
          The deck and the written overview carry the same content model as
          the walkthrough, so a client who watched the demonstration and a
          colleague who only reads the attachment end up with the same story.
        </p>
      </div>
      <div class="grid g4">{files}</div>
    </div>
  </section>

  <section id="runbook">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Run the meeting</div>
        <h2 class="rise">Thirty minutes, and where to slow down.</h2>
      </div>
      <div class="grid g3" style="margin-bottom:3rem">{agenda}</div>

      <div class="card rise"><div class="card-pad" style="padding:2rem">
        <div class="eyebrow" style="margin-bottom:1.4rem">The point to make, section by section</div>
        <table style="width:100%;border-collapse:collapse">
          <tbody>{talk}</tbody>
        </table>
        <p class="tiny muted" style="margin:1.4rem 0 0">
          Two gates carry the argument: permissions applied before searching,
          evidence scored before writing. If a room remembers one thing, make
          it those.</p>
      </div></div>
    </div>
  </section>

  <section id="rules">
    <div class="wrap-narrow">
      <div class="card rise"><div class="card-pad" style="padding:2.2rem">
        <div class="eyebrow">Ground rules</div>
        <h2 style="font-size:clamp(1.4rem,2.4vw,1.9rem)">What is safe to claim.</h2>
        <p style="margin-top:1rem">
          Everything in this kit is deliberately generic — no client names, no
          commercial figures, no deployment tied to one customer. That is what
          makes it safe to hand to anyone, and it only stays true if it is
          presented as built.
        </p>
        <ul style="list-style:none;margin-top:1.4rem">{rules}</ul>
      </div></div>
    </div>
  </section>

</main>
{FOOTER_TPL.replace('%LOGO%', logo('../', 24)).replace('</body></html>', '')}
<script>
(function(){{
  var io = new IntersectionObserver(function(es){{
    es.forEach(function(e){{ if(e.isIntersecting){{ e.target.classList.add('in'); io.unobserve(e.target); }} }});
  }}, {{threshold:.12, rootMargin:'0px 0px -8% 0px'}});
  document.querySelectorAll('.rise').forEach(function(el){{ io.observe(el); }});

  document.querySelectorAll('.tilt').forEach(function(el){{
    el.addEventListener('pointermove', function(e){{
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', ((e.clientX-r.left)/r.width*100)+'%');
      el.style.setProperty('--my', ((e.clientY-r.top)/r.height*100)+'%');
    }});
  }});

  var co = new IntersectionObserver(function(es){{
    es.forEach(function(e){{
      if(!e.isIntersecting) return;
      var el = e.target, to = +el.dataset.to, t0 = performance.now();
      (function step(t){{
        var k = Math.min(1,(t-t0)/1400), v = 1-Math.pow(1-k,3);
        el.textContent = Math.round(to*v).toLocaleString();
        if(k<1) requestAnimationFrame(step);
      }})(t0);
      co.unobserve(el);
    }});
  }}, {{threshold:.5}});
  document.querySelectorAll('[data-to]').forEach(function(el){{ co.observe(el); }});
}})();
</script>
</body></html>
"""


# ---------------------------------------------------------------------------
# Tenant demonstration page
# ---------------------------------------------------------------------------

def build_demo(m: dict) -> str:
    slug = m["slug"]
    rgb = tuple(int(m["accent"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    base = "../../"
    links = [("Graph", "#graph"), ("Answer", "#answerSection"),
             ("Findings", "#findingsSection"),
             ("Lineage", "#lineageSection"), ("Health", "#health"),
             ("Insights", "#insights"), ("Corpus", "#corpus")]

    doc_types = "".join(
        f'<span class="tiny mono">{html.escape(d["abbrev"] or d["name"])}</span>'
        for d in m["doc_types"])
    code_sys = "".join(
        f"""<div class="card tilt rise"><div class="sheen"></div><div class="card-pad">
              <div class="row between"><h3 style="font-size:1rem">{html.escape(c['name'])}</h3>
              <span class="badge">{len(c['codes'])}</span></div>
              <p class="tiny muted mono" style="margin:.5rem 0 .8rem">{html.escape(c['authority'])} · {html.escape(c['fmt'])}</p>
              <div class="cloud tiny">{''.join(f'<span class="mono" title="{html.escape(x["m"])}">{html.escape(x["c"])}</span>' for x in c['codes'][:12])}</div>
            </div></div>"""
        for c in m["code_systems"])
    flows = "".join(
        f"""<div class="card rise"><div class="card-pad">
              <h3 style="font-size:1rem;margin-bottom:.9rem">{html.escape(w['name'])}</h3>
              <div class="row" style="gap:.35rem">
              {''.join(f'<span class="chip tiny" style="pointer-events:none">{html.escape(s)}</span>' for s in w['states'])}
              </div></div></div>"""
        for w in m["workflows"])

    return head(
        f"{m['tenant']} · Knowledge Fabric",
        f"{m['industry']} knowledge fabric — {m['counts']['documents']} documents, "
        f"citation-grounded answers and a live entity graph.",
        base, m["accent"]
    ) + f"""<style>:root{{--accent:{m['accent']};--accent-rgb:{rgb[0]},{rgb[1]},{rgb[2]}}}</style>
""" + topbar(base, links) + f"""
<body-marker>
<main data-tenant="{slug}">

  <section style="padding-top:clamp(2.4rem,5vh,4rem);padding-bottom:2rem">
    <div class="wrap">
      <div class="row between rise" style="margin-bottom:1.6rem">
        <div class="row" style="gap:1.4rem;align-items:center">
          <img class="tenant-lockup" src="{base}assets/brand/{slug}-lockup.png"
               alt="{html.escape(m['tenant'])}" loading="eager" decoding="async">
          <div>
            <div class="eyebrow" style="margin-bottom:.7rem">{html.escape(m['industry'])}</div>
            <h1 style="font-size:clamp(1.7rem,3.6vw,2.9rem)">{html.escape(m['tenant'])}</h1>
            <p class="small muted" style="margin-top:.5rem">{html.escape(m['tagline'])}</p>
          </div>
        </div>
        <a class="btn btn-ghost btn-sm" href="{base}index.html">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.4" stroke-linecap="round"><path d="M19 12H6M11 6l-6 6 6 6"/></svg>
          All domains</a>
      </div>

      <div class="grid g4 rise" style="margin-bottom:2.2rem">
        <div class="stat"><div class="n" data-stat="documents">0</div><div class="l">Documents</div></div>
        <div class="stat"><div class="n" data-stat="passages">0</div><div class="l">Passages</div></div>
        <div class="stat"><div class="n" data-stat="entities">0</div><div class="l">Entities</div></div>
        <div class="stat"><div class="n" data-stat="relationships">0</div><div class="l">Relationships</div></div>
      </div>

      <div class="ask rise" id="askBar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--ink-mute)"
             stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
        <input id="q" type="text" autocomplete="off"
               placeholder="Ask this corpus a question…"
               aria-label="Ask this corpus a question">
        <button class="btn" id="askBtn">Ask
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.4" stroke-linecap="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg>
        </button>
      </div>
      <div class="row rise" id="suggest" style="margin-top:1rem;gap:.45rem"></div>
      <div id="loading" class="tiny muted mono" style="margin-top:1rem">Loading fabric…</div>
    </div>
  </section>

  <section id="graph" style="padding-top:1rem">
    <div class="wrap">
      <div class="stage rise" style="height:min(76vh,680px)">
        <canvas id="galaxy"></canvas>
        <div class="stage-ui">
          <div class="legend" id="legend"></div>
          <div class="stage-hint">Drag to orbit · scroll to zoom · click a node</div>
          <div class="tip" id="tip"></div>
        </div>
      </div>
      <p class="tiny muted center" style="margin-top:1rem">
        Entities and edges derived from document structure. Ask a question above
        to light the retrieval path through the graph.
      </p>
    </div>
  </section>

  <section id="answerSection">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Live answer</div>
        <h2 class="rise">Quoted verbatim, never paraphrased.</h2>
      </div>
      <div class="grid" style="grid-template-columns:minmax(320px,1.7fr) minmax(260px,1fr)">
        <div class="card rise"><div class="card-pad" style="padding:1.8rem">
          <div id="answer"><p class="muted small">Ask a question above, or pick one
            of the suggestions, to populate this section with a cited answer.</p></div>
        </div></div>
        <div class="card rise"><div class="card-pad">
          <div id="answerMeta"><p class="muted small">Confidence, source count and
            graph activation appear here.</p></div>
        </div></div>
      </div>
    </div>
  </section>

  <section id="findingsSection">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Graph findings</div>
        <h2 class="rise">The answer no single document contains.</h2>
        <p class="lede rise" style="margin-top:1rem">
          Retrieval finds passages that mention your question. Traversal joins
          relationships across documents to assemble an answer set — a list of
          affected entities that exists in no file, only in the connections
          between them.
        </p>
      </div>
      <div class="card rise"><div class="card-pad" style="padding:1.8rem">
        <div id="findings"><p class="muted small">Ask a question to traverse the graph.</p></div>
      </div></div>
    </div>
  </section>

  <section id="lineageSection">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Explainability</div>
        <h2 class="rise">The full chain, question to citation.</h2>
      </div>
      <div class="card rise"><div class="card-pad" style="padding:1.8rem">
        <div class="rail" id="lineage">
          <p class="muted small">Ask a question to trace the retrieval chain.</p>
        </div>
      </div></div>
    </div>
  </section>

  <section id="health">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Knowledge health</div>
        <h2 class="rise">Find the gaps before they cost you.</h2>
        <p class="lede rise" style="margin-top:1rem">
          Knowledge that sits in one document, that nobody can date, or that
          extraction has turned to debris is a risk you cannot see on a shared
          drive. Every score below is measured from the corpus — click any card
          to see the formula and the raw inputs behind it.
        </p>
      </div>
      <div class="grid" style="grid-template-columns:minmax(260px,320px) 1fr;gap:2.2rem;align-items:start">
        <div class="rise">
          <div class="card"><div class="card-pad center">
            <div id="healthRing"></div>
          </div></div>
          <div class="card" style="margin-top:1rem"><div class="card-pad">
            <div id="healthSummary"></div>
          </div></div>
        </div>
        <div class="grid g2" id="healthDims"></div>
      </div>

      <div class="section-head rise" style="margin:3.2rem 0 1.4rem">
        <div class="eyebrow">Where the risk sits</div>
        <h3>Four exposures, counted rather than estimated.</h3>
      </div>
      <div class="grid g4" id="healthRisks"></div>
    </div>
  </section>

  <section id="insights">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Insights</div>
        <h2 class="rise">The corpus at a glance.</h2>
      </div>
      <div class="tabs rise" data-tabs="ins">
        <button class="on" data-tab="types">Document types</button>
        <button data-tab="units">Units</button>
        <button data-tab="hubs">Graph hubs</button>
        <button data-tab="clusters">Clusters</button>
        <button data-tab="concepts">Concepts</button>
        <button data-tab="timeline">Timeline</button>
        <button data-tab="model">Domain model</button>
      </div>
      <div class="card rise" style="margin-top:1.2rem"><div class="card-pad" style="padding:1.8rem">
        <div class="panel on" data-panel-group="ins" data-panel="types" id="insDocTypes"></div>
        <div class="panel" data-panel-group="ins" data-panel="units" id="insUnits"></div>
        <div class="panel" data-panel-group="ins" data-panel="hubs" id="insHubs"></div>
        <div class="panel" data-panel-group="ins" data-panel="clusters" id="insDendro"></div>
        <div class="panel" data-panel-group="ins" data-panel="concepts" id="insConcepts"></div>
        <div class="panel" data-panel-group="ins" data-panel="timeline" id="insTimeline"></div>
        <div class="panel" data-panel-group="ins" data-panel="model">
          <div class="eyebrow">Code systems</div>
          <div class="grid g3" style="margin-bottom:2rem">{code_sys}</div>
          <div class="eyebrow">Workflow states</div>
          <div class="grid g2">{flows}</div>
        </div>
      </div></div>
    </div>
  </section>

  <section id="corpus">
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow rise">Corpus</div>
        <h2 class="rise">Read any document in full.</h2>
      </div>
      <div class="ask rise" style="max-width:520px;margin-bottom:1.6rem">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--ink-mute)"
             stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
        <input id="corpusSearch" type="text" placeholder="Filter by title, ID, unit or type…"
               aria-label="Filter the corpus">
        <span class="mono tiny muted" id="corpusCount" style="padding-right:1rem"></span>
      </div>
      <div class="grid g3" id="corpusList"></div>
    </div>
  </section>

</main>

<div class="sheet" id="sheet" role="dialog" aria-modal="true" aria-labelledby="sheetTitle">
  <div class="sheet-in">
    <div class="sheet-head">
      <div style="flex:1">
        <h3 id="sheetTitle">Document</h3>
        <div id="sheetMeta"></div>
      </div>
      <button class="x" id="sheetClose" aria-label="Close">&times;</button>
    </div>
    <div class="sheet-body" id="sheetBody"></div>
  </div>
</div>

{FOOTER_TPL.replace('%LOGO%', logo(base, 24)).replace('</body></html>', '')}
<script src="{base}assets/vendor/three.min.js"></script>
<script src="{base}assets/js/galaxy.js"></script>
<script src="{base}assets/js/engine.js"></script>
<script src="{base}assets/js/app.js"></script>
</body></html>
"""


# ---------------------------------------------------------------------------
# Overview graph for the landing hero
# ---------------------------------------------------------------------------

def build_overview(slugs: list[str]) -> dict:
    """A composite graph: each tenant's top hubs, plus the tenant node itself.

    The landing page should show the whole fabric, not one domain. Linking each
    tenant's hubs back to a tenant node produces eleven visible clusters joined
    at a centre — which is a truthful picture of what the product is.
    """
    nodes, edges = [], []
    for slug in slugs:
        g = json.loads((TENANTS / slug / "fabric" / "graph.json").read_text())
        m = json.loads((TENANTS / slug / "tenant.json").read_text())
        tid = f"unit:{m['tenant']}"
        nodes.append({"id": tid, "label": m["tenant"], "kind": "unit",
                      "docs": [], "degree": 40})
        top = sorted(g["nodes"], key=lambda n: -n["degree"])[:34]
        keep = {n["id"] for n in top}
        for n in top:
            nid = f"{slug}|{n['id']}"
            nodes.append({"id": nid, "label": n["label"], "kind": n["kind"],
                          "docs": [], "degree": n["degree"]})
            edges.append({"s": tid, "t": nid, "rel": "IN_DOMAIN", "docs": []})
        for e in g["edges"]:
            if e["s"] in keep and e["t"] in keep:
                edges.append({"s": f"{slug}|{e['s']}", "t": f"{slug}|{e['t']}",
                              "rel": e["rel"], "docs": []})
    return {"nodes": nodes, "edges": edges,
            "kinds": {"unit": "Domain", "system": "System",
                      "authority": "Standard", "site": "Site",
                      "subject": "Subject", "doctype": "Document type",
                      "role": "Role", "code": "Code"},
            "ontology": []}


# ---------------------------------------------------------------------------

def main() -> None:
    reg_path = TENANTS / "registry.json"
    if not reg_path.exists():
        raise SystemExit(
            "tenants/registry.json not found — run "
            "`python -m pipeline.build_tenants` first."
        )
    registry = json.loads(reg_path.read_text())
    slugs = [t["slug"] for t in registry["tenants"]]

    # Clear generated routes but never assets/.
    for p in (SITE / "demo", SITE / "data", SITE / "demos"):
        if p.exists():
            shutil.rmtree(p)

    print("=" * 74)
    print("  Knowledge Fabric — site build")
    print("=" * 74)

    total_bytes = 0
    for slug in slugs:
        src = TENANTS / slug
        dst = SITE / "data" / slug
        dst.mkdir(parents=True, exist_ok=True)

        for name in ("graph.json", "index.json", "health.json",
                     "insights.json", "documents.json", "semantic.json",
                     "dendrogram.json"):
            shutil.copyfile(src / "fabric" / name, dst / name)
        shutil.copyfile(src / "tenant.json", dst / "tenant.json")
        # Document bodies are NOT copied. The viewer reconstructs them from the
        # passage index, which already holds every paragraph with its section
        # and ordinal. Shipping both would duplicate the entire corpus for no
        # capability — it was 11 MB of the old payload.

        m = json.loads((src / "tenant.json").read_text())
        page = SITE / "demo" / slug / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        # The <main> carries the tenant; move it onto <body> where app.js reads it.
        htmlsrc = build_demo(m).replace(
            "<body-marker>\n<main data-tenant=", "<main data-tenant=")
        htmlsrc = htmlsrc.replace(
            "<body>\n<div class=\"field\">",
            f"<body data-tenant=\"{slug}\" data-base=\"../../\">\n<div class=\"field\">")
        page.write_text(htmlsrc, encoding="utf-8")

        size = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file())
        total_bytes += size
        print(f"  demo/{slug:<18} {m['counts']['documents']:>3} docs · "
              f"{size / 1024 / 1024:>5.1f} MB")

    overview = build_overview(slugs)
    (SITE / "data" / "overview.json").write_text(
        json.dumps(overview, separators=(",", ":")), encoding="utf-8")

    demos = SITE / "demos" / "index.html"
    demos.parent.mkdir(parents=True, exist_ok=True)
    demos.write_text(build_index(registry), encoding="utf-8")

    kit = SITE / "kit" / "index.html"
    kit.parent.mkdir(parents=True, exist_ok=True)
    kit.write_text(build_kit(registry), encoding="utf-8")

    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    print("-" * 74)
    print(f"  {len(slugs)} demonstrations · {total_bytes / 1024 / 1024:.1f} MB payload")
    print(f"  demos:   site/demos/index.html")
    print(f"  routes:  site/demo/<slug>/index.html")
    print(f"  kit:     site/kit/index.html")
    print(f"  static:  site/walkthrough/  site/deck/  site/downloads/")
    print("=" * 74)


if __name__ == "__main__":
    main()
