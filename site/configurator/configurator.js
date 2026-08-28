/* Configurator behaviour: a nine-step questionnaire whose result — the
 * architecture drawing with the vendors' own marks, the ship list, the
 * limitations — is composed entirely from rules.js. Selections live in the
 * URL hash, so a filled-in result is a link a salesperson can send.
 *
 * The takeaways are two branded, print-locked PDFs generated in the browser
 * (vendored jsPDF, no network): the architecture drawing, and a written
 * proposal addressed to the client by name.
 */
"use strict";

const ORDER = ["name", "domain", "infra", "identity", "model", "vector", "roles", "obs", "scope"];
const TITLES = { name: "Client", domain: "Domain", infra: "Cloud", identity: "Sign-in",
                 model: "Models", vector: "Index", roles: "Roles", obs: "Telemetry", scope: "Scope" };
const ADAPTIVE = ["identity", "model", "vector", "obs"];   // labels follow the chosen cloud
const NO_NAME = "-";                                       // sentinel: asked, none given
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
  const inp = document.getElementById("client-name");
  if (inp && sel.name && sel.name !== NO_NAME) inp.value = sel.name;
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
  const h = ORDER.filter(k => sel[k])
    .map(k => `${k}=${k === "name" ? encodeURIComponent(sel[k]) : sel[k]}`).join("&");
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
    } else if (k === "name") {
      sel.name = v.slice(0, 60);
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
    if (q === "name") {
      const v = document.getElementById("client-name").value.trim().slice(0, 60);
      sel.name = v || NO_NAME;
    }
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
    const inp = document.getElementById("client-name");
    if (inp) inp.value = "";
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
  const dlA = e.target.closest("[data-dl-arch]");
  if (dlA && lastR) busy(dlA, () => architecturePDF(lastR));
  const dlP = e.target.closest("[data-dl-proposal]");
  if (dlP && lastR) busy(dlP, () => proposalPDF(lastR));
});

function busy(btn, job) {
  if (btn.dataset.busy) return;
  btn.dataset.busy = "1";
  const t = btn.textContent;
  btn.textContent = "Preparing…";
  Promise.resolve().then(job).catch(err => {
    console.error(err);
    btn.textContent = "Something went wrong — try print";
    setTimeout(() => { btn.textContent = t; delete btn.dataset.busy; }, 2500);
    throw err;
  }).then(() => { btn.textContent = t; delete btn.dataset.busy; });
}

