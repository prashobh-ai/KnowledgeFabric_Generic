/* Configurator behaviour: a four-step questionnaire whose result — the
 * architecture drawing, the ship list, the limitations — is composed entirely
 * from rules.js. Selections live in the URL hash, so a filled-in result is a
 * link a salesperson can send.
 */
"use strict";

const ORDER = ["domain", "infra", "model", "scope"];
const TITLES = { domain: "Domain", infra: "Infrastructure", model: "Models", scope: "Scope" };
const sel = {};

function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}

/* ------------------------------------------------------------- options */
function optionCards() {
  const d = document.getElementById("opt-domain");
  d.innerHTML = DOMAINS.map(x =>
    `<button class="opt" data-v="${x.id}"><b>${esc(x.label)}</b></button>`).join("");
  const i = document.getElementById("opt-infra");
  i.innerHTML = Object.entries(INFRA).map(([k, v]) =>
    `<button class="opt" data-v="${k}"><b>${esc(v.label)}</b><span>${esc(v.boundary)}</span></button>`).join("");
  const m = document.getElementById("opt-model");
  m.innerHTML = Object.entries(MODELS).map(([k, v]) =>
    `<button class="opt" data-v="${k}"><b>${esc(v.label)}</b><span>${esc(v.plane)}</span></button>`).join("");
  const s = document.getElementById("opt-scope");
  s.innerHTML = Object.entries(SCOPES).map(([k, v]) =>
    `<button class="opt" data-v="${k}"><b>${esc(v.label)}</b><span>${esc(v.includes[v.includes.length-1])}</span></button>`).join("");
}

