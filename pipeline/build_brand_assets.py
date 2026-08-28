"""Brand asset processing — real tenant logos, made usable in the product.

    python -m pipeline.build_brand_assets            # every tenant
    python -m pipeline.build_brand_assets q-airlines # one tenant

The source artwork in brand-assets/site/brand/ arrives as full lockups
(emblem + wordmark + tagline) flattened onto white. Two problems follow:

  1. The site is dark. A white-boxed PNG dropped onto #0B1338 looks like a
     sticker, and the shipped <slug>-mark.png files are naive square crops
     with the wordmark bleeding into the bottom edge.
  2. Different surfaces need different shapes: a navbar wants a square mark,
     a card wants the same, a light surface can take the full lockup.

So for each tenant this script derives, deterministically, from the lockup:

    tenants/<slug>/brand/mark.png            512x512, transparent, emblem only
    tenants/<slug>/brand/lockup.png          trimmed full lockup, transparent
    site/assets/brand/<slug>-mark.png        the same mark, where the site serves it
    site/assets/brand/<slug>-lockup.png      the same lockup, likewise

How the emblem is isolated: after removing the border-connected white
background, content rows are projected onto the vertical axis. A lockup is
vertically structured — emblem, gap, wordmark, gap, tagline — so the topmost
content block, after merging blocks separated by hairline gaps, is the emblem.
The split is validated (an emblem is roughly square and dominates the lockup
height); if a file ever violates that shape the script falls back to the whole
trimmed lockup rather than guessing, and says so.

Only border-connected white is removed. White INSIDE a shape (the counter of a
Q, the field of a shield) is part of the drawing and stays opaque, which is
also why these assets are intended to sit on a light chip in the UI rather
than directly on the page background.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

import yaml

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    raise SystemExit("Pillow is required: pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "brand-assets" / "site" / "brand"
# The names the site serves. Written on every run so the committed copies
# can always be regenerated from brand-assets/ — CI runs this in both jobs.
SITE_BRAND = ROOT / "site" / "assets" / "brand"

# Whiteness thresholds for background removal. Pixels lighter than SOLID on
# every channel become fully transparent; the FEATHER..SOLID band gets a
# proportional alpha so anti-aliased edges do not leave a hard white fringe.
SOLID = 246
FEATHER = 224

MARK_SIZE = 256          # output square for mark.png
MARK_MARGIN = 0.07       # breathing room around the emblem, fraction of side
LOCKUP_MAX_W = 880       # lockups are display assets, not print assets
GAP_MERGE_FRAC = 0.008    # gaps thinner than 2% of height are intra-emblem
MIN_EMBLEM_FRAC = 0.34   # emblem must be at least this fraction of content height


def _whiteness(px) -> int:
    """0..255 — how close to pure white a pixel is (min channel)."""
    return min(px[0], px[1], px[2])


def remove_background(im: Image.Image) -> Image.Image:
    """Clear border-connected near-white to transparent, feathering edges."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()

    def push(x: int, y: int):
        i = y * w + x
        if seen[i]:
            return
        seen[i] = 1
        p = px[x, y]
        wh = _whiteness(p)
        if wh >= SOLID:
            px[x, y] = (255, 255, 255, 0)
            q.append((x, y))
        elif wh >= FEATHER:
            # Edge pixel: keep colour, scale alpha down as it approaches white.
            a = int(255 * (SOLID - wh) / (SOLID - FEATHER))
            px[x, y] = (p[0], p[1], p[2], min(p[3], a))
            q.append((x, y))
        # darker than FEATHER: real ink — flood stops here.

    for x in range(w):
        push(x, 0), push(x, h - 1)
    for y in range(h):
        push(0, y), push(w - 1, y)
    while q:
        x, y = q.popleft()
        if x > 0: push(x - 1, y)
        if x < w - 1: push(x + 1, y)
        if y > 0: push(x, y - 1)
        if y < h - 1: push(x, y + 1)
    return im


