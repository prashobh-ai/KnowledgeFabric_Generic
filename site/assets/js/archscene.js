/* Knowledge Fabric — the animated answer journey.
 *
 * One 16-second loop that a non-technical audience can read without a
 * narrator: a question enters, permissions are checked BEFORE search, the
 * evidence gate refuses to let generation start, the system asks one
 * clarifying question, the refined retrieval passes the gate, and a cited,
 * confidence-scored answer lands — while telemetry files the gap it noticed
 * into the content backlog. The two gates and the loop ARE the pitch; the
 * animation exists so the audience watches them happen instead of being told.
 *
 * Self-contained on purpose: injects its own <style> and SVG, no libraries,
 * animates only transform/opacity/stroke-dashoffset, honours
 * prefers-reduced-motion (the scene renders as its final frame), and carries
 * a pause control. Mount with ArchScene.mount(el) or data-archscene.
 */
(function () {
  "use strict";

  var T = 16; /* master loop, seconds */

  /* Keyframe helper: percentages of the master loop. */
  function pct(s) { return (s / T * 100).toFixed(2) + "%"; }

  var CSS = ""
  + ".as-wrap{position:relative;font-family:'Inter',system-ui,sans-serif}"
  + ".as-wrap svg{width:100%;height:auto;display:block;overflow:visible}"
  + "@media(max-width:760px){.as-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}.as-wrap svg{min-width:880px}}"
  + ".as-panel{fill:#fff;stroke:#DFE7EE;rx:14}"
  + ".as-band{rx:12}"
  + ".as-zlabel{font:600 12.5px 'JetBrains Mono',ui-monospace,monospace;letter-spacing:.14em}"
  + ".as-sub{font:400 11px 'Inter',system-ui,sans-serif;fill:#93A6B8}"
  + ".as-node{fill:#F7FAFC;stroke:#DFE7EE}"
  + ".as-nlabel{font:600 12.5px 'Inter',system-ui,sans-serif;fill:#22374D}"
  + ".as-small{font:400 10.5px 'JetBrains Mono',ui-monospace,monospace;fill:#6A7F94}"
  + ".as-chip{font:500 11.5px 'Inter',system-ui,sans-serif}"
  /* ---- caption strip ---- */
  + ".as-cap{margin-top:14px;min-height:2.2em;position:relative}"
  + ".as-cap span{position:absolute;inset:0;display:flex;align-items:center;gap:10px;"
  +   "font:500 14px 'Inter',system-ui,sans-serif;color:#22374D;opacity:0}"
  + ".as-cap i{font-style:normal;font:600 10px 'JetBrains Mono',monospace;letter-spacing:.12em;"
  +   "color:#fff;border-radius:999px;padding:3px 9px}"
  /* ---- pause control ---- */
  + ".as-pause{position:absolute;top:10px;right:10px;z-index:2;border:1px solid #DFE7EE;"
  +   "background:#fff;border-radius:8px;font:600 10.5px 'JetBrains Mono',monospace;"
  +   "letter-spacing:.08em;color:#6A7F94;padding:5px 10px;cursor:pointer}"
  + ".as-pause:hover{color:#0086E6;border-color:#0086E6}"
  + ".as-paused *{animation-play-state:paused!important}"
  /* ==== persistent pulses ==== */
  + "@keyframes asBreathe{0%,100%{opacity:.35}50%{opacity:1}}"
  + ".as-live{animation:asBreathe 2.6s ease-in-out infinite}"
  /* ==== the journey (all share the 16s clock) ==== */
  + "@keyframes asQ{"
  +   "0%{transform:translate(300px,6px);opacity:0}"
  +   pct(0.6) + "{transform:translate(300px,46px);opacity:1}"
  +   pct(1.6) + "{transform:translate(420px,46px);opacity:1}"    /* to access check */
  +   pct(2.4) + "{transform:translate(420px,46px);opacity:1}"    /* held at gate */
  +   pct(3.4) + "{transform:translate(470px,205px);opacity:1}"   /* into retrieve */
  +   pct(4.0) + "{transform:translate(470px,205px);opacity:0}"
  +   "100%{transform:translate(470px,205px);opacity:0}}"
  + ".as-q{animation:asQ " + T + "s cubic-bezier(.4,0,.2,1) infinite}"
  + "@keyframes asTick{0%," + pct(1.7) + "{opacity:0;transform:scale(.4)}"
  +   pct(2.1) + "{opacity:1;transform:scale(1.15)}" + pct(2.5) + "{opacity:1;transform:scale(1)}"
  +   pct(5) + "{opacity:1}" + pct(6) + ",100%{opacity:0;transform:scale(1)}}"
  + ".as-tick{animation:asTick " + T + "s ease infinite;transform-origin:472px 46px}"
  /* passages fly from the index into retrieve — first thin harvest */
  + "@keyframes asP1{0%," + pct(3.2) + "{transform:translate(238px,332px);opacity:0}"
  +   pct(3.5) + "{opacity:1}" + pct(4.4) + "{transform:translate(452px,232px);opacity:0}100%{opacity:0}}"
  + "@keyframes asP2{0%," + pct(3.5) + "{transform:translate(238px,362px);opacity:0}"
  +   pct(3.8) + "{opacity:1}" + pct(4.7) + "{transform:translate(452px,238px);opacity:0}100%{opacity:0}}"
  /* second, richer harvest after the clarification */
  + "@keyframes asP3{0%," + pct(8.2) + "{transform:translate(238px,332px);opacity:0}"
  +   pct(8.5) + "{opacity:1}" + pct(9.3) + "{transform:translate(452px,228px);opacity:0}100%{opacity:0}}"
  + "@keyframes asP4{0%," + pct(8.45) + "{transform:translate(238px,352px);opacity:0}"
  +   pct(8.75) + "{opacity:1}" + pct(9.55) + "{transform:translate(452px,236px);opacity:0}100%{opacity:0}}"
  + "@keyframes asP5{0%," + pct(8.7) + "{transform:translate(238px,372px);opacity:0}"
  +   pct(9.0) + "{opacity:1}" + pct(9.8) + "{transform:translate(452px,244px);opacity:0}100%{opacity:0}}"
  + ".as-p1{animation:asP1 " + T + "s ease-in infinite}"
  + ".as-p2{animation:asP2 " + T + "s ease-in infinite}"
  + ".as-p3{animation:asP3 " + T + "s ease-in infinite}"
  + ".as-p4{animation:asP4 " + T + "s ease-in infinite}"
  + ".as-p5{animation:asP5 " + T + "s ease-in infinite}"
  /* evidence meter: thin fill, hold, then full fill after clarify */
  + "@keyframes asMeter{0%," + pct(3.4) + "{transform:scaleX(0)}"
  +   pct(4.6) + "," + pct(8.4) + "{transform:scaleX(.34)}"
  +   pct(9.9) + ",100%{transform:scaleX(.9)}}"
  + ".as-meter{transform-origin:585px 296px;animation:asMeter " + T + "s cubic-bezier(.2,.8,.2,1) infinite}"
  + "@keyframes asMeterAmber{0%," + pct(3.4) + "{opacity:1}" + pct(9.9) + ",100%{opacity:0}}"
  + ".as-meter-amber{animation:asMeterAmber " + T + "s step-end infinite}"
  /* gate: amber refusal flash, then emerald pass */
  + "@keyframes asGateAmber{0%," + pct(4.4) + "{opacity:0}"
  +   pct(4.7) + "," + pct(5.6) + "{opacity:1}" + pct(8.6) + ",100%{opacity:0}}"
  + "@keyframes asGateGreen{0%," + pct(9.9) + "{opacity:0}" + pct(10.3) + "," + pct(14.6) + "{opacity:1}"
  +   pct(15.4) + ",100%{opacity:0}}"
  + ".as-gate-amber{animation:asGateAmber " + T + "s ease infinite}"
  + ".as-gate-green{animation:asGateGreen " + T + "s ease infinite}"
  + "@keyframes asHold{0%," + pct(4.5) + "{opacity:0}" + pct(4.8) + "," + pct(7.6) + "{opacity:1}"
  +   pct(8.2) + ",100%{opacity:0}}"
  + ".as-hold{animation:asHold " + T + "s ease infinite}"
  /* clarify-back: chip up to the user and reply back down */
  + "@keyframes asC1{0%," + pct(5.0) + "{transform:translate(640px,178px);opacity:0}"
  +   pct(5.3) + "{opacity:1}"
  +   pct(6.2) + "{transform:translate(340px,52px);opacity:1}"
  +   pct(6.8) + "{transform:translate(340px,52px);opacity:0}100%{opacity:0}}"
  + "@keyframes asC2{0%," + pct(6.9) + "{transform:translate(340px,52px);opacity:0}"
  +   pct(7.2) + "{opacity:1}"
  +   pct(8.1) + "{transform:translate(470px,205px);opacity:1}"
  +   pct(8.5) + "{transform:translate(470px,205px);opacity:0}100%{opacity:0}}"
  + ".as-c1{animation:asC1 " + T + "s cubic-bezier(.4,0,.2,1) infinite}"
  + ".as-c2{animation:asC2 " + T + "s cubic-bezier(.4,0,.2,1) infinite}"
  + "@keyframes asDash{0%," + pct(4.9) + "{opacity:0}" + pct(5.2) + "," + pct(8.0) + "{opacity:.9}"
  +   pct(8.6) + ",100%{opacity:0}}"
  + ".as-cpath{stroke-dasharray:5 6;animation:asDash " + T + "s ease infinite}"
  /* generation spark + answer card */
  + "@keyframes asGen{0%," + pct(10.0) + "{opacity:0;transform:scale(.6)}"
  +   pct(10.4) + "{opacity:1;transform:scale(1.15)}" + pct(10.8) + "{transform:scale(1)}"
  +   pct(14.8) + "{opacity:1}" + pct(15.5) + ",100%{opacity:0}}"
  + ".as-gen{animation:asGen " + T + "s ease infinite;transform-origin:790px 232px}"
  + "@keyframes asCard{0%," + pct(10.6) + "{opacity:0;transform:translateY(16px) scale(.96)}"
  +   pct(11.2) + "{opacity:1;transform:translateY(0) scale(1)}"
  +   pct(15.0) + "{opacity:1}" + pct(15.8) + ",100%{opacity:0}}"
  + ".as-card{animation:asCard " + T + "s cubic-bezier(.16,1,.3,1) infinite;transform-origin:600px 420px}"
  + "@keyframes asCite{0%," + pct(11.3) + "{opacity:0;transform:scale(.5)}"
  +   pct(11.7) + "{opacity:1;transform:scale(1)}" + pct(15.0) + "{opacity:1}"
  +   pct(15.8) + ",100%{opacity:0}}"
  + ".as-cite1{animation:asCite " + T + "s ease infinite;transform-origin:585px 458px}"
  + ".as-cite2{animation:asCite " + T + "s .18s ease infinite;transform-origin:668px 458px}"
  /* telemetry: pulse across, dial sweep, backlog particle home */
  + "@keyframes asTel{0%," + pct(11.2) + "{transform:translate(862px,300px);opacity:0}"
  +   pct(11.5) + "{opacity:1}" + pct(12.3) + "{transform:translate(962px,300px);opacity:0}100%{opacity:0}}"
  + ".as-tel{animation:asTel " + T + "s ease-in infinite}"
  + "@keyframes asDial{0%," + pct(11.6) + "{stroke-dashoffset:138}"
  +   pct(12.8) + "," + pct(15.0) + "{stroke-dashoffset:26}100%{stroke-dashoffset:138}}"
  + ".as-dial{stroke-dasharray:138;animation:asDial " + T + "s cubic-bezier(.2,.8,.2,1) infinite}"
  + "@keyframes asGap{0%," + pct(12.6) + "{transform:translate(1005px,468px);opacity:0}"
  +   pct(12.9) + "{opacity:1}"
  +   pct(13.6) + "{transform:translate(620px,530px);opacity:1}"
  +   pct(14.4) + "{transform:translate(238px,468px);opacity:1}"
  +   pct(14.8) + "{transform:translate(238px,420px);opacity:0}100%{opacity:0}}"
  + ".as-gap{animation:asGap " + T + "s cubic-bezier(.4,0,.2,1) infinite}"
  + "@keyframes asNewDoc{0%," + pct(14.4) + "{opacity:0;transform:translateX(-10px)}"
  +   pct(14.9) + "{opacity:1;transform:translateX(0)}" + pct(15.7) + ",100%{opacity:0}}"
  + ".as-newdoc{animation:asNewDoc " + T + "s ease infinite}"
  + "@keyframes asLoopPath{0%," + pct(12.5) + "{opacity:0}" + pct(12.9) + "," + pct(14.6) + "{opacity:.8}"
  +   pct(15.2) + ",100%{opacity:0}}"
  + ".as-looppath{stroke-dasharray:4 7;animation:asLoopPath " + T + "s ease infinite}"
  /* caption cycle */
  + "@keyframes asCap1{0%{opacity:0}" + pct(0.4) + "," + pct(2.9) + "{opacity:1}" + pct(3.5) + ",100%{opacity:0}}"
  + "@keyframes asCap2{0%," + pct(3.5) + "{opacity:0}" + pct(4.0) + "," + pct(4.9) + "{opacity:1}" + pct(5.4) + ",100%{opacity:0}}"
  + "@keyframes asCap3{0%," + pct(5.4) + "{opacity:0}" + pct(5.9) + "," + pct(9.3) + "{opacity:1}" + pct(9.9) + ",100%{opacity:0}}"
  + "@keyframes asCap4{0%," + pct(9.9) + "{opacity:0}" + pct(10.4) + "," + pct(12.2) + "{opacity:1}" + pct(12.8) + ",100%{opacity:0}}"
  + "@keyframes asCap5{0%," + pct(12.8) + "{opacity:0}" + pct(13.3) + "," + pct(15.2) + "{opacity:1}" + pct(15.9) + ",100%{opacity:0}}"
  + ".as-cap .c1{animation:asCap1 " + T + "s ease infinite}"
  + ".as-cap .c2{animation:asCap2 " + T + "s ease infinite}"
  + ".as-cap .c3{animation:asCap3 " + T + "s ease infinite}"
  + ".as-cap .c4{animation:asCap4 " + T + "s ease infinite}"
  + ".as-cap .c5{animation:asCap5 " + T + "s ease infinite}"
  ;
  /* Final-frame rules: gate passed, answer cited, backlog note visible, all
     travellers hidden, captions laid out statically. Applied for reduced
     motion AND print, so a Ctrl+P export never captures a mid-flight frame. */
  var STATIC = ""
  +   ".as-wrap [class^='as-'],.as-wrap [class*=' as-']{animation:none!important}"
  +   ".as-q,.as-tick,.as-p1,.as-p2,.as-p3,.as-p4,.as-p5,.as-c1,.as-c2,.as-cpath,"
  +   ".as-gate-amber,.as-hold,.as-tel,.as-gap,.as-newdoc,.as-looppath,.as-meter-amber{opacity:0!important}"
  +   ".as-gate-green,.as-gen,.as-card,.as-cite1,.as-cite2{opacity:1!important;transform:none!important}"
  +   ".as-meter{transform:scaleX(.9)!important}"
  +   ".as-dial{stroke-dashoffset:26!important}"
  +   ".as-cap span{position:static;opacity:1!important;margin-right:18px;display:inline-flex}"
  +   ".as-cap{display:flex;flex-wrap:wrap;gap:6px}"
  +   ".as-pause{display:none}";
  CSS += "@media (prefers-reduced-motion:reduce){" + STATIC + "}"
       + "@media print{" + STATIC + "}";

  function chip(x, y, w, label, fill, ink) {
    return "<g transform='translate(" + x + "," + y + ")'>"
      + "<rect x='" + (-w / 2) + "' y='-12' width='" + w + "' height='24' rx='12' fill='" + fill + "'/>"
      + "<text class='as-chip' x='0' y='4' text-anchor='middle' fill='" + ink + "'>" + label + "</text></g>";
  }

  var SVG = ""
  + "<svg viewBox='0 0 1200 660' role='img' aria-labelledby='asTitle asDesc'>"
  + "<title id='asTitle'>How Knowledge Fabric produces an answer</title>"
  + "<desc id='asDesc'>A question passes the permission check, retrieval gathers"
  + " evidence, the grounding gate refuses a weak first attempt, one clarifying"
  + " question comes back, the refined retrieval passes, and a cited answer is"
  + " delivered while the unanswered gap is filed into the content backlog.</desc>"

  /* ---------- ACCESS band ---------- */
  + "<rect class='as-band' x='20' y='16' width='1160' height='84' fill='#EEF0FF' stroke='#D6DAFB'/>"
  + "<text class='as-zlabel' x='44' y='45' fill='#4338CA'>ACCESS AND ROLES</text>"
  + "<text class='as-sub' x='44' y='64'>who may ask · what they may see</text>"
  + "<g transform='translate(300,58)'><circle r='16' fill='#fff' stroke='#C7CBF7'/>"
  +   "<circle cx='0' cy='-4' r='5' fill='#4338CA'/>"
  +   "<path d='M-8 8 Q0 -1 8 8' fill='#4338CA'/></g>"
  + "<text class='as-small' x='300' y='92' text-anchor='middle'>the person asking</text>"
  + "<g transform='translate(472,46)'><rect x='-62' y='-18' width='124' height='36' rx='18' fill='#fff' stroke='#C7CBF7'/>"
  +   "<text class='as-nlabel' x='0' y='4' text-anchor='middle' fill='#4338CA'>Role check</text></g>"
  + "<g class='as-tick'><circle cx='548' cy='34' r='11' fill='#047857'/>"
  +   "<path d='M543 34 l4 4 l7 -8' stroke='#fff' stroke-width='2.4' fill='none' stroke-linecap='round'/></g>"
  + "<text class='as-small' x='700' y='40'>permissions applied before anything is searched</text>"

  /* ---------- CONTENT PIPELINE ---------- */
  + "<rect class='as-panel' x='20' y='140' width='300' height='372' rx='14'/>"
  + "<rect x='20' y='140' width='300' height='6' rx='3' fill='#047857'/>"
  + "<text class='as-zlabel' x='44' y='178' fill='#047857'>CONTENT PIPELINE</text>"
  + "<text class='as-sub' x='44' y='197'>source of record → index</text>"
  + "<g class='as-live' style='animation-delay:.2s'><rect x='44' y='216' width='176' height='26' rx='6' fill='#E7F8F1'/><text class='as-small' x='56' y='233' fill='#047857'>SOP-04 · rev 12 · effective</text></g>"
  + "<g class='as-live' style='animation-delay:.9s'><rect x='44' y='250' width='176' height='26' rx='6' fill='#E7F8F1'/><text class='as-small' x='56' y='267' fill='#047857'>POL-11 · rev 3 · effective</text></g>"
  + "<g class='as-live' style='animation-delay:1.6s'><rect x='44' y='284' width='176' height='26' rx='6' fill='#E7F8F1'/><text class='as-small' x='56' y='301' fill='#047857'>WI-208 · rev 7 · effective</text></g>"
  + "<g class='as-newdoc'><rect x='44' y='318' width='176' height='26' rx='6' fill='#F8EDFE' stroke='#E2C4F8'/><text class='as-small' x='56' y='335' fill='#9333EA'>NEW — from the backlog</text></g>"
  + "<g transform='translate(132,420)'>"
  +   "<ellipse cx='0' cy='-22' rx='58' ry='13' fill='#CFF2E4'/>"
  +   "<path d='M-58 -22 v44 a58 13 0 0 0 116 0 v-44' fill='#E7F8F1'/>"
  +   "<ellipse cx='0' cy='22' rx='58' ry='13' fill='#D8F4E8'/>"
  +   "<text class='as-nlabel' x='0' y='8' text-anchor='middle' fill='#047857'>Index</text></g>"
  + "<text class='as-small' x='132' y='492' text-anchor='middle'>every paragraph addressable</text>"

  /* ---------- GROUNDED ANSWERING ---------- */
  + "<rect class='as-panel' x='352' y='140' width='496' height='372' rx='14'/>"
  + "<rect x='352' y='140' width='496' height='6' rx='3' fill='#0086E6'/>"
  + "<text class='as-zlabel' x='376' y='178' fill='#0086E6'>GROUNDED ANSWERING</text>"
  + "<text class='as-sub' x='376' y='197'>the answer is assembled here</text>"
  /* retrieve */
  + "<g transform='translate(470,232)'><circle r='26' fill='#E8F5FF' stroke='#B9E0FB'/>"
  +   "<circle cx='-3' cy='-3' r='9' fill='none' stroke='#0086E6' stroke-width='3'/>"
  +   "<path d='M4 4 l8 8' stroke='#0086E6' stroke-width='3' stroke-linecap='round'/></g>"
  + "<text class='as-small' x='470' y='280' text-anchor='middle'>Retrieve</text>"
  /* grounding gate */
  + "<g transform='translate(640,232)'>"
  +   "<path d='M0 -30 L30 0 L0 30 L-30 0 Z' fill='#FEF4E2' stroke='#F4CE8C'/>"
  +   "<g class='as-gate-amber'><path d='M0 -30 L30 0 L0 30 L-30 0 Z' fill='#F79009'/>"
  +     "<path d='M-8 0 h16 M0 -8 v16' stroke='#fff' stroke-width='0' /></g>"
  +   "<g class='as-gate-green'><path d='M0 -30 L30 0 L0 30 L-30 0 Z' fill='#047857'/>"
  +     "<path d='M-9 1 l6 6 l12 -13' stroke='#fff' stroke-width='3' fill='none' stroke-linecap='round'/></g>"
  + "</g>"
  + "<text class='as-small' x='640' y='280' text-anchor='middle'>Grounding gate</text>"
  /* evidence meter under the gate */
  + "<rect x='585' y='292' width='110' height='8' rx='4' fill='#EEF2F6'/>"
  + "<g class='as-meter'><rect x='585' y='292' width='110' height='8' rx='4' fill='#047857'/></g>"
  + "<g class='as-meter-amber'><rect x='585' y='292' width='38' height='8' rx='4' fill='#F79009'/></g>"
  + "<text class='as-small' x='640' y='316' text-anchor='middle'>evidence, scored before writing</text>"
  + "<g class='as-hold'>" + chip(640, 150, 168, "below threshold — held", "#FEF4E2", "#B54708") + "</g>"
  /* generate */
  + "<g class='as-gen'><g transform='translate(790,232)'><circle r='26' fill='#E8F5FF' stroke='#B9E0FB'/>"
  +   "<path d='M0 -13 L4 -4 L13 0 L4 4 L0 13 L-4 4 L-13 0 L-4 -4 Z' fill='#0086E6'/></g></g>"
  + "<text class='as-small' x='790' y='280' text-anchor='middle'>Generate</text>"
  /* flow arrows */
  + "<path d='M504 232 h96' stroke='#C9D6E2' stroke-width='2'/>"
  + "<path d='M678 232 h72' stroke='#C9D6E2' stroke-width='2'/>"
  + "<path d='M596 226 l8 6 l-8 6 M746 226 l8 6 l-8 6' stroke='#C9D6E2' stroke-width='2' fill='none'/>"
  /* clarify path */
  + "<path class='as-cpath' d='M640 196 C 640 96, 460 44, 344 56' stroke='#F79009' stroke-width='2' fill='none'/>"
  /* answer card */
  + "<g class='as-card'>"
  +   "<rect x='420' y='360' width='360' height='120' rx='14' fill='#fff' stroke='#DFE7EE'/>"
  +   "<rect x='420' y='360' width='360' height='120' rx='14' fill='none' stroke='#0086E6' stroke-opacity='.25'/>"
  +   "<text class='as-small' x='444' y='388' fill='#93A6B8'>ANSWER</text>"
  +   "<rect x='444' y='400' width='300' height='7' rx='3.5' fill='#DCE7F0'/>"
  +   "<rect x='444' y='414' width='260' height='7' rx='3.5' fill='#DCE7F0'/>"
  +   "<rect x='444' y='428' width='282' height='7' rx='3.5' fill='#DCE7F0'/>"
  +   "<g class='as-cite1'>" + chip(585, 458, 96, "SOP-04 · p.12", "#E8F5FF", "#01517F") + "</g>"
  +   "<g class='as-cite2'>" + chip(688, 458, 88, "POL-11 · p.3", "#E8F5FF", "#01517F") + "</g>"
  +   "<circle cx='752' cy='458' r='5' fill='#047857'/>"
  +   "<text class='as-small' x='762' y='462' fill='#047857'>HIGH</text>"
  + "</g>"

  /* ---------- TRUST & TELEMETRY ---------- */
  + "<rect class='as-panel' x='880' y='140' width='300' height='372' rx='14'/>"
  + "<rect x='880' y='140' width='300' height='6' rx='3' fill='#9333EA'/>"
  + "<text class='as-zlabel' x='904' y='178' fill='#9333EA'>TRUST AND TELEMETRY</text>"
  + "<text class='as-sub' x='904' y='197'>proof that it worked</text>"
  + "<circle cx='1005' cy='280' r='44' fill='none' stroke='#F1E7FB' stroke-width='9'/>"
  + "<circle class='as-dial' cx='1005' cy='280' r='44' fill='none' stroke='#9333EA' stroke-width='9'"
  +   " stroke-linecap='round' transform='rotate(-90 1005 280)'/>"
  + "<text class='as-nlabel' x='1005' y='286' text-anchor='middle' fill='#9333EA'>scored</text>"
  + "<text class='as-small' x='1005' y='348' text-anchor='middle'>every answer · every refusal</text>"
  + "<g class='as-live' style='animation-delay:.5s'><rect x='912' y='372' width='186' height='24' rx='6' fill='#F8EDFE'/><text class='as-small' x='924' y='388' fill='#9333EA'>trace · tokens · latency</text></g>"
  + "<g transform='translate(1005,452)'><rect x='-92' y='-16' width='184' height='32' rx='8' fill='#F8EDFE' stroke='#E2C4F8'/>"
  +   "<text class='as-chip' x='0' y='4' text-anchor='middle' fill='#9333EA'>gap noticed → backlog</text></g>"

  /* ---------- SECURITY band ---------- */
  + "<rect class='as-band' x='20' y='552' width='1160' height='72' fill='#EEF1F5' stroke='#DCE2EA'/>"
  + "<text class='as-zlabel' x='44' y='582' fill='#344054'>SECURITY AND OPERATIONS</text>"
  + "<text class='as-sub' x='44' y='601'>underpins every zone above</text>"
  + "<g class='as-small' fill='#475467'>"
  +   "<text x='430' y='592'>private networking</text><text x='590' y='592'>key management</text>"
  +   "<text x='740' y='592'>least privilege</text><text x='872' y='592'>audit trail</text>"
  +   "<text x='980' y='592'>dev / prod isolation</text></g>"

  /* ---------- the loop home ---------- */
  + "<path class='as-looppath' d='M1005 480 C 1005 545, 620 545, 620 536 C 400 545, 238 520, 238 486'"
  +   " stroke='#9333EA' stroke-width='2' fill='none'/>"

  /* ---------- travellers (drawn last, on top) ---------- */
  + "<g class='as-q'>" + chip(0, 0, 130, "a question", "#4338CA", "#fff") + "</g>"
  + "<g class='as-p1'><rect x='-14' y='-8' width='28' height='16' rx='4' fill='#0086E6' opacity='.85'/></g>"
  + "<g class='as-p2'><rect x='-14' y='-8' width='28' height='16' rx='4' fill='#0086E6' opacity='.7'/></g>"
  + "<g class='as-p3'><rect x='-14' y='-8' width='28' height='16' rx='4' fill='#0086E6' opacity='.9'/></g>"
  + "<g class='as-p4'><rect x='-14' y='-8' width='28' height='16' rx='4' fill='#0086E6' opacity='.8'/></g>"
  + "<g class='as-p5'><rect x='-14' y='-8' width='28' height='16' rx='4' fill='#0086E6' opacity='.7'/></g>"
  + "<g class='as-c1'>" + chip(0, 0, 150, "one clarifying question", "#F79009", "#fff") + "</g>"
  + "<g class='as-c2'>" + chip(0, 0, 110, "refined query", "#4338CA", "#fff") + "</g>"
  + "<g class='as-tel'><circle r='7' fill='#9333EA'/></g>"
  + "<g class='as-gap'><circle r='7' fill='#9333EA'/><circle r='12' fill='#9333EA' opacity='.25'/></g>"
  + "</svg>";

  var CAPTIONS = ""
  + "<div class='as-cap' aria-hidden='true'>"
  + "<span class='c1'><i style='background:#4338CA'>1</i>Permissions are applied before anything is searched.</span>"
  + "<span class='c2'><i style='background:#0086E6'>2</i>Evidence is scored before a single word is written.</span>"
  + "<span class='c3'><i style='background:#DC6803'>3</i>Thin evidence? It asks one question — it never invents.</span>"
  + "<span class='c4'><i style='background:#047857'>4</i>The answer arrives cited, with its confidence shown.</span>"
  + "<span class='c5'><i style='background:#9333EA'>5</i>What it could not answer becomes the content backlog.</span>"
  + "</div>";

  function mount(el) {
    if (!el || el.dataset.asMounted) return;
    el.dataset.asMounted = "1";
    var wrap = document.createElement("div");
    wrap.className = "as-wrap";
    wrap.innerHTML = SVG + CAPTIONS
      + "<button class='as-pause' type='button' aria-pressed='false'>PAUSE</button>";
    el.appendChild(wrap);
    var btn = wrap.querySelector(".as-pause");
    btn.addEventListener("click", function () {
      var paused = wrap.classList.toggle("as-paused");
      btn.textContent = paused ? "PLAY" : "PAUSE";
      btn.setAttribute("aria-pressed", String(paused));
    });
  }

  function boot() {
    if (!document.getElementById("archscene-css")) {
      var st = document.createElement("style");
      st.id = "archscene-css";
      st.textContent = CSS;
      document.head.appendChild(st);
    }
    document.querySelectorAll("[data-archscene]").forEach(mount);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else boot();

  window.ArchScene = { mount: mount };
})();
