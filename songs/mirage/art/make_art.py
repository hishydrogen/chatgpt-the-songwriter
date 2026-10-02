#!/usr/bin/env python3
"""Album art for "Mirage": an 8-bit (stair-stepped) sunset over a heat-haze horizon,
chrome title with a shimmering reflection. Renders cover.html -> cover.png (3000x3000)
with headless Chromium, then cover.jpg for embedding.
"""
import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = 1000
CX, CY, R = 500, 400, 235
HORIZON = 545
STEP = 18  # "pixel" size of the quantized sun


def pixel_sun_path():
    """Outline of a circle quantized to STEP x STEP blocks (an 8-bit sun)."""
    rows = []
    for y in range(CY - R, CY + R, STEP):
        yc = y + STEP / 2
        dy = abs(yc - CY)
        if dy > R:
            continue
        half = math.sqrt(R * R - dy * dy)
        half = math.floor(half / STEP) * STEP
        rows.append((y, CX - half, CX + half))
    d = []
    for y, x0, x1 in rows:
        d.append(f"M{x0},{y}H{x1}V{y + STEP}H{x0}Z")
    return "".join(d)


def stair_wave(y0, amp, cycles, step_px=10, levels=9):
    """A sine quantized in time and amplitude, drawn as a stair line."""
    pts = []
    for i, x in enumerate(range(0, W + step_px, step_px)):
        v = math.sin(2 * math.pi * cycles * x / W) * math.exp(-((x - CX) / 420) ** 2)
        q = round(v * (levels // 2)) / (levels // 2)
        y = y0 - q * amp
        if pts:
            pts.append(f"H{x}")
            pts.append(f"V{y:.1f}")
        else:
            pts.append(f"M{x},{y:.1f}")
    return "".join(pts)


def stripes():
    """Horizontal cuts across the lower sun, growing thicker toward the horizon."""
    out = []
    y = CY + 20
    gap = 4
    while y < HORIZON:
        out.append(f'<rect x="0" y="{y}" width="{W}" height="{gap}" fill="black"/>')
        y += gap + max(6, 22 - gap)  # band of sun, then the next (thicker) cut
        gap += 3
    return "".join(out)


HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Anton; src: url(fonts/Anton.ttf); }}
@font-face {{ font-family: Michroma; src: url(fonts/Michroma.ttf); }}
@font-face {{ font-family: SpaceMono; src: url(fonts/SpaceMono-Regular.ttf); }}
@font-face {{ font-family: SpaceMono; font-weight: 700; src: url(fonts/SpaceMono-Bold.ttf); }}
html, body {{ margin: 0; width: {W}px; height: {W}px; background: #06020b; overflow: hidden; }}
svg {{ display: block; }}
.title {{ font-family: Anton; font-size: 214px; letter-spacing: 26px; }}
.artist {{ font-family: Michroma; font-size: 17px; letter-spacing: 9px; fill: #f3d9ff; }}
.small {{ font-family: SpaceMono; font-size: 13px; letter-spacing: 3.2px; fill: #c9a7e6; }}
.small b {{ font-weight: 700; }}
</style></head><body>
<svg width="{W}" height="{W}" viewBox="0 0 {W} {W}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <radialGradient id="sky" cx="50%" cy="{HORIZON / W * 100:.1f}%" r="75%">
    <stop offset="0" stop-color="#5b1a6e"/><stop offset="0.35" stop-color="#2a0c3d"/>
    <stop offset="1" stop-color="#06020b"/></radialGradient>
  <linearGradient id="sun" x1="0" y1="{CY - R}" x2="0" y2="{HORIZON}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#ffe9a3"/><stop offset="0.38" stop-color="#ff9e5e"/>
    <stop offset="0.7" stop-color="#ff3f7f"/><stop offset="1" stop-color="#b0127a"/></linearGradient>
  <linearGradient id="floor" x1="0" y1="{HORIZON}" x2="0" y2="{W}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#1c0729"/><stop offset="1" stop-color="#030106"/></linearGradient>
  <linearGradient id="chrome" x1="0" y1="610" x2="0" y2="800" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.28" stop-color="#d9dcf0"/>
    <stop offset="0.47" stop-color="#8b7fb0"/><stop offset="0.5" stop-color="#2b1640"/>
    <stop offset="0.56" stop-color="#ff7ab8"/><stop offset="0.72" stop-color="#ffd6ec"/>
    <stop offset="1" stop-color="#ffffff"/></linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="white" stop-opacity="0.55"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>
  <mask id="reflmask"><rect x="0" y="{HORIZON}" width="{W}" height="{W - HORIZON}" fill="url(#fade)"/></mask>
  <mask id="sunmask"><rect width="{W}" height="{W}" fill="white"/>{stripes()}</mask>
  <filter id="haze" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.004 0.09" numOctaves="2" seed="7"/>
    <feDisplacementMap in="SourceGraphic" scale="34" xChannelSelector="R" yChannelSelector="G"/></filter>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="softglow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="22"/></filter>
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" seed="3" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 0.16"/></feComponentTransfer></filter>
</defs>

<rect width="{W}" height="{HORIZON}" fill="url(#sky)"/>
<rect y="{HORIZON}" width="{W}" height="{W - HORIZON}" fill="url(#floor)"/>

<!-- sun halo + 8-bit sun -->
<circle cx="{CX}" cy="{CY}" r="{R + 40}" fill="#ff4f9a" opacity="0.28" filter="url(#softglow)"/>
<g mask="url(#sunmask)"><path d="{pixel_sun_path()}" fill="url(#sun)" shape-rendering="crispEdges"/></g>

<!-- quantized waveform crossing the horizon -->
<path d="{stair_wave(HORIZON - 8, 90, 5.5)}" fill="none" stroke="#6ff3ff" stroke-width="2.4"
      shape-rendering="crispEdges" filter="url(#glow)" opacity="0.9"/>

<!-- reflection of sun and wave, shimmering like heat haze -->
<g mask="url(#reflmask)" filter="url(#haze)">
  <g transform="translate(0,{2 * HORIZON}) scale(1,-1)">
    <g mask="url(#sunmask)"><path d="{pixel_sun_path()}" fill="url(#sun)"/></g>
    <path d="{stair_wave(HORIZON - 8, 90, 5.5)}" fill="none" stroke="#6ff3ff" stroke-width="2.4"/>
  </g>
</g>
<rect x="0" y="{HORIZON - 1}" width="{W}" height="2" fill="#ffb3dc" filter="url(#glow)"/>

<!-- title + hazy reflection -->
<text class="title" x="{CX + 13}" y="800" text-anchor="middle" fill="#ff3f9a" opacity="0.45"
      filter="url(#softglow)">MIRAGE</text>
<text class="title" x="{CX + 13}" y="800" text-anchor="middle" fill="url(#chrome)"
      stroke="#ffffff" stroke-opacity="0.35" stroke-width="1">MIRAGE</text>
<g filter="url(#haze)" opacity="0.32">
  <text class="title" x="{CX + 13}" y="-806" text-anchor="middle" fill="url(#chrome)"
        transform="scale(1,-1)" style="mask: none">MIRAGE</text>
</g>
<rect x="0" y="806" width="{W}" height="{W - 806}" fill="url(#floor)" opacity="0.55"/>

<!-- type -->
<text class="artist" x="{CX}" y="92" text-anchor="middle">CLAUDE THE SONGWRITER</text>
<rect x="{CX - 40}" y="112" width="80" height="2" fill="#ff7ab8"/>
<text class="small" x="60" y="948">F MINOR  /  103 BPM  /  8-BIT</text>
<text class="small" x="{W - 60}" y="948" text-anchor="end">INSTRUMENTAL  2026</text>

<rect width="{W}" height="{W}" filter="url(#grain)"/>
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
