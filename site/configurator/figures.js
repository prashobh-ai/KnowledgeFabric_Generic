/* figures.js — the two client-facing drawings, composed from the resolved
 * rules: the five-zone reference architecture and the six-step answer
 * journey. Both follow the QualiZeal capability-overview design language —
 * gradient zone bands, icon cards, the clarify-back band, the backlog pill,
 * the security chip bar — and both substitute the client's actual choices
 * (with the vendors' own marks) into every card flagged * as a deployment
 * choice. Uses esc()/logoTag()/LOGOS from configurator.js at call time.
 */
"use strict";

/* ------------------------------------------------------------ tokens */
const FIG = {
  ink: "#16283A", body: "#52677B", mute: "#7C8FA3", red: "#DC2626",
  panels: {
    indigo:  { g: ["#4F46E5", "#7C7CF0"], tint: "#EEF0FF", line: "#D9DDF6", icon: "#4F46E5", itile: "#E3E6FB" },
    emerald: { g: ["#059669", "#34D399"], tint: "#EBF9F2", line: "#C8EBDA", icon: "#047857", itile: "#D8F3E6" },
    blue:    { g: ["#0284C7", "#38BDF8"], tint: "#EDF7FF", line: "#C9E4F8", icon: "#0369A1", itile: "#D9EEFC" },
    amber:   { g: ["#D97706", "#F59E0B"], tint: "#FEF7E8", line: "#F2D9A6", icon: "#B45309", itile: "#FBEBC9" },
    purple:  { g: ["#9333EA", "#C084FC"], tint: "#F8F1FE", line: "#E8D5F9", icon: "#7E22CE", itile: "#F0E1FC" },
  },
};

/* ------------------------------------------------------------- icons */
const FICONS = {
  users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
  app: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M6.5 6.6h.01M9.5 6.6h.01"/>',
  code: '<path d="m8 6-6 6 6 6M16 6l6 6-6 6"/>',
  doc: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/>',
  zap: '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
  layers: '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 12 10 5 10-5"/><path d="m2 17 10 5 10-5"/>',
  usercheck: '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><path d="m17 11 2 2 4-4"/>',
  db: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
  spark: '<path d="M12 2l1.9 5.9L20 9.8l-5 3.2 1.6 6L12 15.4 7.4 19l1.6-6-5-3.2 6.1-1.9z"/>',
  gauge: '<path d="M12 14l3.5-3.5"/><path d="M20.5 17.5a9.5 9.5 0 1 0-17 0"/>',
  pulse: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7.5 15v3M12 10v8M16.5 6v12"/>',
  archive: '<rect x="2" y="3" width="20" height="5" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8M10 12h4"/>',
  lock: '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  refresh: '<path d="M21 4v6h-6M3 20v-6h6"/><path d="M4.5 9a8 8 0 0 1 13.3-3L21 9M3 15l3.2 3A8 8 0 0 0 19.5 15"/>',
  key: '<circle cx="7.5" cy="15.5" r="4.5"/><path d="M11 12 21 2m-3 3 3 3"/>',
};

function ficon(name, x, y, s, color) {
  const p = FICONS[name];
  if (!p) return "";
  return `<g transform="translate(${x},${y}) scale(${s / 24})"><g fill="none" stroke="${color}"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${p}</g></g>`;
}

/* ------------------------------------------------------------ helpers */
function fwrap(s, maxChars, maxLines) {
  const words = String(s).split(/\s+/), lines = [];
  let line = "";
  for (const w of words) {
    if ((line + " " + w).trim().length > maxChars && line) { lines.push(line); line = w; }
    else line = line ? line + " " + w : w;
  }
  if (line) lines.push(line);
  if (lines.length > maxLines) {
    lines.length = maxLines;
    lines[maxLines - 1] = lines[maxLines - 1].replace(/.{2}$/, "…");
  }
  return lines;
}

function ftext(lines, x, y0, lh, size, color, weight, anchor) {
  return lines.map((l, i) =>
    `<text x="${x}" y="${y0 + i * lh}" font-size="${size}" fill="${color}"
      ${weight ? `font-weight="${weight}"` : ""} ${anchor ? `text-anchor="${anchor}"` : ""}>${esc(l)}</text>`).join("");
}

