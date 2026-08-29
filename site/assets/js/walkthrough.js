/* Knowledge Fabric — walkthrough behaviour.
   Content lives here so the page stays a two-file, dependency-free deploy. */
(function () {
'use strict';
const $ = s => document.querySelector(s);
const el = (t, c, h) => { const n = document.createElement(t); if (c) n.className = c;
  if (h != null) n.innerHTML = h; return n; };
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;

const HUE = { blue:'#0086E6', indigo:'#4338CA', emerald:'#047857', amber:'#DC6803',
              violet:'#9333EA', slate:'#344054' };
const TINT = { blue:'#E8F5FF', indigo:'#EEF0FF', emerald:'#E7F8F1', amber:'#FEF4E2',
               violet:'#F8EDFE', slate:'#EEF1F5' };

/* ---------------- hero loom ---------------- */
(function loom () {
  const warp = $('#warp'), weft = $('#weft'), knots = $('#knots');
  if (!warp) return;
  const N = 9, pad = 26, span = 420 - pad * 2, gap = span / (N - 1);
  const ns = 'http://www.w3.org/2000/svg';
  for (let i = 0; i < N; i++) {
    const p = pad + i * gap;
    const a = document.createElementNS(ns, 'line');
    a.setAttribute('x1', p); a.setAttribute('y1', pad);
    a.setAttribute('x2', p); a.setAttribute('y2', 420 - pad);
    a.setAttribute('class', 'warp');
    a.style.animationDelay = (i * 0.055) + 's';
    warp.appendChild(a);
    const b = document.createElementNS(ns, 'line');
    b.setAttribute('x1', pad); b.setAttribute('y1', p);
    b.setAttribute('x2', 420 - pad); b.setAttribute('y2', p);
    b.setAttribute('class', 'weft');
    b.style.animationDelay = (0.22 + i * 0.055) + 's';
    weft.appendChild(b);
  }
  // interlace: alternate crossings put the warp over the weft
  const inter = document.createElementNS(ns, 'g');
  inter.setAttribute('id', 'interlace');
  weft.after(inter);
  for (let i = 0; i < N; i++) for (let j2 = 0; j2 < N; j2++) {
    if ((i + j2) % 2) continue;
    const x = pad + i * gap, y = pad + j2 * gap;
    const r = document.createElementNS(ns, 'rect');
    r.setAttribute('x', x - 5.5); r.setAttribute('y', y - 2.6);
    r.setAttribute('width', 11); r.setAttribute('height', 5.2);
    r.setAttribute('fill', '#FBFCFD');
    const l = document.createElementNS(ns, 'line');
    l.setAttribute('x1', x); l.setAttribute('y1', y - 6.5);
    l.setAttribute('x2', x); l.setAttribute('y2', y + 6.5);
    l.setAttribute('stroke', '#A9BDCE'); l.setAttribute('stroke-width', 1.4);
    inter.appendChild(r); inter.appendChild(l);
  }
  inter.style.opacity = '0';
  inter.style.animation = 'knotIn .6s .85s forwards';

  // citation knots land where a source thread meets a question thread
  const spots = [[2,3],[5,2],[3,6],[7,5],[6,7],[1,6],[4,4],[7,2]];
  spots.forEach((s, i) => {
    const g = document.createElementNS(ns, 'g');
    g.setAttribute('class', 'knot');
    g.style.animationDelay = (0.95 + i * 0.075) + 's';
    const c = document.createElementNS(ns, 'circle');
    c.setAttribute('cx', pad + s[0] * gap); c.setAttribute('cy', pad + s[1] * gap);
    c.setAttribute('r', 4.2);
    c.setAttribute('fill', i % 3 === 0 ? '#F53E5A' : '#0086E6');
    if (!RM && i % 2 === 0) c.setAttribute('class', 'pulse');
    const h = document.createElementNS(ns, 'circle');
    h.setAttribute('cx', pad + s[0] * gap); h.setAttribute('cy', pad + s[1] * gap);
    h.setAttribute('r', 10); h.setAttribute('fill', i % 3 === 0 ? '#F53E5A' : '#0086E6');
    h.setAttribute('opacity', '.12');
    g.appendChild(h); g.appendChild(c); knots.appendChild(g);
  });
})();

/* ---------------- problem ---------------- */
const PROBS = [
  ['Slow', 'Answers are slow', 'The document exists; finding the right revision of it does not fit inside the decision window.'],
  ['Split', 'Answers disagree', 'Two sites, two teams or two languages give different answers to the same question.'],
  ['Opaque', 'Answers can\u2019t be defended', 'When an auditor asks where an answer came from, nobody can reconstruct the trail.'],
  ['Leaks', 'Knowledge walks out', 'Institutional memory leaves with the people who hold it, and nothing records what was lost.'],
  ['Blind', 'Gaps stay invisible', 'Nobody knows which questions the organisation cannot answer until it matters.']
];
PROBS.forEach(p => $('#probs').appendChild(
  el('div', 'prob', `<i>${p[0]}</i><b>${p[1]}</b><span>${p[2]}</span>`)));

/* ---------------- scrollytelling: stage art ---------------- */
const SVGW = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 344" fill="none"';
const ART = {
  question: `<svg ${SVGW}><g stroke="#C3D2DF" stroke-width="1.4">
    <rect x="72" y="118" width="256" height="108" rx="16"/></g>
    <circle cx="104" cy="172" r="15" fill="#EEF0FF"/><path d="M99 172h10M104 167v10" stroke="#4338CA" stroke-width="1.8" stroke-linecap="round"/>
    <rect x="132" y="160" width="140" height="8" rx="4" fill="#DCE6EF"/>
    <rect x="132" y="176" width="96" height="8" rx="4" fill="#E8EEF4"/>
    <g opacity=".9"><rect x="66" y="248" width="74" height="26" rx="13" fill="#EEF0FF"/>
    <text x="103" y="265" font-family="JetBrains Mono,monospace" font-size="10" fill="#4338CA" text-anchor="middle">role</text>
    <rect x="150" y="248" width="94" height="26" rx="13" fill="#EEF0FF"/>
    <text x="197" y="265" font-family="JetBrains Mono,monospace" font-size="10" fill="#4338CA" text-anchor="middle">language</text>
    <rect x="254" y="248" width="80" height="26" rx="13" fill="#EEF0FF"/>
    <text x="294" y="265" font-family="JetBrains Mono,monospace" font-size="10" fill="#4338CA" text-anchor="middle">intent</text></g></svg>`,

  access: `<svg ${SVGW}>
    <g stroke="#C3D2DF" stroke-width="1.4">
      <rect x="40" y="70" width="92" height="58" rx="10"/><rect x="40" y="146" width="92" height="58" rx="10"/>
      <rect x="40" y="222" width="92" height="58" rx="10"/></g>
    <rect x="40" y="146" width="92" height="58" rx="10" fill="#E7F8F1" stroke="#047857" stroke-width="1.6"/>
    <path d="M132 99h58M132 175h58M132 251h58" stroke="#C3D2DF" stroke-width="1.4" stroke-dasharray="4 4"/>
    <rect x="190" y="60" width="14" height="230" rx="7" fill="#EEF0FF" stroke="#4338CA" stroke-width="1.4"/>
    <circle cx="197" cy="175" r="9" fill="#047857"/><path d="m193 175 3 3 5.5-6" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="197" cy="99" r="9" fill="#fff" stroke="#C3D2DF" stroke-width="1.6"/>
    <path d="m194 96 6 6M200 96l-6 6" stroke="#94A6B8" stroke-width="1.6" stroke-linecap="round"/>
    <circle cx="197" cy="251" r="9" fill="#fff" stroke="#C3D2DF" stroke-width="1.6"/>
    <path d="m194 248 6 6M200 248l-6 6" stroke="#94A6B8" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M204 175h56" stroke="#047857" stroke-width="1.8"/>
    <rect x="260" y="150" width="100" height="50" rx="10" fill="#fff" stroke="#047857" stroke-width="1.6"/>
    <text x="310" y="180" font-family="JetBrains Mono,monospace" font-size="10.5" fill="#047857" text-anchor="middle">searchable</text></svg>`,

  retrieve: `<svg ${SVGW}>
    <text x="88" y="72" font-family="JetBrains Mono,monospace" font-size="10" fill="#6A7F94" text-anchor="middle">MEANING</text>
    <text x="312" y="72" font-family="JetBrains Mono,monospace" font-size="10" fill="#6A7F94" text-anchor="middle">EXACT TERM</text>
    <g stroke="#C3D2DF" stroke-width="1.4">
      <rect x="34" y="88" width="108" height="26" rx="6"/><rect x="34" y="122" width="108" height="26" rx="6"/>
      <rect x="34" y="156" width="108" height="26" rx="6"/>
      <rect x="258" y="88" width="108" height="26" rx="6"/><rect x="258" y="122" width="108" height="26" rx="6"/>
      <rect x="258" y="156" width="108" height="26" rx="6"/></g>
    <rect x="34" y="88" width="108" height="26" rx="6" fill="#E8F5FF" stroke="#0086E6" stroke-width="1.5"/>
    <rect x="258" y="122" width="108" height="26" rx="6" fill="#E8F5FF" stroke="#0086E6" stroke-width="1.5"/>
    <path d="M142 101c40 0 40 78 56 78M366 135c-40 0-40 44-58 44" stroke="#0086E6" stroke-width="1.6"/>
    <path d="M142 135c34 0 34 50 56 50M366 101c-34 0-34 84-58 84" stroke="#C3D2DF" stroke-width="1.3" stroke-dasharray="4 4"/>
    <rect x="128" y="196" width="144" height="46" rx="11" fill="#0086E6"/>
    <text x="200" y="224" font-family="JetBrains Mono,monospace" font-size="11" fill="#fff" text-anchor="middle">RANK FUSION</text>
    <g stroke="#C3D2DF" stroke-width="1.4">
      <rect x="128" y="258" width="144" height="20" rx="5" fill="#fff"/>
      <rect x="140" y="286" width="120" height="18" rx="5" fill="#fff"/></g>
    <rect x="128" y="258" width="144" height="20" rx="5" fill="#E8F5FF" stroke="#0086E6" stroke-width="1.4"/></svg>`,

  ground: `<svg ${SVGW}>
    <path d="M200 44 132 72v54c0 41 29 79 68 91 39-12 68-50 68-91V72z" fill="#FEF4E2" stroke="#DC6803" stroke-width="1.8"/>
    <path d="M176 126l19 20 37-41" stroke="#DC6803" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="86" y="244" font-family="JetBrains Mono,monospace" font-size="10" fill="#6A7F94">evidence strength</text>
    <rect x="86" y="256" width="228" height="10" rx="5" fill="#EEF1F5"/>
    <rect x="86" y="256" width="168" height="10" rx="5" fill="#DC6803"/>
    <path d="M254 248v26" stroke="#0A1626" stroke-width="1.6" stroke-dasharray="3 3"/>
    <text x="254" y="292" font-family="JetBrains Mono,monospace" font-size="10" fill="#0A1626" text-anchor="middle">threshold</text></svg>`,

  generate: `<svg ${SVGW}>
    <g stroke="#C3D2DF" stroke-width="1.4">
      <rect x="30" y="94" width="80" height="56" rx="9"/><rect x="30" y="166" width="80" height="56" rx="9"/></g>
    <path d="M110 122h44M110 194h30c8 0 14-6 14-14v-44" stroke="#0086E6" stroke-width="1.6"/>
    <rect x="154" y="86" width="216" height="150" rx="14" fill="#fff" stroke="#0086E6" stroke-width="1.8"/>
    <rect x="174" y="112" width="140" height="9" rx="4.5" fill="#DCE6EF"/>
    <rect x="322" y="112" width="30" height="9" rx="4.5" fill="#0086E6"/>
    <rect x="174" y="134" width="112" height="9" rx="4.5" fill="#DCE6EF"/>
    <rect x="294" y="134" width="30" height="9" rx="4.5" fill="#0086E6"/>
    <rect x="174" y="156" width="152" height="9" rx="4.5" fill="#DCE6EF"/>
    <rect x="174" y="186" width="70" height="22" rx="11" fill="#E8F5FF"/>
    <text x="209" y="201" font-family="JetBrains Mono,monospace" font-size="9.5" fill="#01517F" text-anchor="middle">SOP-04 p.12</text>
    <rect x="252" y="186" width="70" height="22" rx="11" fill="#E8F5FF"/>
    <text x="287" y="201" font-family="JetBrains Mono,monospace" font-size="9.5" fill="#01517F" text-anchor="middle">POL-11 p.3</text>
    <text x="30" y="262" font-family="JetBrains Mono,monospace" font-size="10" fill="#6A7F94">nothing enters that wasn\u2019t retrieved</text></svg>`,

  scored: `<svg ${SVGW}>
    <rect x="56" y="70" width="288" height="150" rx="14" fill="#fff" stroke="#C3D2DF" stroke-width="1.5"/>
    <rect x="80" y="98" width="180" height="9" rx="4.5" fill="#DCE6EF"/>
    <rect x="80" y="120" width="220" height="9" rx="4.5" fill="#DCE6EF"/>
    <rect x="80" y="142" width="132" height="9" rx="4.5" fill="#DCE6EF"/>
    <rect x="80" y="176" width="76" height="22" rx="11" fill="#F8EDFE"/>
    <text x="118" y="191" font-family="JetBrains Mono,monospace" font-size="9.5" fill="#6B21A8" text-anchor="middle">2 sources</text>
    <circle cx="200" cy="268" r="40" fill="none" stroke="#EEF1F5" stroke-width="9"/>
    <circle cx="200" cy="268" r="40" fill="none" stroke="#9333EA" stroke-width="9" stroke-linecap="round"
      stroke-dasharray="251" stroke-dashoffset="46" transform="rotate(-90 200 268)"/>
    <text x="200" y="266" font-family="Inter,sans-serif" font-weight="600" font-size="17" fill="#6B21A8" text-anchor="middle">HIGH</text>
    <text x="200" y="284" font-family="JetBrains Mono,monospace" font-size="9" fill="#9CA9B8" text-anchor="middle">CONFIDENCE</text></svg>`
};

const STEPS = [
  ['question', 'Question', 'A user asks in ordinary words \u2014 no query syntax, no document numbers. The request carries their role and language with it, so both the search and the answer are shaped for who is asking.', 'Plain language in. No training required.'],
  ['access', 'Access scope', 'Permissions are applied before ranking, not after. Content the user is not entitled to never enters the candidate set, so it cannot shape a result or be inferred from one.', 'Gate one \u2014 unauthorised material never reaches the search.'],
  ['retrieve', 'Retrieve', 'A meaning-based search and an exact-term search run at the same time, and their two ranked lists are merged. Filters keep superseded and draft material out unless it is explicitly requested.', 'Two retrievers disagreeing is itself a useful signal.'],
  ['ground', 'Grounding check', 'Before anything is written, the evidence is scored against a threshold: how strongly the sources agree, how well they cover the question, how clearly the best result separates from the rest.', 'Gate two \u2014 passing this is what authorises generation.'],
  ['generate', 'Generate', 'The answer is composed from the retrieved passages and nothing else, in the language the question was asked in. Citations attach as the answer is written, not afterwards.', 'No general world knowledge enters the answer.'],
  ['scored', 'Scored answer', 'The user receives the answer, the sources behind each claim, and a plain confidence level. Confidence is shown on screen, never buried in a log.', 'The reader decides how much weight to place on it.']
];

(function story () {
  const stage = $('#stage'), steps = $('#steps');
  if (!stage) return;
  STEPS.forEach((s, i) => {
    stage.insertAdjacentHTML('beforeend', ART[s[0]].replace('<svg ', `<svg data-art="${i}" `));
    steps.appendChild(el('article', 'step' + (i === 0 ? ' on' : ''),
      `<div class="n">STAGE ${String(i + 1).padStart(2, '0')} / 06</div>
       <h3>${s[1]}</h3><p>${s[2]}</p><div class="tag">${s[3]}</div>`));
  });
  const arts = [...stage.querySelectorAll('svg')];
  const nodes = [...steps.children];
  arts[0].classList.add('on');
  const io = new IntersectionObserver(es => {
    es.forEach(e => {
      if (!e.isIntersecting) return;
      const i = nodes.indexOf(e.target);
      nodes.forEach((n, k) => n.classList.toggle('on', k === i));
      arts.forEach((a, k) => a.classList.toggle('on', k === i));
    });
  }, { rootMargin: '-46% 0px -46% 0px' });
  nodes.forEach(n => io.observe(n));
})();

/* ---------------- clarify-back turns ---------------- */
const TURNS = [
  ['sys', 'Evidence check', 'Grounding score fell below the threshold. Two candidate sources disagree on scope.'],
  ['ask', 'System asks', 'Which process area do you mean \u2014 incoming inspection, or in-process control? One question, never an interrogation.'],
  ['user', 'User replies', 'In-process control.'],
  ['sys', 'Answer', 'The refined query lifts the evidence above the threshold. The answer proceeds normally, fully cited \u2014 and the clarification is logged as a content gap.']
];
TURNS.forEach((t, i) => {
  const n = el('div', 'turn' + (t[0] === 'sys' ? ' sys' : ''),
    `<div class="who">${t[1]}</div><p${i === 1 ? ' class="typing"' : ''}>${t[2]}</p>`);
  $('#loopDemo').appendChild(n);
});

/* ---------------- architecture zones ---------------- */
const ZONES = [
  { n:'Access and roles', hue:'indigo', cap:'who can ask, and what they may see', full:true,
    items:['Roles from your directory','Branded chat with citations','Federated single sign-on','Role checks on every route'] },
  { n:'Content pipeline', hue:'emerald', cap:'source of record to index',
    items:['Source of record','Event-driven intake','Extract and rank','Curate and resolve','Incremental index sync'] },
  { n:'Grounded answering', hue:'blue', cap:'the answer is assembled here',
    items:['Retrieve','Grounding check','Generate','Clarify-back'] },
  { n:'Trust and telemetry', hue:'violet', cap:'proof that it worked',
    items:['Per-answer scoring','Tracing','Usage, cost and quality','Audit and export'] },
  { n:'Security and operations', hue:'slate', cap:'underpins every zone above', full:true,
    items:['Private networking','Key management','Least privilege','Infrastructure as code'] }
];
(function arch () {
  const host = $('#zones');
  const mk = z => {
    const d = el('div', 'zone');
    d.style.borderColor = HUE[z.hue] + '55';
    d.innerHTML = `<div class="zhead" style="background:${HUE[z.hue]}">${z.n}</div>
      <div class="zcap">${z.cap}</div>
      <ul class="zbody" style="color:${HUE[z.hue]}">${z.items.map(i => `<li>${i}</li>`).join('')}</ul>`;
    return d;
  };
  const top = el('div', 'zrow'); top.appendChild(mk(ZONES[0])); host.appendChild(top);
  host.appendChild(el('div', 'flowline'));
  const mid = el('div', 'zrow');
  [1, 2, 3].forEach(i => mid.appendChild(mk(ZONES[i])));
  host.appendChild(mid);
  host.appendChild(el('div', 'flowline'));
  const bot = el('div', 'zrow'); bot.appendChild(mk(ZONES[4])); host.appendChild(bot);
})();

/* ---------------- capabilities ---------------- */
const ICO = {
  answer:'<path d="M4 5.6A2.2 2.2 0 0 1 6.2 3.4h11.6A2.2 2.2 0 0 1 20 5.6v7.6a2.2 2.2 0 0 1-2.2 2.2H9.2L4 19.6z"/>',
  cite:'<path d="M14 3H7.4A2.4 2.4 0 0 0 5 5.4v13.2A2.4 2.4 0 0 0 7.4 21h9.2a2.4 2.4 0 0 0 2.4-2.4V8z"/><path d="M14 3v5h5"/><path d="M8.6 13h6.8M8.6 16.4h4.6"/>',
  gauge:'<path d="M3.8 17.6a8.6 8.6 0 1 1 16.4 0"/><path d="m12 17.6 4.3-5.1"/><circle cx="12" cy="17.6" r="1.4"/>',
  ask:'<circle cx="12" cy="12" r="8.6"/><path d="M10.2 9.6a2 2 0 1 1 2.4 2.4c-.5.2-.8.6-.8 1.1v.4M12 16.2h.01"/>',
  graph:'<circle cx="12" cy="5" r="2.4"/><circle cx="5" cy="19" r="2.4"/><circle cx="19" cy="19" r="2.4"/><path d="M12 7.4v4.2M12 11.6 6.4 17M12 11.6 17.6 17"/>',
  health:'<path d="M2.8 12.4h4.1l2.6-7.1 4.1 14.2 2.6-7.1h5"/>',
  version:'<path d="M3.6 12a8.4 8.4 0 0 1 14.4-5.9l2.4 2.3"/><path d="M20.4 4v4.4H16"/><path d="M20.4 12a8.4 8.4 0 0 1-14.4 5.9L3.6 15.6"/><path d="M3.6 20v-4.4H8"/>',
  lang:'<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/><path d="M12 3.4a13 13 0 0 1 0 17.2 13 13 0 0 1 0-17.2"/>',
  curate:'<circle cx="9.4" cy="8" r="3.4"/><path d="M3.6 19.6c0-3.2 2.6-5.5 5.8-5.5.9 0 1.8.2 2.6.5"/><path d="m14.8 17.2 2.1 2.1 4.1-4.2"/>',
  lock:'<rect x="4.6" y="10.4" width="14.8" height="10.2" rx="2.2"/><path d="M8 10.4V7.6a4 4 0 0 1 8 0v2.8"/>',
  chart:'<path d="M3.8 20.6h16.4"/><path d="M6.6 20.6v-6.2M11.4 20.6V5.4M16.2 20.6v-9.4"/>',
  api:'<path d="M9 4.5C7 4.5 7 8 7 9.6S5.6 12 4.6 12c1 0 2.4.4 2.4 2.4S7 19.5 9 19.5"/><path d="M15 4.5c2 0 2 3.5 2 5.1s1.4 2.4 2.4 2.4c-1 0-2.4.4-2.4 2.4s0 5.1-2 5.1"/>'
};
const CAPS = [
  ['answer','blue','Grounded answering','Plain-language answers assembled only from approved sources, never from general world knowledge.','Everyone'],
  ['cite','emerald','Verbatim citation','Each claim carries its source, down to document, page and paragraph.','Quality · audit · legal'],
  ['gauge','violet','Confidence scoring','A visible high, medium or low level on every answer, derived from evidence strength.','Everyone'],
  ['ask','amber','Clarify-back','One targeted question when evidence is thin, instead of a refusal or a guess.','Everyone'],
  ['graph','indigo','Relationship graph','Explore how products, processes, regulations and records connect to one another.','Engineering · quality'],
  ['health','violet','Knowledge health','Coverage, connectivity, provenance, quality and freshness, with gaps ranked.','Content owners'],
  ['version','emerald','Version awareness','Current revisions outrank superseded ones; drafts stay out unless requested.','Quality · operations'],
  ['lang','blue','Query & answer translation','Ask in French, Spanish or Japanese and the answer comes back in kind \u2014 sources stay as written. Live in every demonstration.','Global operations'],
  ['curate','emerald','Curator workbench','A human queue for conflicts, duplicates and superseded documents.','Content owners'],
  ['lock','slate','Role-scoped access','Permissions applied before ranking, so unauthorised content never enters a result.','Security · IT'],
  ['chart','violet','Usage dashboards','Consumption, question categories, clarification and refusal rates over time.','Sponsors · IT'],
  ['api','indigo','APIs and embedding','The answer flow exposed to other applications through a governed interface.','IT · product teams']
];
CAPS.forEach(c => {
  const n = el('div', 'cap');
  n.innerHTML = `<div class="ci" style="background:${TINT[c[1]]}">
    <svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="${HUE[c[1]]}"
      stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICO[c[0]]}</svg></div>
    <b>${c[2]}</b><span>${c[3]}</span><em>${c[4]}</em>`;
  $('#capsGrid').appendChild(n);
});

/* ---------------- coverage ---------------- */
const CHIPS_A = ['Standard operating procedures','Work instructions','Policies','Specifications',
  'Manuals','Validation records','Audit findings','Contracts','Training material','Test reports',
  'Change records','Correspondence'];
const CHIPS_B = ['Document management','Quality systems','Product lifecycle','Ticketing',
  'Service desk','Wikis and intranets','Shared drives','Regulatory registries','Scanned archives',
  'Structured exports'];
const fill = (id, arr) => {
  const t = $(id);
  [...arr, ...arr].forEach(c => t.appendChild(el('span', 'chipx', c)));
};
fill('#marqA', CHIPS_A); fill('#marqB', CHIPS_B);

const COV = [
  ['blue','Formats','Word documents, plain text, spreadsheets and readable PDFs — including PDFs with tables and embedded images. Formats beyond these are scoped as their own effort, openly.'],
  ['emerald','Functions','Quality and compliance, engineering and manufacturing, service and support, operations, procurement, legal, and people functions.'],
  ['indigo','Languages','English-first by design; the question and the answer are translated for a quality-validated list. Try it live \u2014 every demonstration answers in EN, FR, ES and \u65e5\u672c\u8a9e.'],
  ['violet','Question shapes','Factual lookup, procedural how-to, comparison across documents, status and version checks, and relationship questions across entities.']
];
COV.forEach(c => $('#cov').appendChild(el('div', '',
  `<div class="bar" style="background:${HUE[c[0]]}"></div><h4>${c[1]}</h4><p>${c[2]}</p>`)));

/* ---------------- value ---------------- */
const VALUE = [
  ['blue','Frontline and operations',['The current, approved answer arrives in seconds instead of after a search through revisions.','The same question gets the same answer across sites, shifts and languages.','New joiners become productive without a colleague acting as their search index.']],
  ['emerald','Quality, compliance and audit',['Every answer can be reconstructed to the document, page and paragraph it came from.','Superseded revisions stop circulating as if they were current.','The refusal and clarification record shows exactly where documented knowledge is thin.']],
  ['indigo','Engineering and technical teams',['Relationships between products, processes and records become explorable rather than tribal.','Prior work, decisions and test evidence surface at the moment they are relevant.','Time spent reconstructing context is returned to engineering work.']],
  ['violet','Leadership and sponsors',['Institutional memory becomes an asset the organisation holds, not one its people carry.','Consumption and quality are visible, so the platform can be governed on evidence.','Knowledge gaps arrive as a ranked backlog, turning content work into a prioritised plan.']],
  ['slate','IT and security',['Identity, permissions and network controls are the ones you already operate.','Content stays inside your boundary; residency and retention follow existing policy.','No component is a lock-in \u2014 model, vector store and cloud are all substitutable.']]
];
VALUE.forEach(v => {
  const n = el('div', 'vcol');
  n.innerHTML = `<h4 style="color:${HUE[v[0]]}">${v[1]}</h4><ul>` +
    v[2].map(p => `<li style="--d:${HUE[v[0]]}">${p}</li>`).join('') + '</ul>';
  n.querySelectorAll('li').forEach(li => li.style.setProperty('--d', HUE[v[0]]));
  $('#valGrid').appendChild(n);
});
document.querySelectorAll('.vcol li').forEach(li => {
  const c = li.style.getPropertyValue('--d');
  li.insertAdjacentHTML('afterbegin', '');
  li.style.setProperty('background-image', 'none');
});
const st = document.createElement('style');
st.textContent = '.vcol li::before{background:var(--d)}';
document.head.appendChild(st);

/* ---------------- phases ---------------- */
const PH = [
  ['indigo','Phase 01','Discover','Corpus assessment and use-case selection. We inventory the candidate content, test how well it is structured, identify the questions that matter most, and agree what a good answer looks like.','Content readiness assessment, prioritised question set, target architecture.'],
  ['blue','Phase 02','Prove','A working pilot on one domain and one audience, with real content and real users. Ontology, filters and thresholds are tuned against the prioritised question set.','Working platform on live content, measured answer quality, curator workflow in use.'],
  ['emerald','Phase 03','Harden','Production readiness: identity integration, permission mapping, security review, telemetry and dashboards, operational runbooks and release automation.','Production deployment inside your control environment, with governance in place.'],
  ['violet','Phase 04','Extend','Additional domains, languages and audiences, driven by the ranked gap backlog the platform itself produces. Continuous curation replaces one-off content projects.','Expanding coverage, improving health scores, a content plan grounded in real demand.']
];
PH.forEach(p => {
  const n = el('div', 'ph');
  n.innerHTML = `<div class="dot" style="border-color:${HUE[p[0]]}"></div>
    <div class="k">${p[1]}</div><h4 style="color:${HUE[p[0]]}">${p[2]}</h4>
    <p>${p[3]}</p><div class="out">${p[4]}</div>`;
  $('#plist').appendChild(n);
});

/* ---------------- differentiators ---------------- */
const DIFF = [
  ['Generation is gated, not trusted','The grounding check runs before anything is written. Citation is a property of the design, not a promise about behaviour.'],
  ['Clarification instead of refusal','Thin evidence produces a targeted question and a second attempt, recovering answers a refusal would have discarded.'],
  ['Permissions before ranking','Unauthorised content never enters the candidate set, so it cannot shape a result or be inferred from one.'],
  ['The system reports its own gaps','Failed and clarified questions become a ranked content backlog, so the corpus improves from real demand.'],
  ['Portable by construction','Model, vector store, embedding and identity are deployment choices. None of them is the product.']
];
DIFF.forEach((d, i) => $('#diffs').appendChild(el('div', 'diff',
  `<span class="num">${String(i + 1).padStart(2, '0')}</span><b>${d[0]}</b><span>${d[1]}</span>`)));

/* ---------------- reveal + rail ---------------- */
const rv = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); rv.unobserve(e.target); }
}), { rootMargin: '0px 0px -12% 0px' });
document.querySelectorAll('.rv').forEach(n => rv.observe(n));

const btns = [...document.querySelectorAll('.rail button')];
btns.forEach(b => b.addEventListener('click', () => {
  const t = document.getElementById(b.dataset.go);
  if (t) t.scrollIntoView({ behavior: RM ? 'auto' : 'smooth', block: 'start' });
}));
const secs = btns.map(b => document.getElementById(b.dataset.go)).filter(Boolean);
const railIO = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return;
  const i = secs.indexOf(e.target);
  btns.forEach((b, k) => b.setAttribute('aria-current', String(k === i)));
}), { rootMargin: '-45% 0px -50% 0px' });
secs.forEach(s => railIO.observe(s));
})();
