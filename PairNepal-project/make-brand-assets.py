#!/usr/bin/env python3
"""
PairNepal brand asset generator.

The mark is "Leaning pair": two rounded units leaning together until they meet
at a single point, so the silhouette is at once two devices pairing and one
Himalayan summit.

Geometry lives here once. Everything else — the SVG, the favicon, the PWA
icons, the social card — is generated from it, so the mark can never drift
between the tab icon and the header.

Rasterisation is done at 4x supersampling with LANCZOS downsampling, and the
rotated rounded rectangles are drawn as exact polygons rather than by rotating
a bitmap, so edges stay clean.
"""
import math
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
PUBLIC = ROOT / "app" / "public"
OUT = PUBLIC / "images"
BRAND = ROOT / "brand"

SS = 4  # supersample factor

# --- brand palette ---------------------------------------------------------
CRIMSON = (193, 18, 53)
CRIMSON_DEEP = (163, 14, 44)
WHITE = (255, 255, 255)
INK = (16, 24, 40)
INK_2 = (71, 84, 103)
INK_3 = (136, 150, 171)
CANVAS = (247, 248, 250)

# --- mark geometry (24 x 24 viewBox) --------------------------------------
# Tuned against a rendered comparison: these proportions are the ones that keep
# a crisp apex while both units stay legible down to 20 px.
VB = 24.0
CARDS = [
    dict(x=2.8, y=4.6, w=7.6, h=16.4, r=2.6, cx=6.6, cy=12.8, angle=22.0),
    dict(x=13.6, y=4.6, w=7.6, h=16.4, r=2.6, cx=17.4, cy=12.8, angle=-22.0),
]


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------
def rounded_rect_points(x, y, w, h, r, steps=28):
    """Outline of a rounded rectangle, clockwise, in viewBox units."""
    pts = []
    for cx, cy, a0 in (
        (x + w - r, y + r, -90),
        (x + w - r, y + h - r, 0),
        (x + r, y + h - r, 90),
        (x + r, y + r, 180),
    ):
        for i in range(steps + 1):
            a = math.radians(a0 + 90.0 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rotate_points(pts, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for px, py in pts:
        dx, dy = px - cx, py - cy
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return out


def card_polygons():
    """Both cards as rotated polygons, in viewBox units."""
    out = []
    for c in CARDS:
        pts = rounded_rect_points(c["x"], c["y"], c["w"], c["h"], c["r"])
        out.append(rotate_points(pts, c["cx"], c["cy"], c["angle"]))
    return out


def mark_bbox(polys=None):
    polys = polys or card_polygons()
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------------------
# drawing
# ---------------------------------------------------------------------------
def draw_mark(d, colour, box, ox, oy, scale):
    """
    Draw the mark filling `box` (side length in device px) whose top-left corner
    is (ox, oy). The mark is optically centred on its own bounding box, not on
    the 24-unit square, so the tile padding is even on all sides.
    """
    x0, y0, x1, y1 = mark_bbox()
    bw, bh = x1 - x0, y1 - y0

    # centre of the mark's bbox -> centre of the target box
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    tx = ox + box / 2.0
    ty = oy + box / 2.0

    k = (box / max(bw, bh)) * scale

    for poly in card_polygons():
        pts = [(tx + (px - cx) * k, ty + (py - cy) * k) for px, py in poly]
        d.polygon(pts, fill=colour)


def rounded_square(size, radius_ratio, fill, bg=None):
    im = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1],
                        radius=int(size * radius_ratio), fill=fill)
    return im


def icon(size, bg=CRIMSON, mark=WHITE, radius_ratio=0.22, pad_ratio=0.235):
    big = size * SS
    im = rounded_square(big, radius_ratio, bg)
    d = ImageDraw.Draw(im)
    inner = big * (1 - 2 * pad_ratio)
    draw_mark(d, mark, inner, big * pad_ratio, big * pad_ratio, 1.0)
    return im.resize((size, size), Image.LANCZOS)


def maskable(size, bg=CRIMSON, mark=WHITE):
    """Maskable icons must keep the mark inside the safe circle (~80%)."""
    return icon(size, bg=bg, mark=mark, radius_ratio=0.5, pad_ratio=0.30)


def bare_mark(size, colour=CRIMSON, fill_ratio=0.94):
    """Mark only, transparent background — for light surfaces and dark ones."""
    big = size * SS
    im = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = big * fill_ratio
    draw_mark(d, colour, box, (big - box) / 2, (big - box) / 2, 1.0)
    return im.resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------------------
# vector source of truth
# ---------------------------------------------------------------------------
def mark_svg(size=None, colour="currentColor", cls=""):
    """The canonical SVG. Inline this into HTML; saves as logo.svg."""
    attrs = f' width="{size}" height="{size}"' if size else ""
    klass = f' class="{cls}"' if cls else ""
    body = "".join(
        f'<rect x="{c["x"]}" y="{c["y"]}" width="{c["w"]}" height="{c["h"]}" '
        f'rx="{c["r"]}" transform="rotate({c["angle"]} {c["cx"]} {c["cy"]})"/>'
        for c in CARDS
    )
    return (f'<svg{klass}{attrs} viewBox="0 0 24 24" fill="{colour}" '
            f'xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="PairNepal">{body}</svg>')