/* -------------------------------------------------- architecture SVG */
function arrowH(x1, x2, y, color) {          // horizontal, pointing +x
  return `<path d="M${x1} ${y} H${x2 - 8}" stroke="${color}" stroke-width="2" fill="none"/>
    <path d="M${x2} ${y} l-8 -4.5 v9 z" fill="${color}"/>`;
}
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
  const who = r.name || "your team";

  const pipelineRows = [
    r.infra.intake,
    "docx · txt · xlsx · readable PDF",
    "Parse · extract · rank",
    r.sel.roles.includes("curator") ? "Curator resolve queue" : "Auto-resolve — admin weekly export",
    { t: r.vector.label, logo: r.vector.logo },
  ];
  const answerRows = [
    "Hybrid retrieval (lexical + semantic)",
    "Grounding gate — evidence first",
    r.sel.model === "none"
      ? "Verbatim answer composer (extractive)"
      : { t: `${r.model.badge} — grounded generation`, logos: r.model.logos },
    graph ? "Entity graph & knowledge health" : "Citations & confidence",
    r.sel.scope === "full" ? "Answer API & widget" : "Clarify-back when evidence is thin",
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
    chipParts.push(`<rect x="${chipX}" y="30" width="${w}" height="22" rx="11"
        fill="#fff" stroke="#D6DAFB"/>
      <text x="${chipX + w / 2}" y="45" text-anchor="middle"
        font-family="JetBrains Mono,monospace" font-size="10" fill="#4338CA">${esc(x.label)}</text>`);
    chipX -= 8;
  }
  const chips = chipParts.join("");

  return `<svg viewBox="0 0 980 544" width="980" height="544" xmlns="http://www.w3.org/2000/svg"
      role="img" aria-label="Proposed architecture" font-family="Inter,sans-serif">
    <title>Knowledge Fabric — proposed architecture</title>
    <rect width="980" height="544" fill="#fff"/>
    <text transform="rotate(-22 490 272)" x="490" y="300" text-anchor="middle"
      font-family="Inter,sans-serif" font-size="110" font-weight="700"
      fill="#0A1626" opacity="0.035" letter-spacing="14">QUALIZEAL</text>

    <rect x="10" y="10" width="960" height="74" rx="12" fill="#EEF0FF" stroke="#D6DAFB"/>
    <text x="26" y="31" font-family="JetBrains Mono,monospace" font-size="11" letter-spacing="1.5"
          fill="#4338CA">ACCESS &amp; IDENTITY</text>
    ${logoTag(r.identity.logo, 26, 40, 20, "#4338CA")}
    <text x="${LOGOS[r.identity.logo] ? 54 : 26}" y="55" font-size="12.5" font-weight="600"
          fill="#22374D">${esc(r.identity.label)}</text>
    <text x="26" y="74" font-size="9.5" fill="#6A7F94">permissions applied before anything is searched</text>
    ${chips}

    <path d="M478 92 v24 M502 92 v24" stroke="#4338CA" stroke-width="2" fill="none"/>
    <path d="M478 116 l-4.5 -8 h9 z" fill="#4338CA"/>
    <path d="M502 92 l-4.5 8 h9 z" fill="#4338CA"/>
    <text x="512" y="99" font-size="9.5" fill="#4338CA">questions in</text>
    <text x="512" y="111" font-size="9.5" fill="#4338CA">cited answers back</text>

    ${zone(10, 124, 296, 226, "#047857", "#E7F8F1", "CONTENT PIPELINE", "your sources, your cadence",
      pipelineRows, false)}

    ${zone(326, 124, 330, 226, "#0086E6", "#E8F5FF", "GROUNDED ANSWERING",
      r.model.planeShort, answerRows, false)}

    ${zone(676, 124, 294, 226, "#9333EA", "#F8EDFE", "ROLES & TELEMETRY",
      tele ? "proof that it worked" : "arrives with the governed tier", teleRows, !tele)}

    ${arrowH(306, 326, 237, "#8FA8BC")}
    <g ${tele ? "" : 'opacity=".45"'}>${arrowH(656, 676, 237, "#8FA8BC")}</g>

    ${tele ? `<path d="M823 350 v14 H158 v-6" stroke="#9333EA" stroke-width="2"
        stroke-dasharray="4 7" fill="none"/>
      <path d="M158 350 l-4.5 8 h9 z" fill="#9333EA"/>
      <text x="490" y="378" text-anchor="middle" font-size="10.5"
        fill="#9333EA">questions the corpus cannot answer return as a ranked content backlog</text>` : ""}

    <rect x="10" y="390" width="960" height="56" rx="12" fill="#EEF1F5" stroke="#DCE2EA"/>
    <text x="26" y="413" font-family="JetBrains Mono,monospace" font-size="11" letter-spacing="1.5"
          fill="#344054">SECURITY &amp; OPERATIONS</text>
    <text x="26" y="431" font-size="11" fill="#475467">${esc(r.infra.runtime)} · ${esc(r.infra.secrets)}</text>
    ${logoTag(r.infra.logo, 926, 404, 28, "#344054")}

    <rect x="10" y="460" width="960" height="50" rx="12" fill="none" stroke="#94A3B8" stroke-dasharray="7 6"/>
    <text x="490" y="490" text-anchor="middle" font-size="12.5"
          fill="#475467">Everything above runs ${esc(r.infra.boundary)} — identity, network, keys and content stay with you.</text>

    <text x="10" y="532" font-size="10" fill="#6A7F94">Prepared for ${esc(who)}</text>
    <text x="970" y="532" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="10"
      letter-spacing="1.2" fill="#0A1626">QUALI<tspan fill="#0086E6">ZEAL</tspan> · AI CENTER OF EXCELLENCE — KNOWLEDGE FABRIC</text>
  </svg>`;
}

/* ------------------------------------------------------- PDF plumbing */
function pdfLib() {
  if (!window.jspdf || !window.jspdf.jsPDF) throw new Error("jsPDF not loaded");
  return window.jspdf.jsPDF;
}

let brandIconCache = null;
async function brandIcon() {
  if (brandIconCache) return brandIconCache;
  const blob = await fetch("../assets/brand/qualizeal-icon.png").then(x => x.blob());
  brandIconCache = await new Promise(res => {
    const f = new FileReader(); f.onload = () => res(f.result); f.readAsDataURL(blob);
  });
  return brandIconCache;
}

