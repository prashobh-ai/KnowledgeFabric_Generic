# Film stage — the explainer's source

`stage.html` is the deterministic timeline the explainer film is recorded
from: five chapters, first-person captions, the answer-journey scene mounted
from `site/assets/js/archscene.js`. Edit the copy or timing here, then
re-record — the film is a build product, not hand-made footage.

To re-record (any machine with Playwright + Chromium):

    # serve THIS directory's parent so ../../site/... resolves
    python3 -m http.server 8844   # from the repo root
    node record.js                # records ~70s at 1280x720 to VP8 WebM

`record.js` (gist): open a browser context with
`recordVideo:{dir,size:{width:1280,height:720}}`, goto
`/brand-assets/film-stage/stage.html`, `waitForFunction('window.FILM_DONE')`,
close the context, and copy the produced .webm to
`site/media/fabric-explainer.webm`. Capture the poster with a
plain screenshot at ~2.8s.

The stage aliases the site's webfonts onto locally installed
metric-compatible faces (Carlito, Caladea, Liberation Mono) so a sandboxed
recorder without font egress still produces intentional typography.
