/* Configurator behaviour: an eight-step questionnaire whose result — the
 * architecture drawing with the vendors' own marks, the ship list, the
 * limitations — is composed entirely from rules.js. Selections live in the
 * URL hash, so a filled-in result is a link a salesperson can send.
 */
"use strict";

const ORDER = ["domain", "infra", "identity", "model", "vector", "roles", "obs", "scope"];
const TITLES = { domain: "Domain", infra: "Cloud", identity: "Sign-in", model: "Models",
                 vector: "Index", roles: "Roles", obs: "Telemetry", scope: "Scope" };
const ADAPTIVE = ["identity", "model", "vector", "obs"];   // labels follow the chosen cloud
const sel = {};
let tempRoles = new Set(["reader"]);
let lastR = null;

function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}

/* --------------------------------------------------------------- logos */
const LOGO_NAMES = ["aws","azure","azureai","bedrock","claude","datadog","gcp","grafana",
  "huggingface","keycloak","kubernetes","mistral","okta","ollama","openai","opensearch",
  "opentelemetry","pinecone","postgresql","python","redis","vertexai"];
const LOGOS = {};

function loadLogos() {
  return Promise.all(LOGO_NAMES.map(n =>
    fetch(`../assets/logos/${n}.svg`)
      .then(r => r.ok ? r.text() : "")
      .then(t => { const i = t.indexOf("<svg"); if (i >= 0) LOGOS[n] = t.slice(i); })
      .catch(() => {})));
}

/* Nest a vendored logo inside the architecture SVG. The vendored files keep
   their own fills; width/height/style on the opening tag are replaced so the
   viewBox scales it, and `color` feeds any fill="currentColor" mark. */
function logoTag(name, x, y, s, color) {
  const raw = LOGOS[name];
  if (!raw) return "";
  return raw.replace(/^<svg[^>]*>/, m => {
    const open = m.replace(/\s(?:width|height|style)="[^"]*"/g, "");
    return open.replace("<svg",
      `<svg x="${x}" y="${y}" width="${s}" height="${s}" style="color:${color || "#22374D"}"`);
  });
}

function imgs(logos, size) {
  return (logos || []).map(n =>
    `<img src="../assets/logos/${n}.svg" alt="" width="${size||18}" height="${size||18}" loading="lazy">`).join("");
}

/* ------------------------------------------------------------- options */
function card(v, entry, extra) {
  const logos = entry.logos || (entry.logo ? [entry.logo] : []);
  return `<button class="opt${extra || ""}" data-v="${v}">
    <span class="opt-top">${imgs(logos)}<b>${esc(entry.label)}</b></span>
    ${entry.sub ? `<span>${esc(entry.sub)}</span>` : ""}</button>`;
}

function optionCards() {
  document.getElementById("opt-domain").innerHTML = DOMAINS.map(x =>
    `<button class="opt" data-v="${x.id}"><b>${esc(x.label)}</b></button>`).join("");
  document.getElementById("opt-infra").innerHTML = Object.entries(INFRA).map(([k, v]) =>
    card(k, { label: v.label, sub: v.boundary, logo: v.logo })).join("");
  document.getElementById("opt-scope").innerHTML = Object.entries(SCOPES).map(([k, v]) =>
    card(k, { label: v.label, sub: v.includes[v.includes.length - 1] })).join("");
  document.getElementById("opt-roles").innerHTML = ROLE_ORDER.map(k => {
    const r = ROLES[k];
    return `<button class="opt${r.locked ? " locked picked" : ""}" data-v="${k}">
      <span class="opt-top"><b>${esc(r.label)}</b>${r.locked ? '<span class="always">always in</span>' : ""}</span>
      <span>${esc(r.sub)}</span></button>`;
  }).join("");
  renderAdaptiveGrids();
}

function renderAdaptiveGrids() {
  const tables = { identity: IDENTITY, model: MODELS, vector: VECTOR, obs: OBS };
  for (const q of ADAPTIVE) {
    const t = tables[q];
    document.getElementById("opt-" + q).innerHTML = Object.keys(t).map(k =>
      card(k, adapt(t, k, sel.infra))).join("");
  }
  applyPicked();
}

function applyPicked() {
  document.querySelectorAll(".q").forEach(qEl => {
    const q = qEl.dataset.q;
    qEl.querySelectorAll(".opt").forEach(o => {
      const locked = o.classList.contains("locked");
      const on = q === "roles" ? (locked || tempRoles.has(o.dataset.v)) : sel[q] === o.dataset.v;
      o.classList.toggle("picked", on);
    });
  });
}