def _row_blocks(im: Image.Image) -> list[tuple[int, int]]:
    """Contiguous vertical bands that contain visible content."""
    w, h = im.size
    alpha = im.getchannel("A").load()
    rows = [any(alpha[x, y] > 24 for x in range(w)) for y in range(h)]
    blocks, start = [], None
    for y, filled in enumerate(rows):
        if filled and start is None:
            start = y
        elif not filled and start is not None:
            blocks.append((start, y - 1)); start = None
    if start is not None:
        blocks.append((start, h - 1))
    # Heal only hairline scan gaps; real emblem/wordmark gaps must survive.
    merged, gap = [], max(2, int(h * GAP_MERGE_FRAC))
    for b in blocks:
        if merged and b[0] - merged[-1][1] <= gap:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(b)
    return merged


def _strip_wordmark(band: Image.Image) -> Image.Image:
    """Remove a wordmark that is ink-bridged to the emblem.

    Letterforms betray themselves: a text row crosses ink many times (two
    edges per stroke, several strokes per letter, several letters per word),
    where emblem rows cross only a handful of shapes. A sustained run of
    high-transition, near-full-width rows in the lower half of the band is a
    wordmark; everything from that run down is dropped, provided what remains
    still looks like an emblem. Anything ambiguous is left untouched.
    """
    w, h = band.size
    alpha = band.getchannel("A").load()
    trans, width = [], []
    for y in range(h):
        on = [alpha[x, y] > 24 for x in range(w)]
        t = sum(1 for x in range(1, w) if on[x] != on[x - 1])
        xs = [x for x, v in enumerate(on) if v]
        trans.append(t)
        width.append((xs[-1] - xs[0] + 1) if xs else 0)

    run_start = None
    for y in range(h // 2, h):
        texty = trans[y] >= 12 and width[y] >= w * 0.82
        if texty and run_start is None:
            run_start = y
        elif texty:
            if y - run_start >= max(6, h * 0.06):      # sustained: a wordmark
                cut = band.crop((0, 0, w, run_start))
                # Fragments sliced by this cut still touch its bottom edge
                # HERE — after a bbox re-crop that guarantee is gone.
                cut = _drop_cut_slivers(cut)
                bbox = cut.getbbox()
                if bbox:
                    cut = cut.crop(bbox)
                    if (cut.height >= h * 0.5
                            and 0.5 <= cut.width / cut.height <= 2.0):
                        return cut
                return band
        else:
            run_start = None
    return band


def _drop_cut_slivers(band: Image.Image) -> Image.Image:
    """Erase fragments left by the wordmark cut.

    When the cut passes through a wordmark, the tallest letter's cap can
    survive above the line as a detached sliver. Such slivers share three
    properties that no legitimate emblem element does: they sit against the cut
    (bottom) edge, they are short, and they are tiny relative to the emblem.
    Legitimate detached elements — a floated star, a molecule dot — touch
    nothing and survive untouched.
    """
    w, h = band.size
    alpha = band.getchannel("A").load()
    label = [[0] * w for _ in range(h)]
    comps: list[dict] = []
    for sy in range(h):
        for sx in range(w):
            if alpha[sx, sy] <= 24 or label[sy][sx]:
                continue
            cid = len(comps) + 1
            area, min_y, max_y, touches = 0, sy, sy, False
            stack = [(sx, sy)]
            label[sy][sx] = cid
            pts = []
            while stack:
                x, y = stack.pop()
                area += 1
                pts.append((x, y))
                min_y, max_y = min(min_y, y), max(max_y, y)
                touches = touches or y >= h - max(2, int(h * 0.15))
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                    if 0 <= nx < w and 0 <= ny < h and not label[ny][nx] \
                            and alpha[nx, ny] > 24:
                        label[ny][nx] = cid
                        stack.append((nx, ny))
            comps.append({"area": area, "h": max_y - min_y + 1,
                          "bottom": touches, "pts": pts})
    if not comps:
        return band
    main_area = max(c["area"] for c in comps)
    px = band.load()
    changed = False
    for c in comps:
        if c["bottom"] and c["h"] < h * 0.14 and c["area"] < main_area * 0.03:
            for x, y in c["pts"]:
                px[x, y] = (0, 0, 0, 0)
            changed = True
    if changed:
        bbox = band.getbbox()
        if bbox:
            band = band.crop(bbox)
    return band


def _keep_emblem_cluster(band: Image.Image) -> Image.Image:
    """Keep only ink that belongs to the emblem's spatial cluster.

    Some lockups run a decorative underline swoosh beneath the wordmark whose
    tips rise into the emblem's vertical range. Those tips are real ink but
    the wrong ink: they belong to the lockup composition, not to the square
    mark. Grown outward from the largest component, the emblem absorbs every
    component near it (orbiting stars, molecule dots, ring icons) and leaves
    the detached swoosh tips outside the cluster, where they are erased.
    Anything big enough to plausibly be emblem anatomy is never dropped.
    """
    w, h = band.size
    alpha = band.getchannel("A").load()
    seen = [[0] * w for _ in range(h)]
    comps = []
    for sy in range(h):
        for sx in range(w):
            if alpha[sx, sy] <= 24 or seen[sy][sx]:
                continue
            stack = [(sx, sy)]
            seen[sy][sx] = 1
            area, minx, miny, maxx, maxy, pts = 0, sx, sy, sx, sy, []
            while stack:
                x, y = stack.pop()
                area += 1
                pts.append((x, y))
                minx, maxx = min(minx, x), max(maxx, x)
                miny, maxy = min(miny, y), max(maxy, y)
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] \
                            and alpha[nx, ny] > 24:
                        seen[ny][nx] = 1
                        stack.append((nx, ny))
            comps.append({"area": area, "bbox": [minx, miny, maxx, maxy],
                          "pts": pts})
    if len(comps) < 2:
        return band

    comps.sort(key=lambda c: c["area"], reverse=True)
    gap = max(6, int(max(w, h) * 0.03))
    cluster = list(comps[0]["bbox"])
    member = [True] + [False] * (len(comps) - 1)

    def near(b):
        return not (b[0] > cluster[2] + gap or b[2] < cluster[0] - gap or
                    b[1] > cluster[3] + gap or b[3] < cluster[1] - gap)

    grown = True
    while grown:
        grown = False
        for i, c in enumerate(comps):
            if member[i] or not near(c["bbox"]):
                continue
            member[i] = True
            b = c["bbox"]
            cluster = [min(cluster[0], b[0]), min(cluster[1], b[1]),
                       max(cluster[2], b[2]), max(cluster[3], b[3])]
            grown = True

    px = band.load()
    changed = False
    for i, c in enumerate(comps):
        if member[i] or c["area"] >= comps[0]["area"] * 0.25:
            continue
        for x, y in c["pts"]:
            px[x, y] = (0, 0, 0, 0)
        changed = True
    if changed:
        bbox = band.getbbox()
        if bbox:
            band = band.crop(bbox)
    return band


