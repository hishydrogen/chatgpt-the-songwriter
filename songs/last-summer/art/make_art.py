#!/usr/bin/env python3
"""Album art for 「ラムネ」: one image - a ramune bottle against an August sky, the glass
marble caught in its neck (the song's metaphor: you can see that summer, you can't take it
out), a towering summer cloud behind it, bubbles rising. No character, no logos; the title
in vertical Shippori Mincho, the credit small at the foot.

cover.html -> headless Chromium at 3x -> cover.png (3000x3000) -> cover.jpg
"""
import math
import random
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = 1000
TILT = -9             # degrees, bottle leaning left
BX, BY = 400, 820     # bottle origin (local 0,0) on the canvas
S = 1.32              # bottle scale: the neck and the marble carry the picture
rng = random.Random(813)


def bottle_path():
    """Codd-neck bottle outline in local coordinates (x right, y down; the body runs off the
    bottom of the sleeve). Right side top to bottom, then mirrored back up."""
    right = [("M", (0, -560)), ("L", (37, -560)), ("C", (41, -559), (42, -551), (41, -540)),
             ("C", (40, -531), (36, -526), (32, -522)), ("L", (31, -428)),
             ("C", (31, -404), (66, -392), (66, -336)), ("C", (66, -290), (44, -276), (39, -254)),
             ("C", (37, -238), (58, -220), (80, -196)), ("C", (101, -172), (117, -146), (117, -112)),
             ("L", (117, 700))]
    d = []
    for cmd, *pts in right:
        d.append(cmd + " " + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts))
    # mirror: walk the right side backwards with x negated
    left = [(-117, 700), (-117, -112)]
    back = [("C", (-117, -146), (-101, -172), (-80, -196)), ("C", (-58, -220), (-37, -238), (-39, -254)),
            ("C", (-44, -276), (-66, -290), (-66, -336)), ("C", (-66, -392), (-31, -404), (-31, -428)),
            ("L", (-32, -522)), ("C", (-36, -526), (-40, -531), (-41, -540)),
            ("C", (-42, -551), (-41, -559), (-37, -560)), ("Z",)]
    d.append(f"L {left[0][0]},{left[0][1]} L {left[1][0]},{left[1][1]}")
    for cmd, *pts in back:
        d.append(cmd + " " + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts))
    return " ".join(d)


def cloud():
    """A towering summer cloud rising from behind the horizon at the lower right: puffs
    stacked into a tower, edges broken up by fractal-noise displacement, lit from the upper
    left (a shadow copy offset down-right, a vertical light-to-shade gradient on top)."""
    puffs = []
    cx, base = 800, 920
    for i in range(95):
        h = rng.random() ** 0.9
        y = base - h * 470
        spread = 230 * (1 - h) ** 0.7 + 50
        x = cx + rng.uniform(-spread, spread)
        r = rng.uniform(30, 70) * (1.25 - 0.55 * h)
        puffs.append((x, y, r))
    mass = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in puffs)
    base_rect = f'<rect x="{cx - 430}" y="{base - 95}" width="860" height="300" rx="80"/>'
    return (f'<g filter="url(#billow)">'
            f'<g fill="#a9bfd8" transform="translate(14,18)">{mass}{base_rect}</g>'
            f'<g fill="url(#cloudBody)">{mass}{base_rect}</g></g>')


def bubbles():
    out = []
    for col in range(9):
        x = rng.uniform(-95, 95)
        y = rng.uniform(80, 640)
        for k in range(rng.randint(4, 9)):
            r = rng.uniform(1.8, 5.5) * (1 - k * 0.06)
            y -= rng.uniform(16, 38)
            x += rng.uniform(-4, 4)
            if y < -120:
                break
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="#ffffff" '
                       f'stroke-opacity="0.75" stroke-width="1.1"/>'
                       f'<circle cx="{x - r * .35:.1f}" cy="{y - r * .35:.1f}" r="{r * .3:.1f}" fill="#ffffff" opacity="0.85"/>')
    return "".join(out)


def droplets():
    out = []
    for _ in range(26):
        x = rng.uniform(-100, 100)
        y = rng.uniform(-90, 640)
        rx = rng.uniform(2.5, 6.5)
        ry = rx * rng.uniform(1.1, 1.6)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#drop)"/>'
                   f'<ellipse cx="{x - rx * .3:.1f}" cy="{y - ry * .35:.1f}" rx="{rx * .3:.1f}" ry="{ry * .25:.1f}" '
                   f'fill="#ffffff" opacity="0.9"/>')
    return "".join(out)