/* ------------------------------------------------------------- stepper */
function show(idx) {
  document.querySelectorAll(".q").forEach((q, i) =>
    q.classList.toggle("on", i === idx && idx < ORDER.length));
  document.getElementById("result").classList.toggle("on", idx >= ORDER.length);
  const dots = document.getElementById("stepdots");
  dots.innerHTML = ORDER.map((k, i) => {
    const cls = i === idx ? "stepdot on" : (sel[k] ? "stepdot done" : "stepdot");
    return `<span class="${cls}">${TITLES[k]}${sel[k] ? " ✓" : ""}</span>`;
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
  ORDER.forEach(k => {
    const v = p.get(k);
    if (!v) return;
    if (k === "roles") {
      const rs = v.split(".").filter(r => ROLES[r]);
      if (rs.length) { if (!rs.includes("reader")) rs.unshift("reader"); sel.roles = rs.join("."); }
    } else sel[k] = v;
  });
  tempRoles = new Set(sel.roles ? sel.roles.split(".") : ["reader"]);
}

document.addEventListener("click", e => {
  const opt = e.target.closest(".opt");
  if (opt) {
    const qEl = opt.closest(".q"), q = qEl.dataset.q;
    if (qEl.hasAttribute("data-multi")) {
      const v = opt.dataset.v;
      if (!opt.classList.contains("locked")) {
        if (tempRoles.has(v)) tempRoles.delete(v); else tempRoles.add(v);
        opt.classList.toggle("picked", tempRoles.has(v));
      }
      return;                                   // multi-select: Continue advances
    }
    sel[q] = opt.dataset.v;
    qEl.querySelectorAll(".opt").forEach(o => o.classList.remove("picked"));
    opt.classList.add("picked");
    if (q === "infra") renderAdaptiveGrids();   // downstream labels follow the cloud
    writeHash();
    setTimeout(() => show(ORDER.indexOf(q) + 1), 220);
  }
  if (e.target.closest("[data-next]")) {
    const q = e.target.closest(".q").dataset.q;
    if (q === "roles")
      sel.roles = ROLE_ORDER.filter(r => tempRoles.has(r) || ROLES[r].locked).join(".");
    writeHash();
    show(ORDER.indexOf(q) + 1);
  }
  if (e.target.closest("[data-back]")) {
    const q = e.target.closest(".q").dataset.q;
    show(ORDER.indexOf(q) - 1);
  }
  if (e.target.closest("[data-restart]")) {
    ORDER.forEach(k => delete sel[k]);
    tempRoles = new Set(["reader"]);
    applyPicked(); writeHash(); show(0);
  }
  if (e.target.closest("[data-print]")) window.print();
  if (e.target.closest("[data-share]")) {
    navigator.clipboard && navigator.clipboard.writeText(location.href).then(() => {
      const b = e.target.closest("[data-share]");
      const t = b.textContent; b.textContent = "Link copied";
      setTimeout(() => { b.textContent = t; }, 1600);
    });
  }
  if (e.target.closest("[data-dl-svg]") && lastR) {
    saveFile(archSVG(lastR), "image/svg+xml",
      `Knowledge-Fabric-Architecture-${lastR.domain.demo}.svg`);
  }
  if (e.target.closest("[data-dl-proposal]") && lastR) {
    saveFile(proposalText(lastR), "text/plain;charset=utf-8",
      `Knowledge-Fabric-Proposal-${lastR.domain.demo}.txt`);
  }
});

function saveFile(content, type, name) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], { type }));
  a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