function fdefs(p) {
  const stops = (id, [a, b]) =>
    `<linearGradient id="${p}-${id}" x1="0" y1="0" x2="1" y2="0">
       <stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>`;
  return `<defs>
    ${Object.entries(FIG.panels).map(([k, v]) => stops(k, v.g)).join("")}
    <linearGradient id="${p}-rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#4F46E5"/><stop offset="1" stop-color="#F53E5A"/></linearGradient>
  </defs>`;
}

/* zone panel: rounded tinted rect with a gradient header band clipped to it */
function fpanel(p, clipId, x, y, w, h, zone, icon, label, tag, bandH) {
  const z = FIG.panels[zone];
  bandH = bandH || 46;
  return `<clipPath id="${p}-${clipId}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14"/></clipPath>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14" fill="${z.tint}" stroke="${z.line}"/>
    <g clip-path="url(#${p}-${clipId})">
      <rect x="${x}" y="${y}" width="${w}" height="${bandH}" fill="url(#${p}-${zone})"/></g>
    ${ficon(icon, x + 20, y + (bandH - 22) / 2, 22, "#fff")}
    <text x="${x + 52}" y="${y + bandH / 2 + 5.5}" font-size="15" font-weight="700" fill="#fff"
      letter-spacing="1.2">${esc(label)}</text>
    ${tag ? `<text x="${x + w - 18}" y="${y + bandH / 2 + 5}" font-size="12.5"
      fill="rgba(255,255,255,.88)" text-anchor="end">${esc(tag)}</text>` : ""}`;
}

/* icon-left detail card */
function fcard(x, y, w, h, zone, o) {
  const z = FIG.panels[zone];
  const tile = 36, tx = x + 14, ty = y + 14;
  const star = o.star ? `<tspan fill="${FIG.red}"> *</tspan>` : "";
  const logos = (o.logos || (o.logo ? [o.logo] : [])).filter(n => LOGOS[n]);
  const tileArt = logos.length
    ? logoTag(logos[0], tx + 7, ty + 7, 22, z.icon)
    : ficon(o.icon || "doc", tx + 7, ty + 7, 22, z.icon);
  const extraLogos = logos.slice(1).map((n, i) =>
    logoTag(n, x + w - 32 - i * 26, y + 14, 20, z.icon)).join("");
  const bodyLines = fwrap(o.body || "", Math.floor((w - 76) / 6.9), 3);
  return `<g ${o.dim ? 'opacity=".55"' : ""}>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="11" fill="#fff" stroke="${z.line}"/>
    <rect x="${tx}" y="${ty}" width="${tile}" height="${tile}" rx="9" fill="${z.itile}"/>
    ${tileArt}${extraLogos}
    <text x="${x + 62}" y="${y + 29}" font-size="15.5" font-weight="600" fill="${FIG.ink}">${esc(o.title)}${star}</text>
    ${ftext(bodyLines, x + 62, y + 48, 17, 12.6, FIG.body)}
  </g>`;
}

/* numbered step card (answering / journey) */
function fstep(x, y, w, h, zone, o) {
  const z = FIG.panels[o.hue || zone];
  const tile = 40, tx = x + 16, ty = y + 16;
  const star = o.star ? `<tspan fill="${FIG.red}"> *</tspan>` : "";
  const logos = (o.logos || []).filter(n => LOGOS[n]);
  const tileArt = logos.length
    ? logoTag(logos[0], tx + 8, ty + 8, 24, z.icon)
    : ficon(o.icon || "spark", tx + 8, ty + 8, 24, z.icon);
  const extraLogos = logos.slice(1).map((n, i) =>
    logoTag(n, x + w - 26 - i * 26, y + 18, 20, z.icon)).join("");
  const titleY = y + tile + 44;
  const bodyLines = fwrap(o.body || "", Math.floor((w - 34) / 6.9), 4);
  return `<g>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="12" fill="#fff" stroke="${o.stroke || z.line}"
      ${o.stroke ? 'stroke-width="1.6"' : ""}/>
    <rect x="${tx}" y="${ty}" width="${tile}" height="${tile}" rx="10" fill="${z.itile}"/>
    ${tileArt}${extraLogos}
    <circle cx="${x + 28}" cy="${titleY - 5.5}" r="11" fill="${z.icon}"/>
    <text x="${x + 28}" y="${titleY - 1}" font-size="12.5" font-weight="700" fill="#fff"
      text-anchor="middle">${o.num}</text>
    <text x="${x + 46}" y="${titleY}" font-size="16.5" font-weight="600" fill="${FIG.ink}">${esc(o.title)}${star}</text>
    ${ftext(bodyLines, x + 17, titleY + 24, 18, 13, FIG.body)}
  </g>`;
}

