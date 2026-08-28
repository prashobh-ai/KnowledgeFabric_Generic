/* Knowledge Fabric — browser deck
 *
 * The same twelve slides as Knowledge-Fabric-Overview.pptx, rendered natively
 * so a meeting can be run from a browser with no PowerPoint installed and no
 * font substitution. All copy lives in SLIDES below: edit the array, save,
 * refresh. There is no build step.
 *
 * If you change a slide here, change it in the .pptx too — the deck download
 * and this page are meant to be the same deck.
 */

const SLIDES = [

/* 1 */ {kind: "title", eyebrow: "AI Center of Excellence",
  title: "Knowledge Fabric",
  sub: "Enterprise Knowledge Intelligence",
  lede: "Answers your organisation can defend, drawn only from documents it has already approved.",
  by: "QualiZeal · AI Center of Excellence"},

/* 2 */ {kind: "cards4", nav: "What it is",
  title: "What Knowledge Fabric is",
  sub: "A system that answers from your own approved documents — and shows its work",
  items: [
    {h: "Answers, not documents", hue: "blue",
     p: "Plain-language answers assembled from approved sources, never from general world knowledge."},
    {h: "Every claim carries its source", hue: "indigo",
     p: "Each sentence traces to a document, page and paragraph the organisation already approved."},
    {h: "It asks before it guesses", hue: "amber",
     p: "When evidence is thin the system asks one clarifying question instead of refusing or inventing."},
    {h: "It reports its own gaps", hue: "violet",
     p: "Questions the corpus cannot answer become a ranked content backlog for the people who own it."}]},

/* 3 */ {kind: "problem", nav: "The problem",
  title: "The problem it addresses",
  sub: "The authoritative answer usually exists — it is just unreachable in the time available",
  label: "Where the time goes",
  items: [
    {h: "Answers are slow",
     p: "The document exists; finding the right revision of it does not fit inside the decision window."},
    {h: "Answers are inconsistent",
     p: "Two sites, two teams or two languages give different answers to the same question."},
    {h: "Answers are undefendable",
     p: "When an auditor asks where an answer came from, nobody can reconstruct the trail."},
    {h: "Knowledge leaves",
     p: "Institutional memory walks out with the people who hold it, and nothing captures what was lost."},
    {h: "Gaps stay invisible",
     p: "Nobody knows which questions the organisation cannot currently answer until it matters."}],
  quote: ["Search returns documents.", "People need answers."],
  quoteBody: "General assistants return fluent answers. Regulated organisations need provenance. Knowledge Fabric is built for the space between the two — fluent answers that carry their evidence with them.",
  foot: "The damage is rarely a wrong answer. It is a slow one — or a confident one taken from a superseded revision."},

/* 4 */ {kind: "flow", nav: "How it works",
  title: "How an answer is produced",
  sub: "Six stages — permissions applied before searching, evidence scored before writing",
  steps: [
    {h: "Question",       p: "Asked in plain language, in the user's language.",      hue: "blue"},
    {h: "Access scope",   p: "Only sources this person may see are searched.",        hue: "indigo", gate: true},
    {h: "Retrieve",       p: "Meaning-based and exact-term search, merged.",          hue: "blue"},
    {h: "Grounding check",p: "Evidence scored before a word is written.",             hue: "amber",  gate: true},
    {h: "Generate",       p: "Written only from retrieved sources, citations inline.", hue: "blue"},
    {h: "Scored answer",  p: "Delivered with citations and a confidence level.",      hue: "violet"}],
  bandLabel: "Clarify-back · ask, don't refuse",
  bandSub: "the recovery path, not a dead end",
  band: [
    {h: "Below threshold",
     p: "One targeted question goes back to the user — which entity, which process area, what level of detail. One question, never an interrogation."},
    {h: "Refined query",
     p: "The added constraint is folded into a fresh retrieval. In most cases this lifts the evidence above the threshold and the answer proceeds normally."},
    {h: "Still insufficient",
     p: "The system returns the nearest approved sources and guidance on how to rephrase. Never a bare refusal, and never an invented answer."}]},

/* 5 */ {kind: "archlive", nav: "Architecture",
  title: "Reference architecture",
  sub: "Five zones — and one question making the journey, live.",
  full: "../downloads/knowledge-fabric-architecture.jpg"},

/* 6 */ {kind: "zones", nav: "The zones",
  title: "What each zone does",
  sub: "One system, five responsibilities",
  items: [
    {h: "Access and roles", t: "who can ask, and what they may see", hue: "indigo",
     chips: ["Roles", "Web application", "Single sign-on", "Answer API"]},
    {h: "Content pipeline", t: "source of record to index", hue: "emerald",
     chips: ["Source of record", "Event-driven intake", "Extract and rank", "Curate and resolve", "Index sync"]},
    {h: "Grounded answering", t: "the answer is assembled here", hue: "blue",
     chips: ["Retrieve", "Grounding check", "Generate", "Clarify-back"]},
    {h: "Trust and telemetry", t: "proof that it worked", hue: "violet",
     chips: ["Per-answer scoring", "Tracing", "Usage, cost and quality", "Audit and export"]},
    {h: "Security and operations", t: "underpins every zone above", hue: "slate",
     chips: ["Private networking", "Key management", "Least privilege", "Edge protection", "Audit trail"]}],
  loop: "The zones close into a loop. Questions the corpus cannot yet answer travel from telemetry back to the content pipeline as a ranked backlog, so the platform improves from real use rather than guesswork."},

/* 7 */ {kind: "table", nav: "Coverage",
  title: "Functional coverage",
  sub: "Delivered as one platform — the list describes scope, not a menu",
  head: ["Capability", "What it does", "Primary audience"],
  rows: [
    ["Grounded answering", "Plain-language answers assembled only from approved sources, never from general world knowledge.", "Everyone"],
    ["Verbatim citation and lineage", "Each claim carries its source, down to document, page and paragraph.", "Quality, audit, legal"],
    ["Confidence scoring", "A visible high / medium / low level on every answer, derived from evidence strength.", "Everyone"],
    ["Clarify-back", "One targeted question when evidence is thin, instead of a refusal or a guess.", "Everyone"],
    ["Entity and relationship graph", "Explore how products, processes, regulations and records connect to one another.", "Engineering, quality"],
    ["Knowledge health", "Coverage, connectivity, provenance, extraction quality and freshness, with gaps ranked.", "Content owners"],
    ["Version and status awareness", "Current revisions outrank superseded ones; draft material is excluded unless requested.", "Quality, operations"],
    ["Multilingual answering", "Ask and answer in the user's language; translated material is labelled as translated.", "Global operations"],
    ["Curator workbench", "A human queue for conflicts, duplicates and superseded documents.", "Content owners"],
    ["Role-scoped access", "Permissions applied before ranking, so unauthorised content never enters a result.", "Security, IT"],
    ["Usage and quality dashboards", "Consumption, question categories, clarification and refusal rates over time.", "Sponsors, IT"],
    ["APIs and embedding", "The answer flow exposed to other applications and portals through a governed interface.", "IT, product teams"]]},

/* 8 */ {kind: "cards6", nav: "What it covers",
  title: "What the platform covers",
  sub: "Coverage is broad because the questions people ask do not respect system boundaries",
  items: [
    {h: "Document formats", hue: "blue",
     p: "Text and scanned documents, office formats, presentations, spreadsheets, structured exports and web content. Scanned material is processed so its text becomes searchable and citable."},
    {h: "Source systems", hue: "emerald",
     p: "Document management and quality systems, engineering and product lifecycle systems, ticketing and service desks, wikis and intranets, shared drives, and regulatory or public registries."},
    {h: "Content types", hue: "indigo",
     p: "Standard operating procedures, work instructions, policies, specifications, manuals, validation and test records, audit findings, contracts, correspondence and training material."},
    {h: "Business functions", hue: "amber",
     p: "Quality and compliance, engineering and manufacturing, service and support, operations, procurement, legal, and people functions."},
    {h: "Languages", hue: "violet",
     p: "Multilingual corpora and multilingual users, with the answer returned in the language of the question and any translated passage labelled."},
    {h: "Question shapes", hue: "slate",
     p: "Factual lookup, procedural how-to, comparison across documents, status and version checks, and relationship questions across entities."}]},

/* 9 */ {kind: "value", nav: "Value",
  title: "Value delivered",
  sub: "What each group gets — stated without reference to commercial figures",
  items: [
    {h: "Frontline and operations", hue: "blue", li: [
      "The current, approved answer arrives in seconds instead of after a search through revisions.",
      "The same question gets the same answer across sites, shifts and languages.",
      "New joiners become productive without a colleague acting as their search index."]},
    {h: "Quality, compliance and audit", hue: "indigo", li: [
      "Every answer can be reconstructed to the document, page and paragraph it came from.",
      "Superseded revisions stop circulating as if they were current.",
      "The refusal and clarification record shows exactly where documented knowledge is thin."]},
    {h: "Engineering and technical teams", hue: "emerald", li: [
      "Relationships between products, processes, regulations and records become explorable rather than tribal.",
      "Prior work, decisions and test evidence surface at the moment they are relevant.",
      "Time spent reconstructing context is returned to engineering work."]},
    {h: "Leadership and sponsors", hue: "violet", li: [
      "Institutional memory becomes an asset the organisation holds rather than one its people carry.",
      "Consumption and quality are visible, so the platform can be governed on evidence.",
      "Knowledge gaps arrive as a ranked backlog, turning content investment into a prioritised plan."]},
    {h: "IT and security", hue: "slate", li: [
      "Identity, permissions and network controls are the ones the organisation already operates.",
      "Content stays inside the customer's boundary; residency and retention follow existing policy.",
      "No component is a lock-in: model, vector store and cloud are all substitutable."]}]},

/* 10 */ {kind: "deploy", nav: "Deployment",
  title: "Deployment and portability",
  sub: "A platform pattern, not a bet on a single vendor",
  pluggableLabel: "Pluggable by design",
  pluggable: [
    {h: "Identity provider", p: "Whatever the organisation already runs for single sign-on."},
    {h: "Embedding model",   p: "Commercial or self-hosted, selected for language coverage and residency."},
    {h: "Vector store",      p: "Managed or in-tenant, selected to match the existing data platform."},
    {h: "Language model",    p: "Commercial API, in-tenant deployment or self-hosted, per the control environment."}],
  modesLabel: "Deployment modes",
  modes: [
    {h: "Managed service", hue: "blue",
     p: "Fastest to stand up. Suited to pilots and to content that is not restricted."},
    {h: "In-tenant deployment", hue: "indigo",
     p: "Runs inside the customer's own cloud account and network boundary. The common production choice."},
    {h: "Restricted or disconnected", hue: "slate",
     p: "Self-hosted models with no external calls, for the most tightly controlled environments."}],
  foot: "If the customer changes cloud, identity provider or model, the pattern survives and the delivered work is not discarded."},

/* 11 */ {kind: "phases", nav: "Delivery",
  title: "Delivery approach",
  sub: "Each phase ends with something the organisation can evaluate on its own terms",
  items: [
    {n: "Phase 1", h: "Discover", dur: "Weeks", hue: "blue",
     p: "Corpus assessment and use-case selection. We inventory the candidate content, test how well it is structured, identify the questions that matter most, and agree what a good answer looks like.",
     out: "Content readiness assessment, prioritised question set, target architecture."},
    {n: "Phase 2", h: "Prove", dur: "Weeks", hue: "emerald",
     p: "A working pilot on one domain and one audience, with real content and real users. The ontology, filters and thresholds are tuned against the prioritised question set.",
     out: "Working platform on live content, measured answer quality, curator workflow in use."},
    {n: "Phase 3", h: "Harden", dur: "Weeks", hue: "indigo",
     p: "Production readiness: identity integration, permission mapping, security review, telemetry and dashboards, operational runbooks and release automation.",
     out: "Production deployment inside the customer's control environment, with governance in place."},
    {n: "Phase 4", h: "Extend", dur: "Ongoing", hue: "violet",
     p: "Additional domains, languages and audiences, driven by the ranked gap backlog the platform itself produces. Continuous curation replaces one-off content projects.",
     out: "Expanding coverage, improving health scores, a content plan grounded in real demand."}]},

/* 12 */ {kind: "diff", nav: "Difference",
  title: "What makes this different",
  items: [
    {h: "Generation is gated, not trusted", hue: "amber",
     p: "The grounding check runs before anything is written. Citation is a property of the design, not a promise about behaviour."},
    {h: "Clarification instead of refusal", hue: "blue",
     p: "Thin evidence produces a targeted question and a second attempt, recovering answers that a refusal would have discarded."},
    {h: "Permissions applied before ranking", hue: "indigo",
     p: "Unauthorised content never enters the candidate set, so it cannot shape a result or be inferred from one."},
    {h: "The system reports its own gaps", hue: "violet",
     p: "Failed and clarified questions become a ranked content backlog, so the corpus improves from real demand."},
    {h: "Portable by construction", hue: "emerald",
     p: "Model, vector store, embedding and identity are all deployment choices; none of them is the product."}]}
];