function svgToPng(svgStr, wPx) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(new Blob([svgStr], { type: "image/svg+xml" }));
    img.onload = () => {
      const scale = wPx / (img.width || 980);
      const c = document.createElement("canvas");
      c.width = wPx; c.height = Math.round((img.height || 544) * scale);
      const g = c.getContext("2d");
      g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height);
      g.drawImage(img, 0, 0, c.width, c.height);
      URL.revokeObjectURL(url);
      resolve({ data: c.toDataURL("image/png"), w: c.width, h: c.height });
    };
    img.onerror = e => { URL.revokeObjectURL(url); reject(e); };
    img.src = url;
  });
}

function newDoc(orientation) {
  const JsPDF = pdfLib();
  return new JsPDF({
    orientation, unit: "mm", format: "a4", compress: true,
    encryption: {                        // print-only: viewers refuse edits
      ownerPassword: "qualizeal-aicoe",
      userPermissions: ["print"],
    },
  });
}

const INK = [10, 22, 38], INK2 = [34, 55, 77], MUTE = [106, 127, 148],
      BLUE = [0, 134, 230], AMBER = [220, 104, 3], RULE = [223, 231, 238];

function chrome(doc, icon, docTitle, who, pageNo, pageCount) {
  const W = doc.internal.pageSize.getWidth(), H = doc.internal.pageSize.getHeight();
  /* watermark */
  doc.saveGraphicsState();
  doc.setGState(new doc.GState({ opacity: 0.045 }));
  doc.setFont("helvetica", "bold"); doc.setFontSize(86); doc.setTextColor(...INK);
  doc.text("QUALIZEAL", W / 2, H / 2 + 10, { align: "center", angle: 28 });
  doc.restoreGraphicsState();
  /* header */
  if (icon) doc.addImage(icon, "PNG", 12, 9, 8, 8);
  doc.setFont("helvetica", "bold"); doc.setFontSize(11); doc.setTextColor(...INK);
  doc.text("QUALI", 23, 15);
  doc.setTextColor(...BLUE); doc.text("ZEAL", 23 + doc.getTextWidth("QUALI"), 15);
  doc.setFont("helvetica", "normal"); doc.setFontSize(7); doc.setTextColor(...MUTE);
  doc.text("AI CENTER OF EXCELLENCE", 23, 19.2);
  doc.setFontSize(9); doc.setTextColor(...INK2);
  doc.text(docTitle, W - 12, 15, { align: "right" });
  doc.setDrawColor(...RULE); doc.setLineWidth(0.3); doc.line(12, 22, W - 12, 22);
  /* footer */
  doc.line(12, H - 14, W - 12, H - 14);
  doc.setFontSize(7.5); doc.setTextColor(...MUTE);
  doc.text(`Prepared for ${who} by QualiZeal · AI Center of Excellence — confidential`, 12, H - 9);
  doc.text(`${new Date().toISOString().slice(0, 10)} · page ${pageNo} of ${pageCount}`,
    W - 12, H - 9, { align: "right" });
}

function fileSlug(r) {
  const n = (r.name || "").replace(/[^\w]+/g, "-").replace(/^-+|-+$/g, "");
  return n || r.domain.demo;
}

/* ------------------------------------------------ architecture PDF */
async function architecturePDF(r) {
  const who = r.name || "your team";
  const [icon, png] = await Promise.all([brandIcon(), svgToPng(archSVG(r), 2940)]);
  const doc = newDoc("landscape");
  const W = doc.internal.pageSize.getWidth();
  chrome(doc, icon, "Knowledge Fabric — proposed architecture", who, 1, 1);
  doc.setFont("helvetica", "bold"); doc.setFontSize(15); doc.setTextColor(...INK);
  doc.text(`${r.domain.label}, running on ${r.infra.label}`, 12, 32);
  doc.setFont("helvetica", "normal"); doc.setFontSize(9); doc.setTextColor(...MUTE);
  doc.text(`${r.model.badge}  ·  ${r.vector.label}  ·  ${r.obs.short}  ·  ${r.scope.label}  ·  roles: ${r.roles.map(x => x.label.toLowerCase()).join(", ")}`,
    12, 38);
  const iw = W - 24, ih = iw * (png.h / png.w);
  doc.addImage(png.data, "PNG", 12, 43, iw, ih, undefined, "FAST");
  doc.save(`Knowledge-Fabric-Architecture-${fileSlug(r)}.pdf`);
}

