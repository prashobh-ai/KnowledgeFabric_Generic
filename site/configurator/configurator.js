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

/* The architecture and journey drawings live in figures.js (archSVG, journeySVG). */

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
  const [icon, archPng, jourPng] = await Promise.all([
    brandIcon(), svgToPng(archSVG(r), 3800), svgToPng(journeySVG(r), 3800)]);
  const doc = newDoc("landscape");
  const W = doc.internal.pageSize.getWidth(), H = doc.internal.pageSize.getHeight();
  const place = (png) => {
    /* fit inside the chrome: x 12..W-12, y 26..H-18, centred */
    const maxW = W - 24, maxH = H - 44;
    let w = maxW, h = w * (png.h / png.w);
    if (h > maxH) { h = maxH; w = h * (png.w / png.h); }
    doc.addImage(png.data, "PNG", (W - w) / 2, 26 + (maxH - h) / 2, w, h, undefined, "FAST");
  };
  chrome(doc, icon, "Knowledge Fabric — proposed architecture", who, 1, 2);
  place(archPng);
  doc.addPage("a4", "landscape");
  chrome(doc, icon, "Knowledge Fabric — how an answer is produced", who, 2, 2);
  place(jourPng);
  doc.save(`Knowledge-Fabric-Architecture-${fileSlug(r)}.pdf`);
}

/* --------------------------------------------------- proposal PDF */
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
  const [icon, archPng, jourPng] = await Promise.all([
    brandIcon(), svgToPng(archSVG(r), 3000), svgToPng(journeySVG(r), 3000)]);
  const doc = newDoc("portrait");
  const W = doc.internal.pageSize.getWidth();
  const demoURL = new URL(`../demo/${r.domain.demo}/`, location.href).href;
  const title = "Knowledge Fabric — solution proposal";
  const PAGES = 6;
  let y;

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
  doc.text("The full-size architecture drawing accompanies this document as its own PDF.", 12, 146);

  /* -------- page 2: what we understood -------- */
  doc.addPage(); chrome(doc, icon, title, who, 2, PAGES);
  y = h2(doc, 34, "What we understood");
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

  /* -------- page 3: how an answer is produced -------- */
  doc.addPage(); chrome(doc, icon, title, who, 3, PAGES);
  y = h2(doc, 34, "How an answer is produced");
  const jw = W - 24, jh = jw * (jourPng.h / jourPng.w);
  doc.addImage(jourPng.data, "PNG", 12, y - 2, jw, jh, undefined, "FAST");
  y += jh + 8;
  doc.setFont("helvetica", "bold"); doc.setFontSize(10.5); doc.setTextColor(...AMBER);
  doc.text("Clarify-back: ask, don't refuse", 12, y); y += 6;
  doc.setFont("helvetica", "normal"); doc.setFontSize(9.3); doc.setTextColor(...INK2);
  doc.text(doc.splitTextToSize(
    "Generation is gated on the grounding check, which is what makes the citation promise structural " +
    "rather than aspirational. When evidence falls short, the system asks one targeted question, " +
    "re-retrieves on the refined query, and only then answers. When that is still not enough, it " +
    "returns the nearest approved sources and how to rephrase — never a bare refusal, never an " +
    "invented answer. Every clarification is logged, so the questions the corpus cannot yet answer " +
    "become a ranked content backlog and the knowledge base improves from real demand.", W - 24), 12, y);

  /* -------- page 4: the architecture -------- */
  doc.addPage(); chrome(doc, icon, title, who, 4, PAGES);
  y = h2(doc, 34, "The proposed architecture");
  const aw = W - 24, ah = aw * (archPng.h / archPng.w);
  doc.addImage(archPng.data, "PNG", 12, y - 2, aw, ah, undefined, "FAST");
  y += ah + 8;
  const zones = [
    ["Access and roles", `${r.identity.label}; ${r.roles.map(x => x.label.toLowerCase()).join(", ")} — permissions applied before anything is searched.`],
    ["Content pipeline", `${r.infra.intake}, then ${r.infra.flow}, into ${r.vector.label} — with ${r.sel.roles.includes("curator") ? "a human curator queue" : "weekly admin conflict export"}.`],
    ["Grounded answering", `Retrieve, grounding check, then ${r.sel.model === "none" ? "the verbatim composer" : r.model.badge} — with clarify-back as the recovery path.`],
    ["Trust and telemetry", r.sel.obs === "none" ? "Deferred by your choice — added when you opt in." : `${r.obs.label}; per-answer scoring; ${r.infra.audit}.`],
    ["Security and operations", `${r.infra.runtime}; ${r.infra.secrets}. Everything runs ${r.infra.boundary}.`],
  ];
  for (const [k, v] of zones) {
    doc.setFont("helvetica", "bold"); doc.setFontSize(9.3); doc.setTextColor(...INK);
    doc.text(k, 12, y);
    doc.setFont("helvetica", "normal"); doc.setTextColor(...INK2);
    const lines = doc.splitTextToSize(v, W - 70);
    doc.text(lines, 58, y);
    y += Math.max(5.2, lines.length * 4.2 + 1.4);
  }

  /* -------- page 5: approach & what makes this different -------- */
  doc.addPage(); chrome(doc, icon, title, who, 5, PAGES);
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
  doc.text("What makes this different", 12, y); y += 6;
  y = bullets(doc, y, [
    "Generation is gated, not trusted — the grounding check runs before anything is written; citation is a property of the design.",
    "Clarification instead of refusal — thin evidence produces a targeted question and a second attempt.",
    "Permissions applied before ranking — unauthorised content never enters the candidate set, so it cannot shape a result.",
    "The system reports its own gaps — failed and clarified questions become a ranked content backlog.",
    `Portable by construction — ${r.model.badge}, ${r.vector.label} and ${r.identity.label} are your deployment choices, swappable without re-platforming.`,
  ], BLUE, W - 24);
  y += 2;
  doc.setFont("helvetica", "bold"); doc.setFontSize(10.5); doc.setTextColor(...INK);
  doc.text("The working principles", 12, y); y += 6;
  y = bullets(doc, y, [
    `The answer workspace${r.sel.obs === "qzotel" ? " and the dashboards are" : " is"} custom-built for ${who}, not a re-skin of anything of ours.`,
    "Telemetry, translation and deferred formats are opt-in efforts we scope openly — never silently bundled, never silently dropped.",
    "Everything runs " + r.infra.boundary + "; identity, network, keys and content stay with you.",
  ], BLUE, W - 24);

  /* -------- page 6: ships, limitations, demo -------- */
  doc.addPage(); chrome(doc, icon, title, who, 6, PAGES);
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

    <div class="arch-svg" style="margin-top:20px">${archSVG(r)}</div>

    <div class="r-grid">
      <div>
        <div class="card">
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