def svg():
    path = bottle_path()
    liquid_top = -150
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1d63b8"/><stop offset="0.45" stop-color="#4a97da"/>
    <stop offset="0.8" stop-color="#a9d3f0"/><stop offset="1" stop-color="#e3f1f8"/>
  </linearGradient>
  <radialGradient id="sun" cx="0.12" cy="0.06" r="0.55">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.55"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="cloudLit" cx="0.38" cy="0.32" r="0.7">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.7" stop-color="#f7fbfe"/><stop offset="1" stop-color="#e2ecf5"/>
  </radialGradient>
  <radialGradient id="cloudShade" cx="0.5" cy="0.5" r="0.6">
    <stop offset="0" stop-color="#cbd9e8"/><stop offset="1" stop-color="#b9cde2"/>
  </radialGradient>
  <filter id="soft" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.6"/></filter>
  <linearGradient id="cloudBody" gradientUnits="userSpaceOnUse" x1="0" y1="330" x2="0" y2="900">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.55" stop-color="#f4f8fc"/><stop offset="1" stop-color="#c9d8e8"/>
  </linearGradient>
  <filter id="billow" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency="0.014" numOctaves="4" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="46" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="1.4"/>
  </filter>
  <filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#e6fbff" stop-opacity="0.62"/><stop offset="0.18" stop-color="#b8ecf5" stop-opacity="0.32"/>
    <stop offset="0.55" stop-color="#7fd0e2" stop-opacity="0.2"/><stop offset="0.86" stop-color="#3f9fc0" stop-opacity="0.34"/>
    <stop offset="1" stop-color="#1d6f93" stop-opacity="0.62"/>
  </linearGradient>
  <linearGradient id="soda" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#bff3ff" stop-opacity="0.55"/><stop offset="0.5" stop-color="#6fd1e6" stop-opacity="0.42"/>
    <stop offset="1" stop-color="#2b8fb4" stop-opacity="0.62"/>
  </linearGradient>
  <radialGradient id="marble" cx="0.36" cy="0.32" r="0.75">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.95"/><stop offset="0.22" stop-color="#d8f8ff" stop-opacity="0.9"/>
    <stop offset="0.6" stop-color="#6ccbe4" stop-opacity="0.85"/><stop offset="1" stop-color="#1b6488" stop-opacity="0.95"/>
  </radialGradient>
  <radialGradient id="drop" cx="0.4" cy="0.35" r="0.7">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.5"/><stop offset="1" stop-color="#2b7fa3" stop-opacity="0.45"/>
  </radialGradient>
  <clipPath id="inside"><path d="{path}"/></clipPath>
</defs>
<rect width="{W}" height="{W}" fill="url(#sky)"/>
<rect width="{W}" height="{W}" fill="url(#sun)"/>
{cloud()}
<g transform="translate({BX},{BY}) rotate({TILT}) scale({S})">
  <!-- shadow-side refraction of the sky through the glass -->
  <path d="{path}" fill="url(#glass)"/>
  <g clip-path="url(#inside)">
    <g transform="rotate({-TILT})">
      <rect x="-400" y="{liquid_top}" width="800" height="1200" fill="url(#soda)"/>
      <rect x="-400" y="{liquid_top - 3}" width="800" height="5" fill="#ffffff" opacity="0.55"/>
    </g>
    {bubbles()}
    <!-- inner shadow along the right wall, caustic glow under the marble -->
    <path d="M 98,-120 L 98,700 L 140,700 L 140,-120 Z" fill="#0e4f70" opacity="0.28" filter="url(#blur8)"/>
    <ellipse cx="6" cy="-236" rx="30" ry="9" fill="#ffffff" opacity="0.45" filter="url(#blur3)"/>
  </g>
  <!-- the marble in its cage -->
  <circle cx="2" cy="-318" r="47" fill="url(#marble)"/>
  <ellipse cx="6" cy="-293" rx="30" ry="12" fill="#0d4766" opacity="0.35" filter="url(#blur3)"/>
  <ellipse cx="-14" cy="-338" rx="13" ry="8" fill="#ffffff" opacity="0.95" transform="rotate(-30 -14 -338)"/>
  <circle cx="16" cy="-300" r="3.2" fill="#ffffff" opacity="0.8"/>
  {droplets()}
  <!-- glass edges and highlights -->
  <path d="{path}" fill="none" stroke="#2a8fb0" stroke-opacity="0.55" stroke-width="7"/>
  <path d="{path}" fill="none" stroke="#0f4f6e" stroke-opacity="0.5" stroke-width="2"/>
  <path d="M -96,-108 L -96,700" stroke="#ffffff" stroke-opacity="0.8" stroke-width="7" filter="url(#blur3)"/>
  <path d="M -80,-108 L -80,700" stroke="#ffffff" stroke-opacity="0.35" stroke-width="3"/>
  <path d="M -50,-372 C -52,-350 -50,-310 -42,-288" stroke="#ffffff" stroke-opacity="0.8" stroke-width="5" fill="none" filter="url(#blur3)"/>
  <path d="M -22,-515 L -22,-440" stroke="#ffffff" stroke-opacity="0.7" stroke-width="4" filter="url(#blur3)"/>
  <path d="M -98,-150 C -84,-178 -62,-206 -44,-224" stroke="#ffffff" stroke-opacity="0.65" stroke-width="4" fill="none" filter="url(#blur3)"/>
  <path d="M 96,-120 L 96,700" stroke="#0b3d58" stroke-opacity="0.35" stroke-width="5" filter="url(#blur3)"/>
  <ellipse cx="0" cy="-558" rx="37" ry="7" fill="none" stroke="#ffffff" stroke-opacity="0.8" stroke-width="2.5"/>
</g>
<!-- title, vertical, and the credit -->
<g font-family="Shippori" fill="#ffffff">
  <text x="872" y="150" font-size="92" text-anchor="middle">ラ</text>
  <text x="872" y="252" font-size="92" text-anchor="middle">ム</text>
  <text x="872" y="354" font-size="92" text-anchor="middle">ネ</text>
  <text x="948" y="928" font-size="20" letter-spacing="1.5" fill="#3d6286" text-anchor="end">Claude the Songwriter</text>
  <text x="948" y="960" font-size="20" letter-spacing="1.5" fill="#3d6286" text-anchor="end">feat. 筆墨クミ</text>
</g>
</svg>"""


HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Shippori; src: url('fonts/ShipporiMincho-Medium.ttf'); }}
html, body {{ margin: 0; padding: 0; background: #1d63b8; }}
svg {{ display: block; }}
</style></head><body>{svg()}</body></html>"""


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