/* --------------------------------------------------- proposal PDF */
function drawFlow(doc, y, steps, opts) {
  /* one left-to-right workflow: boxes joined by arrows, laid out to fill the
     text column; optional labelled return arrow drawn UNDER the row so no
     line ever crosses a box. Returns the y below everything drawn. */
  const x0 = 12, x1 = doc.internal.pageSize.getWidth() - 12;
  const gap = 6, boxH = 14;
  const wSum = x1 - x0 - gap * (steps.length - 1);
  const weights = steps.map(s => Math.max(s.t.length, 8));
  const wTot = weights.reduce((a, b) => a + b, 0);
  let x = x0;
  const centers = [];
  steps.forEach((s, i) => {
    const w = Math.max(16, wSum * weights[i] / wTot);
    doc.setFillColor(...(s.hue ? [232, 245, 255] : [244, 246, 248]));
    doc.setDrawColor(...RULE); doc.setLineWidth(0.3);
    doc.roundedRect(x, y, w, boxH, 1.6, 1.6, "FD");
    doc.setFont("courier", "normal"); doc.setFontSize(6.8);
    doc.setTextColor(...INK2);
    const lines = doc.splitTextToSize(s.t, w - 3);
    const ty = y + boxH / 2 + (lines.length > 1 ? -0.6 : 1);
    doc.text(lines.slice(0, 2), x + w / 2, ty, { align: "center", baseline: "middle" });
    centers.push({ cx: x + w / 2, xEnd: x + w, xStart: x });
    if (i < steps.length - 1) {
      const ax = x + w, ay = y + boxH / 2;
      doc.setDrawColor(143, 168, 188); doc.setLineWidth(0.5);
      doc.line(ax + 0.8, ay, ax + gap - 2.4, ay);
      doc.setFillColor(143, 168, 188);
      doc.triangle(ax + gap - 0.8, ay, ax + gap - 3.2, ay - 1.4, ax + gap - 3.2, ay + 1.4, "F");
    }
    x += w + gap;
  });
  let yb = y + boxH;
  if (opts && opts.back) {
    const from = centers[opts.back.from].cx, to = centers[opts.back.to].cx;
    const yr = yb + 5;
    doc.setDrawColor(147, 51, 234); doc.setLineWidth(0.45);
    doc.setLineDashPattern([1.4, 1.6], 0);
    doc.line(from, yb + 1, from, yr); doc.line(from, yr, to, yr); doc.line(to, yr, to, yb + 2.6);
    doc.setLineDashPattern([], 0);
    doc.setFillColor(147, 51, 234);
    doc.triangle(to, yb + 0.8, to - 1.4, yb + 3.2, to + 1.4, yb + 3.2, "F");
    doc.setFont("helvetica", "italic"); doc.setFontSize(6.8);
    doc.setTextColor(147, 51, 234);
    doc.text(opts.back.label, (from + to) / 2, yr + 3.4, { align: "center" });
    yb = yr + 5;
  }
  return yb;
}

function h2(doc, y, text) {
  doc.setFont("helvetica", "bold"); doc.setFontSize(14); doc.setTextColor(...INK);
  doc.text(text, 12, y);
  doc.setDrawColor(245, 62, 90); doc.setLineWidth(0.7);
  doc.line(12, y + 2.2, 24, y + 2.2);
  return y + 10;
}

function bullets(doc, y, items, color, maxW) {
  doc.setFont("helvetica", "normal"); doc.setFontSize(9.3);
  for (const it of items) {
    const lines = doc.splitTextToSize(it, maxW - 6);
    doc.setFillColor(...(color || BLUE));
    doc.circle(14.2, y - 1.2, 0.8, "F");
    doc.setTextColor(...INK2);
    doc.text(lines, 18, y);
    y += lines.length * 4.3 + 2.2;
  }
  return y;
}