function fArrowV(x, y1, y2, color, w) {
  const d = y2 > y1 ? 1 : -1;
  return `<path d="M${x} ${y1} V${y2 - 8 * d}" stroke="${color}" stroke-width="${w || 2.2}" fill="none"/>
    <path d="M${x} ${y2} l${-5} ${-8 * d} h10 z" fill="${color}"/>`;
}
function fArrowH(x1, x2, y, color, w) {
  return `<path d="M${x1} ${y} H${x2 - 8}" stroke="${color}" stroke-width="${w || 2.2}" fill="none"/>
    <path d="M${x2} ${y} l-8 -5 v10 z" fill="${color}"/>`;
}

function fpill(cx, cy, text, fg, bg, line) {
  const w = text.length * 6.9 + 30;
  return `<rect x="${cx - w / 2}" y="${cy - 15}" width="${w}" height="30" rx="15"
      fill="${bg}" stroke="${line}"/>
    <text x="${cx}" y="${cy + 4.5}" font-size="13" font-weight="600" fill="${fg}"
      text-anchor="middle">${esc(text)}</text>`;
}

function ftitle(p, title, sub, who) {
  return `<text x="40" y="64" font-size="34" font-weight="700" fill="${FIG.ink}">${esc(title)}</text>
    <text x="40" y="92" font-size="15" fill="${FIG.mute}">${esc(sub)}</text>
    <rect x="40" y="104" width="130" height="5" rx="2.5" fill="url(#${p}-rule)"/>
    <text x="1860" y="60" font-size="14.5" font-weight="600" fill="${FIG.body}"
      text-anchor="end">Prepared for ${esc(who)}</text>
    <text x="1860" y="82" font-size="12.5" fill="${FIG.mute}" text-anchor="end">${new Date().toISOString().slice(0, 10)}</text>`;
}

function fbrand(y) {
  return `<text x="40" y="${y}" font-family="JetBrains Mono,monospace" font-size="12"
      letter-spacing="1.2" fill="${FIG.ink}">QUALI<tspan fill="#0086E6">ZEAL</tspan> · AI CENTER OF EXCELLENCE</text>
    <text x="1860" y="${y}" font-size="12" fill="${FIG.mute}" text-anchor="end">Knowledge Fabric — every commitment in this drawing is one we stand behind</text>`;
}

function fwatermark(cx, cy) {
  return `<text transform="rotate(-20 ${cx} ${cy})" x="${cx}" y="${cy}" text-anchor="middle"
    font-size="190" font-weight="700" fill="#0A1626" opacity="0.028" letter-spacing="26">QUALIZEAL</text>`;
}