/* -------------------------------------------------- architecture SVG */
function zone(x, y, w, h, hue, tint, label, sub, rows, dim) {
  const row = (r, i) => {
    const t = typeof r === "string" ? { t: r } : r;
    const logos = (t.logos || (t.logo ? [t.logo] : [])).filter(n => LOGOS[n]);
    const tx = 8 + logos.length * 22 + (logos.length ? 6 : 2);
    return `<g transform="translate(${x + 14},${y + 64 + i * 30})">
       <rect width="${w - 28}" height="24" rx="6" fill="${dim ? "#F4F6F8" : tint}"/>
       ${logos.map((n, j) => logoTag(n, 8 + j * 22, 4, 16, dim ? "#93A6B8" : "#22374D")).join("")}
       <text x="${tx}" y="16" font-family="JetBrains Mono,monospace" font-size="10.5"
             fill="${dim ? "#93A6B8" : "#22374D"}">${esc(t.t)}</text></g>`;
  };
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
  const extraRoles = r.roles.filter(x => x.ws);

  const pipelineRows = [
    r.infra.intake,
    "Extract · rank · OCR",
    r.sel.roles.includes("curator") ? "Curator resolve queue" : "Auto-resolve — admin weekly export",
    { t: r.vector.label, logo: r.vector.logo },
    "Corpus versioning & lineage",
  ];
  const answerRows = [
    "Hybrid retrieval (lexical + semantic)",
    "Grounding gate — evidence first",
    r.sel.model === "none"
      ? "Verbatim answer composer (extractive)"
      : { t: `${r.model.badge} — grounded generation`, logos: r.model.logos },
    graph ? "Entity graph & knowledge health" : "Citations & confidence",
    r.sel.scope === "full" ? "Answer API & multilingual" : "Clarify-back when evidence is thin",
  ];
  const teleRows = [
    ...extraRoles.map(x => x.ws),
    "Per-answer scoring & tracing",
    { t: r.obs.short, logos: r.obs.logos },
  ];

  /* role chips, right-aligned in the access band */
  let chipX = 954;
  const chipParts = [];
  for (const x of r.roles.slice().reverse()) {
    const w = Math.round(x.label.length * 6.6 + 22);
    chipX -= w;
    chipParts.push(`<rect x="${chipX}" y="34" width="${w}" height="22" rx="11"
        fill="#fff" stroke="#D6DAFB"/>
      <text x="${chipX + w / 2}" y="49" text-anchor="middle"
        font-family="JetBrains Mono,monospace" font-size="10" fill="#4338CA">${esc(x.label)}</text>`);
    chipX -= 8;
  }
  const chips = chipParts.join("");

  return `<svg viewBox="0 0 980 562" xmlns="http://www.w3.org/2000/svg" role="img"
      aria-label="Proposed architecture" font-family="Inter,sans-serif">
    <title>Knowledge Fabric — proposed architecture</title>
    <rect width="980" height="562" fill="#fff"/>
    <rect x="10" y="10" width="960" height="76" rx="12" fill="#EEF0FF" stroke="#D6DAFB"/>
    <text x="26" y="32" font-family="JetBrains Mono,monospace" font-size="11" letter-spacing="1.5"
          fill="#4338CA">ACCESS &amp; IDENTITY</text>
    ${logoTag(r.identity.logo, 26, 42, 20, "#4338CA")}
    <text x="${LOGOS[r.identity.logo] ? 54 : 26}" y="57" font-size="12.5" font-weight="600"
          fill="#22374D">${esc(r.identity.label)}</text>
    <text x="26" y="76" font-size="9.5" fill="#6A7F94">permissions applied before anything is searched</text>
    ${chips}

    ${zone(10, 108, 296, 226, "#047857", "#E7F8F1", "CONTENT PIPELINE", "your sources, your cadence",
      pipelineRows, false)}

    ${zone(326, 108, 330, 226, "#0086E6", "#E8F5FF", "GROUNDED ANSWERING",
      r.model.planeShort, answerRows, false)}

    ${zone(676, 108, 294, 226, "#9333EA", "#F8EDFE", "ROLES & TELEMETRY",
      tele ? "proof that it worked" : "arrives with the governed tier", teleRows, !tele)}

    <path d="M306 221 h20 M656 221 h20" stroke="#C9D6E2" stroke-width="2"/>
    <path d="M318 215 l8 6 l-8 6 M668 215 l8 6 l-8 6" stroke="#C9D6E2" stroke-width="2" fill="none"/>

    <rect x="10" y="358" width="960" height="58" rx="12" fill="#EEF1F5" stroke="#DCE2EA"/>
    <text x="26" y="382" font-family="JetBrains Mono,monospace" font-size="11" letter-spacing="1.5"
          fill="#344054">SECURITY &amp; OPERATIONS</text>
    <text x="26" y="400" font-size="11" fill="#475467">${esc(r.infra.runtime)} · ${esc(r.infra.secrets)}</text>
    ${logoTag(r.infra.logo, 926, 373, 28, "#344054")}

    <rect x="10" y="432" width="960" height="54" rx="12" fill="none" stroke="#94A3B8" stroke-dasharray="7 6"/>
    <text x="490" y="464" text-anchor="middle" font-size="13"
          fill="#475467">Everything above runs ${esc(r.infra.boundary)} — identity, network, keys and content stay with you.</text>

    ${tele ? `<path d="M823 334 V506 Q823 518 811 518 H172 Q160 518 160 506 V346"
        stroke="#9333EA" stroke-width="2" stroke-dasharray="4 7" fill="none"/>
      <path d="M154 356 l6 -10 l6 10" fill="none" stroke="#9333EA" stroke-width="2"/>
      <text x="490" y="542" text-anchor="middle" font-size="11.5"
        fill="#9333EA">questions the corpus cannot answer return as a ranked content backlog</text>` : ""}
  </svg>`;
}

