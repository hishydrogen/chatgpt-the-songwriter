#!/usr/bin/env python3
"""Album art for "Catalina Blue": blue hour over the San Pedro Channel, Santa Catalina
Island low on the horizon, one far-off sloop. Designed like a 1978 West Coast LP sleeve:
one full-bleed picture, quiet type in the sky, no retro effects (no stripes, no grain,
no faux wear). Renders cover.html -> cover.png (3000x3000) with headless Chromium, then
cover.jpg for embedding.
"""
import math
import random
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = 1000
HORIZON = 612


def island_path():
    """Catalina seen from the mainland: a long ridge rising from the Avalon end (left),
    its highest mass left of centre, the dip of the isthmus, a smaller west end."""
    rnd = random.Random(1978)
    keys = [(0.18, 0.0), (0.205, 5), (0.23, 11), (0.26, 13), (0.29, 20), (0.32, 19), (0.355, 27),
            (0.39, 31), (0.415, 29), (0.445, 37), (0.47, 41), (0.495, 36), (0.52, 39), (0.555, 32),
            (0.585, 34), (0.62, 27), (0.655, 25), (0.69, 17), (0.715, 12), (0.735, 6), (0.75, 8),
            (0.775, 16), (0.80, 19), (0.825, 21), (0.85, 16), (0.875, 10), (0.895, 4), (0.905, 0.0)]
    xs = [k[0] * W for k in keys]
    hs = [k[1] for k in keys]
    pts = []
    x = xs[0]
    noise = 0.0
    while x <= xs[-1]:
        # piecewise-linear base ridge + smoothed small-scale roughness
        i = max(j for j in range(len(xs)) if xs[j] <= x) if x < xs[-1] else len(xs) - 2
        t = (x - xs[i]) / (xs[i + 1] - xs[i])
        t = t * t * (3 - 2 * t)
        h = hs[i] + (hs[i + 1] - hs[i]) * t
        noise = 0.86 * noise + 0.14 * rnd.uniform(-1, 1)
        h = max(0.0, h + noise * 3.2 * min(1.0, h / 6))
        pts.append((x, HORIZON - h))
        x += 1.5
    d = f"M{xs[0]:.1f},{HORIZON + 0.5}" + "".join(f"L{px:.1f},{py:.2f}" for px, py in pts)
    return d + f"L{xs[-1]:.1f},{HORIZON + 0.5}Z"


def sea_lines():
    """Faint long swells: a few hairlines that get closer together toward the horizon."""
    out = []
    y = HORIZON + 6
    k = 0
    while y < W:
        op = 0.05 + 0.05 * math.exp(-(y - HORIZON) / 120)
        out.append(f'<rect x="0" y="{y:.1f}" width="{W}" height="{0.6 + (y - HORIZON) / 260:.2f}" '
                   f'fill="#dfe8f0" opacity="{op:.3f}"/>')
        k += 1
        y += 3.5 + k * 1.9
    return "".join(out)


def clouds():
    """A few long, thin streaks of altostratus lit from below, airbrush-soft."""
    rnd = random.Random(12)
    out = []
    for cx, cy, w, h, col, op in ((610, 452, 420, 5.5, "#f3cfae", 0.55), (760, 476, 300, 4.0, "#f6d8b8", 0.5),
                                  (420, 498, 360, 3.5, "#efd2b6", 0.42), (850, 408, 260, 4.5, "#e9c3a6", 0.35),
                                  (300, 430, 220, 3.0, "#dcc3b0", 0.28), (690, 520, 240, 3.0, "#f7dcc0", 0.4)):
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 2}" ry="{h}" fill="{col}" opacity="{op}" '
                   f'filter="url(#cloud)"/>')
        for k in range(3):   # broken edges
            dx, dy = rnd.uniform(-w / 3, w / 3), rnd.uniform(-h, h)
            out.append(f'<ellipse cx="{cx + dx:.1f}" cy="{cy + dy:.1f}" rx="{w / 5:.1f}" ry="{h * 0.7:.1f}" '
                       f'fill="{col}" opacity="{op * 0.6:.2f}" filter="url(#cloud)"/>')
    return "".join(out)