async function proposalPDF(r) {
  const who = r.name || "your team";
  const [icon, png] = await Promise.all([brandIcon(), svgToPng(archSVG(r), 2450)]);
  const doc = newDoc("portrait");
  const W = doc.internal.pageSize.getWidth();
  const demoURL = new URL(`../demo/${r.domain.demo}/`, location.href).href;
  const title = "Knowledge Fabric — solution proposal";
  const PAGES = 5;

  /* -------- page 1: cover -------- */
  chrome(doc, icon, title, who, 1, PAGES);
  doc.setFont("helvetica", "normal"); doc.setFontSize(10); doc.setTextColor(...MUTE);
  doc.text("QualiZeal · AI Center of Excellence", 12, 66);
  doc.setFont("helvetica", "bold"); doc.setFontSize(30); doc.setTextColor(...INK);
  doc.text("Knowledge Fabric", 12, 78);
  doc.setFont("helvetica", "normal"); doc.setFontSize(15); doc.setTextColor(...BLUE);
  doc.text(`A solution proposal for ${who}`, 12, 88);
  doc.setFontSize(10.5); doc.setTextColor(...INK2);
  doc.text(doc.splitTextToSize(
    `${r.domain.label} · running ${r.infra.boundary} · ${r.scope.label.toLowerCase()}.`, W - 24), 12, 98);
  const chipsY = 112;
  doc.setFont("courier", "normal"); doc.setFontSize(8); doc.setTextColor(...INK2);
  let cx = 12;
  for (const c of [r.model.badge, r.vector.label, r.identity.label, r.obs.short]) {
    const w = doc.getTextWidth(c) + 6;
    doc.setDrawColor(...RULE); doc.setFillColor(248, 250, 252);
    doc.roundedRect(cx, chipsY - 4.4, w, 6.6, 2.2, 2.2, "FD");
    doc.text(c, cx + 3, chipsY);
    cx += w + 3;
    if (cx > W - 40) break;
  }
  doc.setFont("helvetica", "italic"); doc.setFontSize(9); doc.setTextColor(...MUTE);
  doc.text(doc.splitTextToSize(
    "Composed from your answers to our solution-fit questionnaire. Every commitment in this document " +
    "is one we are prepared to stand behind — and every limitation is stated before a contract would.", W - 24), 12, 128);
  doc.setFontSize(8.5);
  doc.text("This document accompanies your architecture drawing (separate PDF).", 12, 148);

  /* -------- page 2: what we understood -------- */
  doc.addPage(); chrome(doc, icon, title, who, 2, PAGES);
  let y = h2(doc, 34, "What we understood");
  doc.setFont("helvetica", "normal"); doc.setFontSize(9.5); doc.setTextColor(...INK2);
  doc.text(doc.splitTextToSize(
    `${who === "your team" ? "Your" : who + "'s"} documents live in the ${r.domain.label.toLowerCase()} domain. ` +
    `The platform must run ${r.infra.boundary}, sign users in through ${r.identity.label}, ` +
    `and answer with ${r.model.plane.replace(/\.$/, "").replace(/^Extractive/, "extractive")}. ` +
    `The people working it: ${r.roles.map(x => x.label.toLowerCase()).join(", ")}.`, W - 24), 12, y);
  y += 20;
  const rows = [
    ["Domain", r.domain.label],
    ["Runs on", `${r.infra.label} — ${r.infra.boundary}`],
    ["Sign-in", r.identity.label],
    ["Models", r.model.label],
    ["Search index", r.vector.label],
    ["Team roles", r.roles.map(x => x.label).join(", ")],
    ["Telemetry", r.obs.label],
    ["First release", r.scope.label],
  ];
  for (const [k, v] of rows) {
    doc.setDrawColor(...RULE); doc.setLineWidth(0.25); doc.line(12, y + 2.4, W - 12, y + 2.4);
    doc.setFont("courier", "normal"); doc.setFontSize(8); doc.setTextColor(...MUTE);
    doc.text(k.toUpperCase(), 12, y);
    doc.setFont("helvetica", "normal"); doc.setFontSize(9.5); doc.setTextColor(...INK);
    doc.text(doc.splitTextToSize(v, W - 70), 58, y);
    y += 8.4;
  }
  y += 6;
  doc.setFont("helvetica", "bold"); doc.setFontSize(10.5); doc.setTextColor(...INK);
  doc.text("What we take in, honestly", 12, y); y += 6;
  doc.setFont("helvetica", "normal"); doc.setFontSize(9.3); doc.setTextColor(...INK2);
  doc.text(doc.splitTextToSize(
    "The first build ingests text-first formats — .docx, .txt, .xlsx and readable PDFs, " +
    "including PDFs that carry tables and embedded images. Scanned or image-only documents, OCR, " +
    "audio and video are deliberately not first-build items: a reading limitation should never " +
    "become a question mark over what the fabric answers. Where your estate needs them, that effort " +
    "is scoped and finalised with QualiZeal separately.", W - 24), 12, y);
  y += 26;
  doc.setFont("helvetica", "bold"); doc.setFontSize(10.5); doc.setTextColor(...INK);
  doc.text("Language", 12, y); y += 6;
  doc.setFont("helvetica", "normal"); doc.setFontSize(9.3); doc.setTextColor(...INK2);
  doc.text(doc.splitTextToSize(
    "English is the working language of the first release. Where you need more, we translate the " +
    "question and the answer only — source documents stay as written — and we commit to a language " +
    "only after validating its quality with your approved model, never by default.", W - 24), 12, y);

  /* -------- page 3: how we approach it -------- */
  doc.addPage(); chrome(doc, icon, title, who, 3, PAGES);
  y = h2(doc, 34, "How we plan to approach it");
  if (r.adjustments.length) {
    doc.setFillColor(238, 240, 255); doc.setDrawColor(214, 218, 251);
    doc.setFont("helvetica", "normal"); doc.setFontSize(8.6);
    const boxLines = r.adjustments.map(a => doc.splitTextToSize("•  " + a, W - 34));
    const boxH = boxLines.reduce((a, l) => a + l.length * 4.1 + 2, 8);
    doc.roundedRect(12, y - 4, W - 24, boxH, 2, 2, "FD");
    doc.setFont("helvetica", "bold"); doc.setFontSize(9); doc.setTextColor(67, 56, 202);
    doc.text("Where we adjusted an answer — and said so", 16, y + 1);
    let yy = y + 6.5;
    doc.setFont("helvetica", "normal"); doc.setFontSize(8.6);
    for (const l of boxLines) { doc.text(l, 16, yy); yy += l.length * 4.1 + 2; }
    y = yy + 4;
  }
  const phaseNotes = {
    Discover: "We inventory the document estate, agree the ingest format list, size capacity" +
      (r.sel.model === "selfhost" ? " and the GPU pool" : "") +
      ", and validate answer quality with your approved model against your own material.",
    Prove: "A working fabric on a bounded corpus, in your boundary, measured against questions " +
      "your teams actually ask — with the grounding gate showing its evidence.",
    Harden: (r.sel.infra === "onprem" || r.sel.infra === "disconnected"
      ? "Boundary work is the long pole here: your cluster, storage and transfer cadence set the pace. "
      : "") + "Security review, role scoping, audit trail, operational runbooks — production posture.",
    Extend: "Corpus growth on your cadence, the ranked content backlog worked down" +
      (r.sel.obs !== "none" ? ", dashboards live" : "") +
      ", and anything we deferred scoped honestly as its own effort.",
  };
  for (const [ph] of r.phases) {
    doc.setFont("helvetica", "bold"); doc.setFontSize(11); doc.setTextColor(...BLUE);
    doc.text(ph, 12, y);
    doc.setFont("helvetica", "normal"); doc.setFontSize(9.3); doc.setTextColor(...INK2);
    const lines = doc.splitTextToSize(phaseNotes[ph] || "", W - 52);
    doc.text(lines, 40, y);
    y += Math.max(8, lines.length * 4.3 + 3.5);
  }
  y += 4;
  doc.setFont("helvetica", "bold"); doc.setFontSize(10.5); doc.setTextColor(...INK);
  doc.text("The working principles", 12, y); y += 6;
  y = bullets(doc, y, [
    "Answers only from your governed content, with citations — the grounding gate refuses before it invents.",
    `The answer workspace${r.sel.obs === "qzotel" ? " and the dashboards are" : " is"} custom-built for ${who}, not a re-skin of anything of ours.`,
    "Telemetry, translation and deferred formats are opt-in efforts we scope openly — never silently bundled, never silently dropped.",
    "Everything runs " + r.infra.boundary + "; identity, network, keys and content stay with you.",
  ], BLUE, W - 24);

  /* -------- page 4: workflows -------- */
  doc.addPage(); chrome(doc, icon, title, who, 4, PAGES);
  y = h2(doc, 34, "How it works — two workflows");
  doc.setFont("helvetica", "bold"); doc.setFontSize(10); doc.setTextColor(...INK);
  doc.text("1 · How knowledge gets in", 12, y); y += 7;
  const curator = r.sel.roles.includes("curator");
  y = drawFlow(doc, y, [
    { t: "Your sources — docx txt xlsx pdf" },
    { t: r.infra.intake },
    { t: "Parse · extract · rank" },
    { t: r.vector.label, hue: 1 },
    { t: "Governed corpus" },
  ], { back: curator
        ? { from: 4, to: 2, label: "curators resolve conflicts & duplicates before answers rely on them" }
        : { from: 4, to: 2, label: "auto-resolve — conflicts export weekly for admin review" } });
  y += 10;
  doc.setFont("helvetica", "bold"); doc.setFontSize(10); doc.setTextColor(...INK);
  doc.text("2 · How a question becomes a cited answer", 12, y); y += 7;
  y = drawFlow(doc, y, [
    { t: `${who} asks` },
    { t: r.identity.label },
    { t: "Hybrid retrieval" },
    { t: "Grounding gate" },
    { t: r.sel.model === "none" ? "Verbatim composer" : r.model.badge, hue: 1 },
    { t: "Cited answer" },
  ], { back: { from: 5, to: 0, label: "answer returns with citations & confidence — or an honest clarify-back" } });
  y += 12;
  doc.setFont("helvetica", "normal"); doc.setFontSize(8.8); doc.setTextColor(...MUTE);
  doc.text(doc.splitTextToSize(
    (r.sel.scope === "governed" || r.sel.scope === "full"
      ? "Questions the corpus cannot answer return as a ranked content backlog, so the fabric tells you what to write next. "
      : "") +
    "The full architecture, drawn with each vendor's own mark, is the companion PDF to this document.",
    W - 24), 12, y);
  y += 14;
  const archW = W - 24, archH = archW * (png.h / png.w);
  doc.setFont("helvetica", "bold"); doc.setFontSize(10); doc.setTextColor(...INK);
  doc.text("The architecture, at a glance", 12, y); y += 4;
  doc.addImage(png.data, "PNG", 12, y, archW, archH, undefined, "FAST");

  /* -------- page 5: ships, limitations, demo -------- */
  doc.addPage(); chrome(doc, icon, title, who, 5, PAGES);
  y = h2(doc, 34, "What ships in the first release");
  y = bullets(doc, y, scopeShips(r.sel.scope), BLUE, W - 24);
  y += 4;
  doc.setFont("helvetica", "bold"); doc.setFontSize(12); doc.setTextColor(...AMBER);
  doc.text("The limitations, out loud", 12, y); y += 7;
  y = bullets(doc, y, r.limits, AMBER, W - 24);
  y += 4;
  doc.setFont("helvetica", "bold"); doc.setFontSize(12); doc.setTextColor(...INK);
  doc.text("We have built this before", 12, y); y += 6;
  doc.setFont("helvetica", "normal"); doc.setFontSize(9.3); doc.setTextColor(...INK2);
  doc.text(doc.splitTextToSize(
    `For ${r.domain.label.toLowerCase()}, we have shown ${r.domain.built}. ` +
    "The demonstration runs on a fully synthetic corpus — real standards, invented content.", W - 24), 12, y);
  y += 14;
  doc.setFont("courier", "normal"); doc.setFontSize(8.6); doc.setTextColor(...BLUE);
  doc.textWithLink("See it running:  " + demoURL, 12, y, { url: demoURL });

  doc.save(`Knowledge-Fabric-Proposal-${fileSlug(r)}.pdf`);
}

/* ------------------------------------------------------------- result */
function renderResult() {
  const r = resolve(sel);
  lastR = r;
  const who = r.name || "your team";
  const el = document.getElementById("result");
  el.innerHTML = `
    <div class="eyebrow">${r.name ? `Prepared for ${esc(r.name)}` : "Your proposed fabric"}</div>
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
      <button class="ghost primary" data-dl-arch>Download the architecture (PDF)</button>
      <button class="ghost primary" data-dl-proposal>Download ${r.name ? esc(r.name) + "'s" : "your"} proposal (PDF)</button>
      <button class="ghost" data-print>Print this page</button>
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
  const nameForm = document.getElementById("client-name");
  if (nameForm) nameForm.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      const btn = nameForm.closest(".q").querySelector("[data-next]");
      if (btn) btn.click();
    }
  });
  window.addEventListener("hashchange", syncFromHash);
  const first = ORDER.findIndex(k => !sel[k]);
  show(first === -1 ? ORDER.length : first);
});