/* =========================================================== ARCH */
function archSVG(r) {
  const p = "fa";
  const tele = r.sel.scope === "governed" || r.sel.scope === "full";
  const who = r.name || "your team";
  const curator = r.sel.roles.includes("curator");
  const roleList = r.roles.map(x => x.label.toLowerCase()).join(", ");
  const consoles = r.roles.filter(x => x.ws).map(x => x.label.toLowerCase().replace(/s$/, ""));

  const accessCards = [
    { icon: "users", title: "Roles",
      body: `${roleList.charAt(0).toUpperCase() + roleList.slice(1)} — mapped from your existing directory groups` },
    { icon: "app", title: "Web application",
      body: consoles.length
        ? `Chat with citations, custom-built for ${who} — plus ${consoles.join(", ")} consoles`
        : `Chat with citations, custom-built for ${who}` },
    { logo: r.identity.logo, title: r.identity.label, star: true,
      body: `${r.identity.sub} — group-to-role claims carried in the session token` },
    { icon: "code", title: "Answer API",
      body: `Role checks enforced on every route; orchestrates the answer flow — ${r.infra.api}` },
  ];

  const pipeCards = [
    { icon: "doc", title: "Source of record",
      body: "Procedures, policies, specs & process docs — docx · txt · xlsx · readable PDF" },
    { icon: "zap", title: "Event-driven intake", star: true,
      body: `${r.infra.intake} — publishes at any cadence` },
    { icon: "layers", title: "Extract and rank",
      body: `${r.infra.flow}: metadata, version rank, type, process area, entity, status` },
    { icon: "usercheck", title: "Curate and resolve",
      body: curator
        ? "Conflicts and superseded versions routed to your curator queue"
        : "Auto-resolve — conflicts exported weekly for admin review" },
    { logo: r.vector.logo, title: "Index sync", star: true,
      body: `${r.vector.label} — incremental; only what changed is reprocessed` },
  ];

  const genBody = r.sel.model === "none"
    ? "Verbatim answer composer — exact quoted sentences with citations, no generation"
    : `${r.model.plane} — citations inline`;
  const steps = [
    { num: 1, icon: "search", title: "Retrieve",
      body: "Hybrid search filtered by status and entity, reranked to the strongest sources" },
    { num: 2, icon: "shield", title: "Grounding check",
      body: "Evidence scored against a set threshold before a single word is written" },
    { num: 3, logos: r.model.logos, icon: "spark", title: "Generate", star: true, body: genBody },
  ];

  const obsNone = r.sel.obs === "none";
  const trustCards = [
    { icon: "gauge", title: "Per-answer scoring",
      body: "Grounding score, citation coverage, retrieval confidence — shown as high / medium / low" },
    { logos: obsNone ? [] : r.obs.logos, icon: "pulse", title: "Tracing", star: true,
      body: obsNone
        ? "Deferred by your choice — the hooks ship; spans arrive when you opt in"
        : "One span per answer: model, tokens, cost, latency, clarify, refusal, rating",
      dim: obsNone },
    { logos: obsNone ? [] : r.obs.logos, icon: "chart", title: "Usage, cost and quality", star: true,
      body: obsNone
        ? "Deferred — added when you opt in, scoped honestly as its own effort"
        : `${r.obs.short} — cost by day, top categories, clarify & refusal rates`,
      dim: obsNone },
    { icon: "archive", title: "Audit and BI export",
      body: r.infra.audit },
  ];

  const clarifyLines = [
    ["Below threshold", " → one targeted question back to the user — which entity? which process area? what detail?"],
    ["Refined query", " → re-retrieve → grounded answer; the added constraint usually lifts confidence over the threshold"],
    ["Still insufficient", " → the nearest approved sources plus how to rephrase — never a bare refusal"],
    ["Every clarification", " is logged, so unanswerable questions become a ranked content backlog"],
  ];

  const stepW = 264, stepXs = [534, 818, 1102];
  const pipeYs = [422, 526, 630, 734, 838];
  const trustYs = [422, 550, 678, 806];

  return `<svg viewBox="0 0 1900 1210" width="1900" height="1210" xmlns="http://www.w3.org/2000/svg"
      role="img" aria-label="Proposed architecture" font-family="Inter,system-ui,sans-serif">
  <title>Knowledge Fabric — proposed architecture</title>
  ${fdefs(p)}
  <rect width="1900" height="1210" fill="#fff"/>
  ${fwatermark(950, 620)}
  ${ftitle(p, "Knowledge Fabric — proposed architecture",
    `Every answer written from ${who}'s own approved sources, scored for confidence, and traceable to the page it came from`, who)}

  ${fpanel(p, "acc", 40, 128, 1820, 188, "indigo", "users", "ACCESS AND ROLES",
    "who can ask, and what they are allowed to see", 48)}
  ${accessCards.map((c, i) => fcard(60 + i * 455, 192, 435, 108, "indigo", c)).join("")}

  ${fArrowV(950, 318, 356, "#6366F1", 2.6)}
  ${fpill(1064, 337, r.sel.scope === "full" ? "query · role · language" : "query · role",
    "#4F46E5", "#EEF0FF", "#C7CBF5")}

  ${fpanel(p, "pipe", 40, 360, 430, 610, "emerald", "db", "CONTENT PIPELINE", "source of record to index")}
  ${pipeCards.map((c, i) => fcard(60, pipeYs[i], 390, 88, "emerald", c)).join("")}
  ${pipeYs.slice(1).map(y => fArrowV(255, y - 16, y - 2, "#34B37E")).join("")}

  ${fpanel(p, "ans", 510, 360, 880, 610, "blue", "spark", "GROUNDED ANSWERING", "the answer is assembled here")}
  ${steps.map((s, i) => fstep(stepXs[i], 422, stepW, 210, "blue", s)).join("")}
  ${fArrowH(798, 818, 527, "#5FA8D8")}${fArrowH(1082, 1102, 527, "#5FA8D8")}

  ${fArrowV(950, 636, 684, "#D97706")}
  <text x="964" y="664" font-size="12.5" font-style="italic" fill="#B45309">below threshold</text>
  ${fArrowV(666, 686, 636, "#D97706")}
  <text x="652" y="664" font-size="12.5" font-style="italic" fill="#B45309" text-anchor="end">refined query</text>

  ${fpanel(p, "cl", 534, 688, 832, 250, "amber", "chat", "CLARIFY-BACK · ASK, DON'T REFUSE",
    "the recovery path, not a dead end", 44)}
  ${clarifyLines.map(([b, t], i) => {
    const lines = fwrap(b + t, 112, 1);
    return `<text x="556" y="${766 + i * 42}" font-size="13.5" fill="#7A4A10">
      <tspan font-weight="700" fill="#92400E">${esc(b)}</tspan>${esc(t)}</text>`;
  }).join("")}

  <g ${tele ? "" : 'opacity=".55"'}>
  ${fpanel(p, "tr", 1430, 360, 430, 610, "purple", "gauge", "TRUST AND TELEMETRY",
    tele ? "proof that it worked" : "")}
  ${trustCards.map((c, i) => fcard(1450, trustYs[i], 390, 112, "purple", c)).join("")}
  ${trustYs.slice(1).map(y => fArrowV(1645, y - 16, y - 2, "#B478E8")).join("")}
  ${tele ? "" : `<text x="1836" y="348" font-size="12.5" font-weight="700" fill="${FIG.mute}"
      text-anchor="end" letter-spacing="1.5">ARRIVES WITH THE GOVERNED TIER</text>`}
  </g>

  ${fArrowH(470, 510, 527, "#8FA8BC", 2.6)}
  <g ${tele ? "" : 'opacity=".45"'}>${fArrowH(1390, 1430, 527, "#8FA8BC", 2.6)}</g>

  ${tele ? `
    <path d="M1645 970 V994 H255 V978" stroke="#A855F7" stroke-width="2.2"
      stroke-dasharray="5 7" fill="none"/>
    <path d="M255 970 l-5 8 h10 z" fill="#A855F7"/>
    ${fpill(950, 994, "Questions the corpus cannot yet answer return as a ranked content backlog",
      "#7E22CE", "#FAF5FF", "#E9D5FF")}` : ""}

  <rect x="40" y="1022" width="1820" height="118" rx="14" fill="#1F2937"/>
  ${ficon("lock", 64, 1036, 20, "#fff")}
  <text x="94" y="1051" font-size="15" font-weight="700" fill="#fff" letter-spacing="1.2">SECURITY AND OPERATIONS</text>
  <text x="1836" y="1051" font-size="12.5" fill="rgba(255,255,255,.75)" text-anchor="end">underpins every zone above</text>
  ${(() => {
    let x = 64;
    const chips = r.infra.secchips.map(c => {
      const w = c.length * 7.1 + 28;
      const s = `<rect x="${x}" y="1074" width="${w}" height="38" rx="10" fill="rgba(255,255,255,.95)"/>
        <text x="${x + w / 2}" y="1097.5" font-size="12.5" font-weight="600" fill="#1F2937"
          text-anchor="middle">${esc(c)}</text>`;
      x += w + 12;
      return s;
    }).join("");
    return chips + logoTag(r.infra.logo, 1822, 1078, 30, "#fff");
  })()}

  <text x="40" y="1172" font-size="12.5" fill="${FIG.mute}">Zones deploy together; depth within each is scoped to the engagement.</text>
  <text x="1860" y="1172" font-size="12.5" font-weight="600" fill="${FIG.red}"
    text-anchor="end">* your deployment choices — selected in this proposal, swappable without re-platforming</text>
  ${fbrand(1198)}
</svg>`;
}

/* ========================================================= JOURNEY */
function journeySVG(r) {
  const p = "fj";
  const who = r.name || "your team";
  const obsNone = r.sel.obs === "none";
  const cards = [
    { num: 1, icon: "chat", title: "Question",
      body: r.sel.scope === "full" ? "Carries the user's role and language" : "Carries the user's role" },
    { num: 2, icon: "key", title: "Access scope",
      body: "Only sources this role may see enter the search" },
    { num: 3, icon: "search", title: "Retrieve",
      body: "Hybrid search, filtered and reranked to the top sources" },
    { num: 4, icon: "shield", title: "Grounding check", hue: "amber", stroke: "#F5C97E",
      body: "Evidence scored against a threshold before generating" },
    { num: 5, logos: r.model.logos, icon: "spark", title: "Generate", star: true,
      body: r.sel.model === "none"
        ? "Verbatim composer — exact quoted sentences only"
        : `${r.model.badge} — written from the retrieved sources only` },
    { num: 6, icon: "gauge", title: "Scored answer", hue: "purple",
      body: "Citations inline; confidence shown as high, medium or low" },
  ];
  const w = 286, xs = [40, 346, 652, 958, 1264, 1570];
  const clarify = [
    { icon: "chat", title: "Ask one targeted question",
      body: "Which entity? Which process area? What level of detail? One question, never an interrogation" },
    { icon: "refresh", title: "Re-retrieve on the refined query",
      body: "The added constraint usually lifts grounding above the threshold and the answer proceeds" },
    { icon: "doc", title: "Still insufficient",
      body: "The nearest approved sources and how to rephrase — never a bare refusal, never an invented answer" },
  ];
  const teleText = obsNone
    ? [["You deferred telemetry for the first build", " — the hooks are in place. When you opt in, every answer, clarification and"],
       ["", "refusal emits one span, and questions the corpus cannot yet answer surface as a ranked content backlog."]]
    : [["Every answer, clarification and refusal emits one telemetry span", " — model, tokens, cost, latency, confidence, user rating. Questions the"],
       ["", "corpus cannot yet answer surface as a ranked content backlog, so the knowledge base improves from real usage rather than guesswork."]];

  return `<svg viewBox="0 0 1900 780" width="1900" height="780" xmlns="http://www.w3.org/2000/svg"
      role="img" aria-label="How an answer is produced" font-family="Inter,system-ui,sans-serif">
  <title>Knowledge Fabric — how an answer is produced</title>
  ${fdefs(p)}
  <rect width="1900" height="780" fill="#fff"/>
  ${fwatermark(950, 400)}
  ${ftitle(p, "Knowledge Fabric — how an answer is produced",
    "The system never guesses. When the evidence is thin it asks one clarifying question rather than refusing or inventing", who)}

  ${cards.map((c, i) => fstep(xs[i], 150, w, 150, "indigo", c)).join("")}
  ${xs.slice(1).map(x => fArrowH(x - 20, x, 225, "#9AACBE")).join("")}

  <path d="M1101 302 V340 Q1101 352 1089 352 H807 Q795 352 795 340 V310"
    stroke="#EA8C0F" stroke-width="2.6" fill="none"/>
  <path d="M795 302 l-5.5 9 h11 z" fill="#EA8C0F"/>
  <text x="779" y="336" font-size="13.5" font-weight="600" fill="#B45309" text-anchor="end">refined query</text>
  <text x="1115" y="336" font-size="13.5" font-weight="600" fill="#B45309">below threshold</text>
  <path d="M948 353 V400" stroke="#EA8C0F" stroke-width="2.2" stroke-dasharray="2 6" fill="none"/>

  ${fpanel(p, "cl", 40, 404, 1820, 200, "amber", "chat", "CLARIFY-BACK · ASK, DON'T REFUSE",
    "the recovery path, not a dead end", 46)}
  ${clarify.map((c, i) => fcard(60 + i * 597, 462, 577, 118, "amber", c)).join("")}

  <rect x="40" y="628" width="1820" height="76" rx="12" fill="#F7F2FD" stroke="#E4D4F8"/>
  ${teleText.map(([b, t], i) => `<text x="64" y="${658 + i * 24}" font-size="14" fill="#6B21A8">
    ${b ? `<tspan font-weight="700">${esc(b)}</tspan>` : ""}${esc(t)}</text>`).join("")}

  <text x="40" y="740" font-size="12.5" fill="${FIG.mute}">Confidence is shown to the user on every answer, not buried in a log.</text>
  <text x="1860" y="740" font-size="12.5" font-weight="600" fill="${FIG.red}"
    text-anchor="end">* model is your deployment choice — selected in this proposal, swappable per environment</text>
  ${fbrand(768)}
</svg>`;
}