def sloop(x, y, s):
    """A small sloop under sail (main + jib), seen side-on, with a soft reflection."""
    mast = f"M{x},{y - 30 * s}L{x},{y}"
    main = (f"M{x + 0.6 * s},{y - 29 * s}L{x + 0.6 * s},{y - 1.6 * s}L{x + 14 * s},{y - 1.6 * s}"
            f"Q{x + 9.5 * s},{y - 14 * s} {x + 0.6 * s},{y - 29 * s}Z")
    jib = (f"M{x - 0.6 * s},{y - 26 * s}L{x - 0.6 * s},{y - 2.2 * s}L{x - 10 * s},{y - 2.2 * s}"
           f"Q{x - 6.5 * s},{y - 12 * s} {x - 0.6 * s},{y - 26 * s}Z")
    hull = f"M{x - 12 * s},{y - 1.2 * s}L{x + 16 * s},{y - 1.2 * s}L{x + 13 * s},{y + 1.4 * s}L{x - 10 * s},{y + 1.4 * s}Z"
    return (f'<g><path d="{main}" fill="#f7f1e6"/><path d="{jib}" fill="#efe7da"/>'
            f'<path d="{mast}" stroke="#d8d2c8" stroke-width="{0.35 * s}"/>'
            f'<path d="{hull}" fill="#2c3d55"/></g>'
            f'<g opacity="0.14" filter="url(#ripple)" transform="translate(0,{(y + 1.4 * s) * 1.62:.2f}) scale(1,-0.62)">'
            f'<path d="{main}" fill="#f7f1e6"/><path d="{jib}" fill="#efe7da"/></g>')


HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Fraunces; font-style: italic; src: url(fonts/Fraunces-Italic.ttf); }}
@font-face {{ font-family: Fraunces; font-style: normal; src: url(fonts/Fraunces.ttf); }}
@font-face {{ font-family: Josefin; src: url(fonts/JosefinSans.ttf); }}
html, body {{ margin: 0; width: {W}px; height: {W}px; background: #20324c; overflow: hidden; }}
svg {{ display: block; }}
.title {{ font-family: Fraunces; font-style: italic; font-size: 86px; font-weight: 380;
          font-variation-settings: "SOFT" 100, "WONK" 0, "opsz" 144; letter-spacing: -0.5px; fill: #f5ead8; }}
.artist {{ font-family: Josefin; font-size: 19px; font-weight: 300; letter-spacing: 6.5px; fill: #f0e3cf; }}
</style></head><body>
<svg width="{W}" height="{W}" viewBox="0 0 {W} {W}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="{HORIZON}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#2d4a73"/><stop offset="0.38" stop-color="#5f7fa3"/>
    <stop offset="0.7" stop-color="#a9b9c8"/><stop offset="0.88" stop-color="#e2cdb8"/>
    <stop offset="1" stop-color="#f1d2ae"/></linearGradient>
  <radialGradient id="afterglow" cx="0.68" cy="{HORIZON / W:.3f}" r="0.55" fx="0.68" fy="{HORIZON / W:.3f}">
    <stop offset="0" stop-color="#f6c99c" stop-opacity="0.55"/><stop offset="1" stop-color="#f6c99c" stop-opacity="0"/></radialGradient>
  <linearGradient id="sea" x1="0" y1="{HORIZON}" x2="0" y2="{W}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#8ea3b5"/><stop offset="0.05" stop-color="#5d7b98"/>
    <stop offset="0.3" stop-color="#2f557d"/><stop offset="1" stop-color="#16304f"/></linearGradient>
  <linearGradient id="isl" x1="0" y1="{HORIZON - 45}" x2="0" y2="{HORIZON}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#5d6683"/><stop offset="1" stop-color="#7d8499"/></linearGradient>
  <linearGradient id="haze" x1="0" y1="{HORIZON - 14}" x2="0" y2="{HORIZON + 2}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#d9cbbd" stop-opacity="0"/><stop offset="1" stop-color="#d9cbbd" stop-opacity="0.55"/></linearGradient>
  <linearGradient id="glint" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#f3d6b6" stop-opacity="0"/><stop offset="0.5" stop-color="#f3d6b6" stop-opacity="0.32"/>
    <stop offset="1" stop-color="#f3d6b6" stop-opacity="0"/></linearGradient>
  <filter id="soft"><feGaussianBlur stdDeviation="0.6"/></filter>
  <filter id="cloud" x="-30%" y="-300%" width="160%" height="700%"><feGaussianBlur stdDeviation="9 2.2"/></filter>
  <filter id="ripple" x="-50%" y="-50%" width="200%" height="200%">
    <feTurbulence type="fractalNoise" baseFrequency="0.02 0.6" numOctaves="2" seed="11" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/>
    <feGaussianBlur stdDeviation="0.5"/></filter>
  <filter id="water" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.0035 0.045" numOctaves="3" seed="21"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0.88  0 0 0 0 0.92  0 0 0 0 0.97  0 0 0 1.6 -0.78"/></filter>
  <filter id="water2" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.007 0.1" numOctaves="3" seed="22"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0.88  0 0 0 0 0.92  0 0 0 0 0.97  0 0 0 1.6 -0.78"/></filter>
  <filter id="water3" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.014 0.3" numOctaves="2" seed="23"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0.9  0 0 0 0 0.93  0 0 0 0 0.97  0 0 0 1.6 -0.8"/></filter>
  <linearGradient id="gfar" x1="0" y1="{HORIZON}" x2="0" y2="{W}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="white"/><stop offset="0.16" stop-color="white"/><stop offset="0.3" stop-color="black"/></linearGradient>
  <linearGradient id="gmid" x1="0" y1="{HORIZON}" x2="0" y2="{W}" gradientUnits="userSpaceOnUse">
    <stop offset="0.14" stop-color="black"/><stop offset="0.3" stop-color="white"/><stop offset="0.5" stop-color="white"/>
    <stop offset="0.66" stop-color="black"/></linearGradient>
  <linearGradient id="gnear" x1="0" y1="{HORIZON}" x2="0" y2="{W}" gradientUnits="userSpaceOnUse">
    <stop offset="0.5" stop-color="black"/><stop offset="0.68" stop-color="white"/></linearGradient>
  <mask id="zfar"><rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" fill="url(#gfar)"/></mask>
  <mask id="zmid"><rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" fill="url(#gmid)"/></mask>
  <mask id="znear"><rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" fill="url(#gnear)"/></mask>
  <linearGradient id="wfade" x1="0" y1="{HORIZON}" x2="0" y2="{W}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="white" stop-opacity="0.5"/><stop offset="0.35" stop-color="white" stop-opacity="0.3"/>
    <stop offset="1" stop-color="white" stop-opacity="0.1"/></linearGradient>
  <mask id="watermask"><rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" fill="url(#wfade)"/></mask>
  <filter id="dither"><feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="1" seed="5"/>
    <feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 0.022"/></feComponentTransfer></filter>
</defs>

<rect width="{W}" height="{HORIZON}" fill="url(#sky)"/>
<rect width="{W}" height="{HORIZON}" fill="url(#afterglow)"/>
<circle cx="834" cy="122" r="1.5" fill="#fff6e6" opacity="0.8"/>
{clouds()}

<path d="{island_path()}" fill="url(#isl)" filter="url(#soft)"/>
<rect x="0" y="{HORIZON - 14}" width="{W}" height="16" fill="url(#haze)"/>

<rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" fill="url(#sea)"/>
<rect x="420" y="{HORIZON + 1}" width="520" height="5" fill="url(#glint)"/>
<g mask="url(#watermask)">
  <rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" filter="url(#water3)" mask="url(#zfar)"/>
  <rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" filter="url(#water2)" mask="url(#zmid)"/>
  <rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" filter="url(#water)" mask="url(#znear)"/>
</g>
<rect y="{HORIZON - 0.4}" width="{W}" height="1.1" fill="#f4dcc0" opacity="0.6"/>

{sloop(262, HORIZON + 22, 0.9)}

<text class="title" x="78" y="168">Catalina Blue</text>
<text class="artist" x="82" y="210">CLAUDE THE SONGWRITER</text>

<rect width="{W}" height="{W}" filter="url(#dither)"/>
</svg></body></html>"""


def main():
    (HERE / "cover.html").write_text(HTML)
    chrome = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
    subprocess.run([chrome, "--headless=new", "--no-sandbox", "--hide-scrollbars", "--disable-gpu",
                    f"--window-size={W},{W + 200}", "--force-device-scale-factor=3",
                    "--virtual-time-budget=3000", f"--screenshot={HERE / 'cover.png'}",
                    (HERE / "cover.html").as_uri()], check=True, capture_output=True)
    # headless viewport is shorter than the window: render tall, crop to an exact square
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "cover.png"), "-vf", f"crop={3 * W}:{3 * W}:0:0",
                    str(HERE / "cover_sq.png")], check=True)
    (HERE / "cover_sq.png").replace(HERE / "cover.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "cover.png"), "-q:v", "2",
                    str(HERE / "cover.jpg")], check=True)
    print("cover.png / cover.jpg written")


if __name__ == "__main__":
    main()