def write_logo_svg():
    BRAND.mkdir(parents=True, exist_ok=True)
    (BRAND / "logo.svg").write_text(mark_svg() + "\n")
    # A version that is a filled silhouette, for tools that ignore currentColor.
    (BRAND / "logo-crimson.svg").write_text(mark_svg(colour="#c11235") + "\n")


# ---------------------------------------------------------------------------
# social card — rendered by the browser so the type is the real brand type
# ---------------------------------------------------------------------------
def write_card_html():
    BRAND.mkdir(parents=True, exist_ok=True)
    (BRAND / "card.html").write_text(CARD_HTML.replace("%%MARK%%", mark_svg()))


CARD_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
  *{box-sizing:border-box}
  html,body{margin:0;width:1200px;height:630px;overflow:hidden}
  body{
    font-family:'Instrument Sans',system-ui,sans-serif;
    background:#f7f8fa;color:#101828;position:relative;
  }
  .rule{position:absolute;left:0;top:0;width:12px;height:630px;background:#c11235}
  .glow{position:absolute;right:-140px;top:-160px;width:640px;height:640px;border-radius:50%;
        border:1px solid rgba(193,18,53,.13);}
  .glow.b{right:-40px;top:-60px;width:440px;height:440px;border-color:rgba(193,18,53,.09)}
  .glow.c{right:60px;top:40px;width:240px;height:240px;border-color:rgba(193,18,53,.07)}
  .wrap{position:absolute;left:92px;top:88px;right:92px}
  .lock{display:flex;align-items:center;gap:18px}
  .mark{width:88px;height:88px;color:#c11235;flex:none}
  .name{font-family:'Instrument Serif',Georgia,serif;font-size:60px;line-height:1;
        letter-spacing:-.015em;color:#101828}
  h1{font-family:'Instrument Serif',Georgia,serif;font-weight:400;
     font-size:74px;line-height:1.06;letter-spacing:-.02em;margin:44px 0 0;max-width:14ch}
  h1 em{font-style:italic;color:#c11235}
  p{font-size:25px;line-height:1.45;color:#475467;margin:22px 0 0;max-width:48ch}
  .mono{font-family:'JetBrains Mono',monospace;font-size:16px;letter-spacing:.16em;
        text-transform:uppercase;color:#8896ab;position:absolute;left:92px;bottom:74px}
  .credit{font-family:'JetBrains Mono',monospace;font-size:15px;letter-spacing:.06em;
          color:#8896ab;position:absolute;right:92px;bottom:74px}
</style></head>
<body>
  <div class="rule"></div><div class="glow"></div><div class="glow b"></div><div class="glow c"></div>
  <div class="wrap">
    <div class="lock">
      <span class="mark">%%MARK%%</span>
      <span class="name">PairNepal</span>
    </div>
    <h1>Send files between <em>every screen</em> you own</h1>
    <p>Peer to peer, in the browser. No signup, no cables, no upload limit.</p>
  </div>
  <div class="mono">pairnepal.bond</div>
  <div class="credit">built by Samir Puri</div>
</body></html>
"""


# ---------------------------------------------------------------------------
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    written = []

    def save(im, name, **kw):
        p = OUT / name
        im.save(p, **kw)
        written.append((name, p.stat().st_size))

    # Browser tab + legacy favicon probes.
    save(icon(96), "favicon-96x96.png")
    save(icon(96), "favicon-96x96-notification.png")
    icon(64).save(OUT / "favicon.ico",
                  sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    written.append(("favicon.ico", (OUT / "favicon.ico").stat().st_size))
    (OUT / "favicon.svg").write_text(mark_svg(colour="#c11235") + "\n")
    written.append(("favicon.svg", (OUT / "favicon.svg").stat().st_size))

    # PWA / platform icons.
    save(icon(192), "android-chrome-192x192.png")
    save(icon(512), "android-chrome-512x512.png")
    save(maskable(192), "android-chrome-192x192-maskable.png")
    save(maskable(512), "android-chrome-512x512-maskable.png")
    save(icon(180, radius_ratio=0.0), "apple-touch-icon.png")
    save(icon(150, radius_ratio=0.0), "mstile-150x150.png")

    # Bare marks, for light and dark surfaces.
    save(bare_mark(512, CRIMSON), "logo_transparent_512x512.png")
    save(bare_mark(256, WHITE), "logo_mark_white_256.png")
    save(bare_mark(256, INK), "logo_mark_ink_256.png")
    save(icon(512), "pairnepal-og-square.png")

    write_logo_svg()
    write_card_html()

    print("Brand assets written to", OUT)
    for name, size in written:
        print(f"  {name:<42} {size:>9,} bytes")
    print("Vector source:", BRAND / "logo.svg")
    print("Social card source:", BRAND / "card.html")
    print()
    print("Inline mark for HTML:")
    print(mark_svg())


if __name__ == "__main__":
    main()