def _pick_emblem(im: Image.Image) -> tuple[Image.Image, str] | None:
    """The emblem is the TALLEST content band. Wordmarks and taglines are
    cap-height text; the drawn mark dominates the vertical axis in every
    lockup in this family. Bands hugging the emblem from above (a floated
    star, a swoosh tip) are absorbed; text below is not."""
    blocks = _row_blocks(im)
    if not blocks:
        return None
    full_h = blocks[-1][1] - blocks[0][0] + 1
    tallest = max(blocks, key=lambda b: b[1] - b[0])
    idx = blocks.index(tallest)
    top = tallest[0]
    # absorb near floaters directly above (within 6% of height)
    for b in reversed(blocks[:idx]):
        if top - b[1] <= im.height * 0.06:
            top = b[0]
        else:
            break
    band = im.crop((0, top, im.width, tallest[1] + 1))
    bbox = band.getbbox()
    if not bbox:
        return None
    band = band.crop(bbox)
    band = _keep_emblem_cluster(_strip_wordmark(band))
    ratio = band.width / max(1, band.height)
    frac = (tallest[1] - tallest[0] + 1) / full_h
    if frac >= MIN_EMBLEM_FRAC and 0.5 <= ratio <= 2.0:
        return band, f"h={frac:.0%},r={ratio:.2f}"
    return None