/* ------------------------------------------------------------------ render */

const HUE = {blue: "--blue", indigo: "--indigo", emerald: "--emerald",
             amber: "--amber", violet: "--violet", slate: "--slate"};

const esc = s => String(s).replace(/[&<>]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
const hue = h => `var(${HUE[h] || "--blue"})`;
const tint = h => `var(${(HUE[h] || "--blue")}-t)`;

function chrome(s, n) {
  if (s.kind === "title") return "";
  return `<header class="s-head">
      <h2>${esc(s.title)}</h2>
      ${s.sub ? `<p class="s-sub">${esc(s.sub)}</p>` : ""}
    </header>`;
}

function body(s) {
  switch (s.kind) {

  case "title":
    return `<div class="title-slide">
      <div class="t-rule"></div>
      <div class="eyebrow">${esc(s.eyebrow)}</div>
      <h1>${esc(s.title)}</h1>
      <p class="t-sub">${esc(s.sub)}</p>
      <p class="t-lede">${esc(s.lede)}</p>
      <div class="t-by">${esc(s.by)}</div>
    </div>`;

  case "cards4":
    return `<div class="g4">${s.items.map((c, i) => `
      <div class="card" style="--h:${hue(c.hue)};--t:${tint(c.hue)};--i:${i}">
        <span class="num">${i + 1}</span>
        <h3>${esc(c.h)}</h3>
        <p>${esc(c.p)}</p>
      </div>`).join("")}</div>`;

  case "problem":
    return `<div class="prob-wrap">
      <div>
        <div class="mini-label">${esc(s.label)}</div>
        <ol class="probs">${s.items.map((c, i) => `
          <li style="--i:${i}"><span class="pn">${i + 1}</span>
            <div><h3>${esc(c.h)}</h3><p>${esc(c.p)}</p></div></li>`).join("")}</ol>
      </div>
      <aside class="pull" style="--i:5">
        ${s.quote.map(q => `<p class="q">${esc(q)}</p>`).join("")}
        <p class="qb">${esc(s.quoteBody)}</p>
      </aside>
    </div>
    <p class="s-foot">${esc(s.foot)}</p>`;

  case "flow":
    return `<div class="flow">${s.steps.map((c, i) => `
      <div class="step${c.gate ? " gate" : ""}" style="--h:${hue(c.hue)};--t:${tint(c.hue)};--i:${i}">
        <span class="sn">${i + 1}</span>
        <h3>${esc(c.h)}</h3><p>${esc(c.p)}</p>
        ${c.gate ? `<span class="gate-tag">gate</span>` : ""}
      </div>`).join("")}</div>
    <div class="band" style="--i:6">
      <div class="band-head"><span>${esc(s.bandLabel)}</span><i>${esc(s.bandSub)}</i></div>
      <div class="band-body">${s.band.map(c => `
        <div><h4>${esc(c.h)}</h4><p>${esc(c.p)}</p></div>`).join("")}</div>
    </div>`;

  case "archlive":
    return `<div class="archlive">
      <div class="archlive-scene" data-archscene></div>
      <p class="archlive-note">Static full-resolution diagram for print and proposals:
        <a href="${s.full}" target="_blank" rel="noopener">3800&nbsp;px JPEG</a></p>
    </div>`;

  case "figure":
    return `<figure class="fig">
      <img src="${s.src}" alt="${esc(s.alt)}" loading="eager" decoding="async">
      <figcaption>Open the full-resolution diagram:
        <a href="${s.full}" target="_blank" rel="noopener">3800&nbsp;px JPEG</a></figcaption>
    </figure>`;

  case "zones":
    return `<div class="zones">${s.items.map((c, i) => `
      <div class="zone" style="--h:${hue(c.hue)};--t:${tint(c.hue)};--i:${i}">
        <div class="z-head"><h3>${esc(c.h)}</h3><i>${esc(c.t)}</i></div>
        <div class="chips">${c.chips.map(x => `<span>${esc(x)}</span>`).join("")}</div>
      </div>`).join("")}</div>
    <p class="loop-note">${esc(s.loop)}</p>`;

  case "table":
    return `<div class="tbl-wrap" style="--i:0"><table class="tbl">
      <thead><tr>${s.head.map(h => `<th>${esc(h)}</th>`).join("")}</tr></thead>
      <tbody>${s.rows.map(r => `<tr>
        <td class="c1">${esc(r[0])}</td><td>${esc(r[1])}</td>
        <td class="c3">${esc(r[2])}</td></tr>`).join("")}</tbody>
    </table></div>`;

  case "cards6":
    return `<div class="g6">${s.items.map((c, i) => `
      <div class="card" style="--h:${hue(c.hue)};--t:${tint(c.hue)};--i:${i}">
        <h3>${esc(c.h)}</h3><p>${esc(c.p)}</p>
      </div>`).join("")}</div>`;

  case "value":
    return `<div class="g5">${s.items.map((c, i) => `
      <div class="vcol" style="--h:${hue(c.hue)};--t:${tint(c.hue)};--i:${i}">
        <h3>${esc(c.h)}</h3>
        <ul>${c.li.map(x => `<li>${esc(x)}</li>`).join("")}</ul>
      </div>`).join("")}</div>`;

  case "deploy":
    return `<div class="deploy">
      <div>
        <div class="mini-label">${esc(s.pluggableLabel)}</div>
        <div class="plug">${s.pluggable.map((c, i) => `
          <div style="--i:${i}"><h4>${esc(c.h)}</h4><p>${esc(c.p)}</p></div>`).join("")}</div>
      </div>
      <div>
        <div class="mini-label">${esc(s.modesLabel)}</div>
        <div class="modes">${s.modes.map((c, i) => `
          <div style="--h:${hue(c.hue)};--t:${tint(c.hue)};--i:${i + 4}">
            <span class="mn">${i + 1}</span>
            <h4>${esc(c.h)}</h4><p>${esc(c.p)}</p></div>`).join("")}</div>
      </div>
    </div>
    <p class="s-foot">${esc(s.foot)}</p>`;

  case "phases":
    return `<div class="phases">${s.items.map((c, i) => `
      <div class="phase" style="--h:${hue(c.hue)};--t:${tint(c.hue)};--i:${i}">
        <div class="p-top"><span class="p-n">${esc(c.n)}</span><span class="p-d">${esc(c.dur)}</span></div>
        <h3>${esc(c.h)}</h3>
        <p>${esc(c.p)}</p>
        <div class="p-out"><span>Leaves behind</span>${esc(c.out)}</div>
      </div>`).join("")}</div>`;

  case "diff":
    return `<div class="diffs">${s.items.map((c, i) => `
      <div class="diff" style="--h:${hue(c.hue)};--t:${tint(c.hue)};--i:${i}">
        <span class="dn">${i + 1}</span>
        <div><h3>${esc(c.h)}</h3><p>${esc(c.p)}</p></div>
      </div>`).join("")}</div>`;

  default:
    return "";
  }
}

const deck = document.getElementById("deck");
const total = SLIDES.length;

deck.innerHTML = SLIDES.map((s, i) => `
  <section class="slide${s.kind === "title" ? " is-title" : ""}"
           id="s${i + 1}" data-i="${i + 1}" aria-label="Slide ${i + 1} of ${total}">
    <div class="stage">
      ${chrome(s, i + 1)}
      <div class="s-body">${body(s)}</div>
      ${s.kind === "title" ? "" : `<footer class="s-foot-bar">
        <span class="fb-brand">Knowledge Fabric · QualiZeal AI Center of Excellence</span>
        <span class="fb-n">${i + 1}</span></footer>`}
    </div>
  </section>`).join("");

const slides = [...deck.querySelectorAll(".slide")];

/* ------------------------------------------------------------------- scale */
/* Every slide is laid out on a fixed 1280x720 canvas and scaled to fit, so a
   projector, a laptop and a print sheet all get identical geometry. */

function fit() {
  const pad = window.innerWidth < 760 ? 8 : 46;
  const k = Math.min((window.innerWidth - pad * 2) / 1280,
                     (window.innerHeight - pad * 2 - 44) / 720);
  document.documentElement.style.setProperty("--k", Math.max(k, 0.12));
}
addEventListener("resize", fit);
fit();

/* -------------------------------------------------------------- navigation */

let cur = 1;
const bar   = document.getElementById("bar");
const nowEl = document.getElementById("now");
const grid  = document.getElementById("grid");

function go(n, push) {
  cur = Math.min(Math.max(n, 1), total);
  slides.forEach(s => s.classList.toggle("on", +s.dataset.i === cur));
  bar.style.transform = `scaleX(${cur / total})`;
  nowEl.textContent = cur;
  [...grid.children].forEach(c => c.classList.toggle("on", +c.dataset.i === cur));
  if (push !== false) history.replaceState(null, "", "#" + cur);
}

function toggleGrid(force) {
  const open = force !== undefined ? force : !document.body.classList.contains("grid-on");
  document.body.classList.toggle("grid-on", open);
  document.getElementById("gridBtn").setAttribute("aria-expanded", String(open));
}

/* Overview: real slides, scaled down. Cheap at twelve, and a presenter
   recognises the slide they want by its shape, not by its title. */
grid.innerHTML = SLIDES.map((s, i) => `
  <button class="thumb" data-i="${i + 1}" title="${esc(s.title)}">
    <span class="t-frame"></span>
    <span class="t-meta"><b>${i + 1}</b> ${esc(s.nav || s.title)}</span>
  </button>`).join("");

[...grid.children].forEach((btn, i) => {
  const frame = btn.querySelector(".t-frame");
  const clone = slides[i].querySelector(".stage").cloneNode(true);
  clone.classList.add("thumb-stage");
  clone.querySelectorAll("img").forEach(im => im.loading = "lazy");
  frame.appendChild(clone);
  btn.addEventListener("click", () => { go(i + 1); toggleGrid(false); });
});

document.getElementById("prev").addEventListener("click", () => go(cur - 1));
document.getElementById("next").addEventListener("click", () => go(cur + 1));
document.getElementById("gridBtn").addEventListener("click", () => toggleGrid());
document.getElementById("fsBtn").addEventListener("click", () => {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen?.();
});

addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key;
  if (k === "ArrowRight" || k === "PageDown" || k === " " || k === "Enter") { e.preventDefault(); go(cur + 1); }
  else if (k === "ArrowLeft" || k === "PageUp" || k === "Backspace")        { e.preventDefault(); go(cur - 1); }
  else if (k === "Home") { e.preventDefault(); go(1); }
  else if (k === "End")  { e.preventDefault(); go(total); }
  else if (k === "g" || k === "G") { e.preventDefault(); toggleGrid(); }
  else if (k === "Escape") toggleGrid(false);
  else if (k === "f" || k === "F") document.getElementById("fsBtn").click();
});

/* Touch: swipe left/right. Vertical drags are left to the browser. */
let x0 = null, y0 = null;
deck.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, {passive: true});
deck.addEventListener("touchend", e => {
  if (x0 === null) return;
  const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
  if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.6) go(cur + (dx < 0 ? 1 : -1));
  x0 = y0 = null;
}, {passive: true});

addEventListener("hashchange", () => go(+location.hash.slice(1) || 1, false));

document.getElementById("count").textContent = total;
go(+location.hash.slice(1) || 1, false);