/* ------------------------------------------------------------- stepper */
function show(idx) {
  document.querySelectorAll(".q").forEach((q, i) =>
    q.classList.toggle("on", i === idx && idx < ORDER.length));
  document.getElementById("result").classList.toggle("on", idx >= ORDER.length);
  const dots = document.getElementById("stepdots");
  dots.innerHTML = ORDER.map((k, i) => {
    const cls = i === idx ? "stepdot on" : (sel[k] ? "stepdot done" : "stepdot");
    return `<span class="${cls}">${i + 1} · ${TITLES[k]}${sel[k] ? " ✓" : ""}</span>`;
  }).join("") + (idx >= ORDER.length ? `<span class="stepdot on">Your fabric</span>` : "");
  if (idx >= ORDER.length) renderResult();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function writeHash() {
  const h = ORDER.filter(k => sel[k]).map(k => `${k}=${sel[k]}`).join("&");
  history.replaceState(null, "", h ? "#" + h : location.pathname);
}

function readHash() {
  const p = new URLSearchParams(location.hash.slice(1));
  ORDER.forEach(k => { const v = p.get(k); if (v) sel[k] = v; });
}

document.addEventListener("click", e => {
  const opt = e.target.closest(".opt");
  if (opt) {
    const q = opt.closest(".q").dataset.q;
    sel[q] = opt.dataset.v;
    opt.parentElement.querySelectorAll(".opt").forEach(o => o.classList.remove("picked"));
    opt.classList.add("picked");
    writeHash();
    setTimeout(() => show(ORDER.indexOf(q) + 1), 220);
  }
  if (e.target.closest("[data-back]")) {
    const q = e.target.closest(".q").dataset.q;
    show(ORDER.indexOf(q) - 1);
  }
  if (e.target.closest("[data-restart]")) {
    ORDER.forEach(k => delete sel[k]);
    document.querySelectorAll(".opt").forEach(o => o.classList.remove("picked"));
    writeHash(); show(0);
  }
  if (e.target.closest("[data-print]")) window.print();
  if (e.target.closest("[data-share]")) {
    navigator.clipboard && navigator.clipboard.writeText(location.href).then(() => {
      const b = e.target.closest("[data-share]");
      const t = b.textContent; b.textContent = "Link copied";
      setTimeout(() => { b.textContent = t; }, 1600);
    });
  }
});

/* -------------------------------------------------- architecture SVG */
function zone(x, y, w, h, hue, tint, label, sub, rows, dim) {
  const row = (r, i) =>
    `<g transform="translate(${x + 14},${y + 64 + i * 30})">
       <rect width="${w - 28}" height="24" rx="6" fill="${dim ? "#F4F6F8" : tint}"/>
       <text x="10" y="16" font-family="JetBrains Mono,monospace" font-size="10.5"
             fill="${dim ? "#93A6B8" : "#22374D"}">${esc(r)}</text></g>`;
  return `<g ${dim ? 'opacity=".55"' : ""}>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="12" fill="#fff" stroke="#DFE7EE"/>
    <rect x="${x}" y="${y}" width="${w}" height="5" rx="2.5" fill="${hue}"/>
    <text x="${x + 14}" y="${y + 28}" font-family="JetBrains Mono,monospace" font-size="11"
          letter-spacing="1.5" fill="${hue}">${esc(label)}</text>
    <text x="${x + 14}" y="${y + 45}" font-family="Inter,sans-serif" font-size="10.5"
          fill="#93A6B8">${esc(sub)}</text>
    ${rows.map(row).join("")}
    ${dim ? `<text x="${x + w - 14}" y="${y + 28}" text-anchor="end"
        font-family="JetBrains Mono,monospace" font-size="9.5" fill="#93A6B8">LATER PHASE</text>` : ""}
  </g>`;
}

function archSVG(r) {
  const tele = r.sel.scope === "governed" || r.sel.scope === "full";
  const graph = r.sel.scope !== "core";
  const centerRows = [
    "Hybrid retrieval (lexical + semantic)",
    "Grounding gate — evidence before writing",
    r.sel.model === "none" ? "Verbatim answer composer (extractive)" : "Grounded generation + clarify-back",
    graph ? "Entity graph & knowledge health" : "Citations & confidence",
  ];
  const teleRows = tele
    ? ["Per-answer scoring & tracing", "Curator workbench + dashboards", "Model routing & caps (admin)"]
    : ["Per-answer scoring & tracing", "Curator dashboards", "Model governance"];
  return `<svg viewBox="0 0 980 560" role="img" aria-label="Proposed architecture">
    <rect x="10" y="10" width="960" height="76" rx="12" fill="#EEF0FF" stroke="#D6DAFB"/>
    <text x="26" y="40" font-family="JetBrains Mono,monospace" font-size="11" letter-spacing="1.5"
          fill="#4338CA">ACCESS AND ROLES</text>
    <text x="26" y="60" font-family="Inter,sans-serif" font-size="11.5" fill="#22374D">${esc(r.infra.identity)}</text>
    <text x="954" y="40" text-anchor="end" font-family="Inter,sans-serif" font-size="10.5"
          fill="#6A7F94">permissions applied before anything is searched</text>

    ${zone(10, 108, 296, 210, "#047857", "#E7F8F1", "CONTENT PIPELINE", "your sources, your cadence",
      [r.infra.intake, "Extract · rank · OCR", "Curator resolve queue", r.infra.search], false)}

    ${zone(326, 108, 330, 210, "#0086E6", "#E8F5FF", "GROUNDED ANSWERING",
      r.model.planeShort, centerRows, false)}

    ${zone(676, 108, 294, 210, "#9333EA", "#F8EDFE", "TRUST AND TELEMETRY",
      tele ? "proof that it worked" : "available in the governed tier", teleRows, !tele)}

    <path d="M306 213 h20 M656 213 h20" stroke="#C9D6E2" stroke-width="2"/>
    <path d="M318 207 l8 6 l-8 6 M668 207 l8 6 l-8 6" stroke="#C9D6E2" stroke-width="2" fill="none"/>

    <rect x="10" y="342" width="960" height="60" rx="12" fill="#EEF1F5" stroke="#DCE2EA"/>
    <text x="26" y="368" font-family="JetBrains Mono,monospace" font-size="11" letter-spacing="1.5"
          fill="#344054">SECURITY AND OPERATIONS</text>
    <text x="26" y="386" font-family="Inter,sans-serif" font-size="11" fill="#475467">${esc(r.infra.runtime)} · ${esc(r.infra.secrets)}</text>

    <rect x="10" y="426" width="960" height="54" rx="12" fill="none" stroke="#94A3B8" stroke-dasharray="7 6"/>
    <text x="490" y="458" text-anchor="middle" font-family="Inter,sans-serif" font-size="13"
          fill="#475467">Everything above runs ${esc(r.infra.boundary)} — identity, network, keys and content stay with you.</text>

    ${tele ? `<path d="M823 322 V500 Q823 512 811 512 H172 Q160 512 160 500 V322"
        stroke="#9333EA" stroke-width="2" stroke-dasharray="4 7" fill="none"/>
      <path d="M154 334 l6 -10 l6 10" fill="none" stroke="#9333EA" stroke-width="2"/>
      <text x="490" y="536" text-anchor="middle" font-family="Inter,sans-serif" font-size="11.5"
        fill="#9333EA">questions the corpus cannot answer return as a ranked content backlog</text>` : ""}
  </svg>`;
}

/* ------------------------------------------------------------- result */
function renderResult() {
  const r = resolve(sel);
  const el = document.getElementById("result");
  el.innerHTML = `
    <div class="eyebrow">Your proposed fabric</div>
    <div class="r-head">
      <h2>${esc(r.domain.label)}, running on ${esc(r.infra.label)}.</h2>
      <div class="badges">
        <span class="badge">${esc(r.model.badge)}</span>
        <span class="badge">${esc(r.scope.label)}</span>
      </div>
    </div>

    ${r.adjustments.length ? `<div class="card adjust" style="margin-top:16px">
      <h3>We adjusted one answer — here is why</h3>
      <ul class="klist">${r.adjustments.map(a => `<li>${esc(a)}</li>`).join("")}</ul>
    </div>` : ""}

    <div class="r-grid">
      <div>
        <div class="arch-svg">${archSVG(r)}</div>
        <div class="card" style="margin-top:18px">
          <h3>What ships in this release</h3>
          <ul class="klist">${r.scope.includes.map(x => `<li>${esc(x)}</li>`).join("")}</ul>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:18px">
        <div class="card limits">
          <h3><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2.2" stroke-linecap="round"><path d="M12 3 L22 20 H2 Z"/><path d="M12 10v4M12 17.5v.5"/></svg>
            The limitations, out loud</h3>
          <ul class="klist">${r.limits.map(x => `<li>${esc(x)}</li>`).join("")}</ul>
        </div>
        <div class="card proof">
          <h3>We have built this before</h3>
          <p class="built">For ${esc(r.domain.label.toLowerCase())}, we have shown ${esc(r.domain.built)}.</p>
          <a class="demo-btn" href="../demo/${esc(r.domain.demo)}/">
            Open the ${esc(r.domain.label)} demonstration
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="2.4" stroke-linecap="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg></a>
          <p class="syn">The demonstration runs on a fully synthetic corpus — real standards,
            invented content — ${r.sel.model === "none"
              ? "and answers in exactly the extractive mode proposed above."
              : "with every answer quoted verbatim and cited to its paragraph."}</p>
        </div>
        <div class="card">
          <h3>How we would deliver it</h3>
          <div class="phases">${r.phases.map(p =>
            `<div class="phase"><b>${esc(p[0])}</b><span>${esc(p[1])}</span></div>`).join("")}</div>
        </div>
      </div>
    </div>

    <div class="r-actions">
      <button class="ghost" data-restart>Start again</button>
      <button class="ghost" data-share>Copy link to this result</button>
      <button class="ghost" data-print>Print / save as PDF</button>
      <a class="ghost" style="text-decoration:none" href="../downloads/Knowledge-Fabric-Capability-Overview.docx" download>Capability overview (.docx)</a>
    </div>`;
}

/* ------------------------------------------------------------- boot */
optionCards();
readHash();
document.querySelectorAll(".q").forEach(q => {
  const k = q.dataset.q;
  if (sel[k]) {
    const o = q.querySelector(`.opt[data-v="${sel[k]}"]`);
    if (o) o.classList.add("picked");
  }
});
function syncFromHash() {
  ORDER.forEach(k => delete sel[k]);
  readHash();
  document.querySelectorAll(".q").forEach(q => {
    const k = q.dataset.q;
    q.querySelectorAll(".opt").forEach(o =>
      o.classList.toggle("picked", sel[k] === o.dataset.v));
  });
  const first = ORDER.findIndex(k => !sel[k]);
  show(first === -1 ? ORDER.length : first);
}
window.addEventListener("hashchange", syncFromHash);
const firstUnanswered = ORDER.findIndex(k => !sel[k]);
show(firstUnanswered === -1 ? ORDER.length : firstUnanswered);