def extract_emblem(slug: str) -> tuple[Image.Image, str]:
    """Lockup first; the shipped square mark second; trimmed lockup last.
    The mark files are naive crops with wordmark bleed, but cropping also
    severs ink bridges between emblem and text, so they rescue exactly the
    lockups where everything is connected into one band."""
    for name, label in ((f"{slug}-lockup.png", "lockup"),
                        (f"{slug}-mark.png", "markfile")):
        f = SRC / name
        if not f.exists():
            continue
        art = remove_background(Image.open(f))
        bbox = art.getbbox()
        if not bbox:
            continue
        art = art.crop(bbox)
        picked = _pick_emblem(art)
        if picked:
            return picked[0], f"{label}:{picked[1]}"
        if label == "lockup":
            fallback = art  # keep for last resort
    return fallback, "trimmed-lockup-fallback"


def quantize(im: Image.Image) -> Image.Image:
    """RGBA -> 256-colour palette with alpha. Logo art is flat colour with
    anti-aliased edges, so this quarters the file size with no visible loss —
    the committed assets are palette PNGs and eleven of them load on the
    landing page at once."""
    return im.quantize(colors=256, method=Image.Quantize.FASTOCTREE)


def to_square(im: Image.Image, size: int, margin_frac: float) -> Image.Image:
    inner = int(size * (1 - 2 * margin_frac))
    scale = min(inner / im.width, inner / im.height)
    im = im.resize((max(1, round(im.width * scale)),
                    max(1, round(im.height * scale))), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
    return out


def process(slug: str) -> str:
    lockup_src = SRC / f"{slug}-lockup.png"
    if not lockup_src.exists():
        lockup_src = SRC / f"{slug}-mark.png"
    if not lockup_src.exists():
        return f"{slug}: NO SOURCE ART — skipped"

    dest = ROOT / "tenants" / slug / "brand"
    dest.mkdir(parents=True, exist_ok=True)
    SITE_BRAND.mkdir(parents=True, exist_ok=True)

    emblem, note = extract_emblem(slug)
    mark = quantize(to_square(emblem, MARK_SIZE, MARK_MARGIN))
    mark.save(dest / "mark.png", optimize=True)
    mark.save(SITE_BRAND / f"{slug}-mark.png", optimize=True)

    lockup = remove_background(Image.open(lockup_src))
    lockup = lockup.crop(lockup.getbbox() or (0, 0, 1, 1))
    if lockup.width > LOCKUP_MAX_W:
        s = LOCKUP_MAX_W / lockup.width
        lockup = lockup.resize((LOCKUP_MAX_W, round(lockup.height * s)),
                               Image.LANCZOS)
    lockup = quantize(lockup)
    lockup.save(dest / "lockup.png", optimize=True)
    lockup.save(SITE_BRAND / f"{slug}-lockup.png", optimize=True)
    return f"{slug}: mark + lockup written  [{note}]"


def main(only: str | None = None):
    reg = yaml.safe_load((ROOT / "tenants" / "registry.yml").read_text())
    slugs = [t["slug"] for t in reg["tenants"] if not only or t["slug"] == only]
    if not slugs:
        raise SystemExit(f"unknown tenant '{only}'")
    for s in slugs:
        print(" ", process(s))
    print(f"[OK] brand assets — {len(slugs)} tenants")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