/* --------------------------------------------------- proposal download */
function wrap(text, indent) {
  const words = String(text).split(/\s+/), out = [];
  let line = indent;
  for (const w of words) {
    if ((line + " " + w).length > 78 && line.trim()) { out.push(line); line = indent + w; }
    else line = line.trim() ? line + " " + w : indent + w;
  }
  if (line.trim()) out.push(line);
  return out.join("\n");
}

function proposalText(r) {
  const row = (k, v) => `  ${(k + " ").padEnd(18, ".")} ${v}`;
  const bullet = t => "  - " + wrap(t, "    ").slice(4);
  const demoURL = new URL(`../demo/${r.domain.demo}/`, location.href).href;
  const L = [];
  L.push("KNOWLEDGE FABRIC — PROPOSED SOLUTION",
         "QualiZeal · AI Center of Excellence",
         "Prepared " + new Date().toISOString().slice(0, 10), "");
  L.push("YOUR ANSWERS",
    row("Domain", r.domain.label),
    row("Runs on", `${r.infra.label} (${r.infra.boundary})`),
    row("Sign-in", r.identity.label),
    row("Models", r.model.label),
    row("Search index", r.vector.label),
    row("Team roles", r.roles.map(x => x.label).join(", ")),
    row("Telemetry", r.obs.label),
    row("First release", r.scope.label), "");
  if (r.adjustments.length) {
    L.push("WHERE WE ADJUSTED AN ANSWER — AND WHY");
    r.adjustments.forEach(a => L.push(bullet(a)));
    L.push("");
  }
  L.push("WHAT QUALIZEAL BUILDS FOR YOU");
  r.scope.includes.forEach(x => L.push("  - " + x));
  L.push("");
  L.push("THE ARCHITECTURE, IN WORDS",
    row("Access", `${r.identity.label}; roles: ${r.roles.map(x => x.label.toLowerCase()).join(", ")}`),
    row("Pipeline", `${r.infra.intake} -> extract/rank/OCR -> ${r.vector.label}`),
    row("Answering", r.model.plane),
    row("Telemetry", r.obs.label),
    row("Runs on", `${r.infra.runtime}; ${r.infra.secrets}`),
    row("Boundary", `everything runs ${r.infra.boundary}`), "");
  L.push("THE LIMITATIONS, OUT LOUD");
  r.limits.forEach(x => L.push(bullet(x)));
  L.push("");
  L.push("HOW WE DELIVER",
    "  " + r.phases.map(p => p[0]).join(" -> "),
    ...r.phases.map(p => row(p[0], p[1])), "");
  L.push("WE HAVE BUILT THIS BEFORE");
  L.push(wrap(`For ${r.domain.label.toLowerCase()}, we have shown ${r.domain.built}.`, "  "));
  L.push("  See it running: " + demoURL, "");
  L.push("QualiZeal — AI Center of Excellence · Knowledge Fabric");
  return L.join("\n") + "\n";
}

/* ------------------------------------------------------------- result */
function renderResult() {
  const r = resolve(sel);
  lastR = r;
  const el = document.getElementById("result");
  el.innerHTML = `
    <div class="eyebrow">Your proposed fabric</div>
    <div class="r-head">
      <h2>${esc(r.domain.label)}, running on ${esc(r.infra.label)}.</h2>
      <div class="badges">
        <span class="badge">${esc(r.model.badge)}</span>
        <span class="badge">${esc(r.vector.label)}</span>
        <span class="badge">${esc(r.scope.label)}</span>
        ${r.roles.map(x => `<span class="badge role">${esc(x.label)}</span>`).join("")}
      </div>
    </div>

    ${r.adjustments.length ? `<div class="card adjust" style="margin-top:16px">
      <h3>We adjusted ${r.adjustments.length === 1 ? "one answer" : "some answers"} — here is why</h3>
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
      <button class="ghost primary" data-dl-svg>Download the architecture (.svg)</button>
      <button class="ghost primary" data-dl-proposal>Download your proposal (.txt)</button>
      <button class="ghost" data-print>Print / save as PDF</button>
      <button class="ghost" data-share>Copy link to this result</button>
      <button class="ghost" data-restart>Start again</button>
    </div>`;
}

/* ------------------------------------------------------------- boot */
function syncFromHash() {
  ORDER.forEach(k => delete sel[k]);
  tempRoles = new Set(["reader"]);
  readHash();
  renderAdaptiveGrids();
  const first = ORDER.findIndex(k => !sel[k]);
  show(first === -1 ? ORDER.length : first);
}

loadLogos().then(() => {
  optionCards();
  readHash();
  applyPicked();
  window.addEventListener("hashchange", syncFromHash);
  const first = ORDER.findIndex(k => !sel[k]);
  show(first === -1 ? ORDER.length : first);
});
