#!/usr/bin/env python3
"""Album art for "ドゥームスクロール (Doomscroll)": a homage to the reference sleeve's idea
(a flat grey-and-dark-red drawing inside an old desktop window), redrawn as a classic
Mac OS 8/9 "Platinum" window: pinstriped title bar, close / zoom / collapse boxes, lavender
scroll thumb, a menu bar whose clock reads 2:00 AM (the song's first line).
Inside: a notepad with the first lines of the song typed at 2 AM and a waiting caret,
and one Platinum alert on top: "まだ起きてる？" [寝る] [もう少しだけ] (default). Renders cover.html -> cover.png (3000x3000) with headless Chromium -> cover.jpg.
No logos: the Apple menu is a plain note glyph.
"""
import random
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = 1000

GREY_BG = "#8a8a8a"
SKIN = "#c9c9c9"
RED = "#7b1d22"
INK = "#141414"

# window geometry
WX0, WY0, WX1, WY1 = 34, 66, 966, 968
TB = 38          # title bar height
SB = 30          # scroll bar width
CX0, CY0 = WX0 + 8, WY0 + TB
CX1, CY1 = WX1 - 8 - SB, WY1 - 8 - SB


def pinstripes(x0, y0, x1, y1):
    out = []
    y = y0 + 9
    while y < y1 - 8:
        out.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="1.6" fill="#9a9a9a"/>'
                   f'<rect x="{x0}" y="{y + 1.6}" width="{x1 - x0}" height="1.4" fill="#ffffff"/>')
        y += 4.6
    return "".join(out)


def bevel_box(x, y, s, inner=""):
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="#d8d8d8" stroke="{INK}" stroke-width="1.6"/>'
            f'<path d="M{x + 2},{y + s - 2} V{y + 2} H{x + s - 2}" stroke="#ffffff" stroke-width="2" fill="none"/>'
            f'<path d="M{x + 2},{y + s - 1.5} H{x + s - 1.5} V{y + 2}" stroke="#8c8c8c" stroke-width="2" fill="none"/>'
            + inner)


def scroll_v():
    x = CX1
    y0, y1 = CY0, CY1
    track = f'<rect x="{x}" y="{y0}" width="{SB}" height="{y1 - y0}" fill="#e6e6e6" stroke="{INK}" stroke-width="1.4"/>'
    track += f'<rect x="{x + 4}" y="{y0 + SB}" width="{SB - 8}" height="{y1 - y0 - 2 * SB}" fill="#c4c4c4"/>'
    up = bevel_box(x, y0, SB, f'<path d="M{x + 9},{y0 + 19} L{x + 15},{y0 + 11} L{x + 21},{y0 + 19}Z" fill="{INK}"/>')
    dn = bevel_box(x, y1 - SB, SB, f'<path d="M{x + 9},{y1 - 19} L{x + 15},{y1 - 11} L{x + 21},{y1 - 19}Z" fill="{INK}"/>')
    # thumb almost at the bottom: a long way down an endless feed
    ty = y1 - SB - 74
    thumb = (f'<rect x="{x + 2}" y="{ty}" width="{SB - 4}" height="44" rx="2" fill="#c3c3f0" stroke="{INK}" stroke-width="1.4"/>'
             + "".join(f'<rect x="{x + 9}" y="{ty + 15 + 5 * i}" width="12" height="1.6" fill="#6f6fb0"/>'
                       f'<rect x="{x + 9}" y="{ty + 16.6 + 5 * i}" width="12" height="1.2" fill="#ffffff"/>' for i in range(3)))
    return track + up + dn + thumb


def scroll_h():
    y = CY1
    x0, x1 = CX0, CX1
    track = f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{SB}" fill="#e6e6e6" stroke="{INK}" stroke-width="1.4"/>'
    track += f'<rect x="{x0 + SB}" y="{y + 4}" width="{x1 - x0 - 2 * SB}" height="{SB - 8}" fill="#cfcfcf"/>'
    lf = bevel_box(x0, y, SB, f'<path d="M{x0 + 19},{y + 9} L{x0 + 11},{y + 15} L{x0 + 19},{y + 21}Z" fill="{INK}"/>')
    rt = bevel_box(x1 - SB, y, SB, f'<path d="M{x1 - 19},{y + 9} L{x1 - 11},{y + 15} L{x1 - 19},{y + 21}Z" fill="{INK}"/>')
    grow = bevel_box(x1, y, SB, "".join(
        f'<rect x="{x1 + 8 + 4 * i}" y="{y + 8 + 4 * i}" width="{14 - 4 * i}" height="{14 - 4 * i}" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>'
        for i in range(2)))
    return track + lf + rt + grow


def sparkle(x, y, r, color):
    return (f'<path d="M{x},{y - r} Q{x + r * 0.18},{y - r * 0.18} {x + r},{y} Q{x + r * 0.18},{y + r * 0.18} {x},{y + r} '
            f'Q{x - r * 0.18},{y + r * 0.18} {x - r},{y} Q{x - r * 0.18},{y - r * 0.18} {x},{y - r}Z" fill="{color}"/>')


def star(x, y, r, color, rot=-12):
    import math
    pts = []
    for i in range(10):
        a = math.radians(rot - 90 + 36 * i)
        rr = r if i % 2 == 0 else r * 0.48
        pts.append(f"{x + rr * math.cos(a):.1f},{y + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>'


LINE = "#2b2147"
HOOD = "#3b3f86"
HOOD_HI = "#5157a8"
EAR_IN = "#ff9ec8"
HAIR = "#b9a7ff"
HAIR_SH = "#9583ea"
SKIN_C = "#ffe6d8"
SKIN_SH = "#f7c9b6"
BG = "#f1ecfd"


def drawing_detailed():
    """Original character: a sleepy night-owl girl in a cat-ear hoodie, upper body only."""
    cx = (CX0 + CX1) / 2
    s = [f'<rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}" fill="{BG}"/>']
    # dotted desktop-pattern background and a few sparkles
    for y in range(int(CY0) + 12, int(CY1), 26):
        for x in range(int(CX0) + 12 + (13 if (y // 26) % 2 else 0), int(CX1), 26):
            s.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#ddd3f6"/>')
    for x, y, r, c in ((CX0 + 110, CY0 + 120, 26, "#ff9ec8"), (CX0 + 70, CY0 + 300, 14, "#7fd8ea"),
                       (CX1 - 120, CY0 + 150, 20, "#7fd8ea"), (CX1 - 80, CY0 + 330, 30, "#ff9ec8"),
                       (CX0 + 150, CY0 + 470, 12, "#b9a7ff"), (CX1 - 160, CY0 + 520, 14, "#b9a7ff")):
        s.append(sparkle(x, y, r, c))
    # hoodie body
    s.append(f'<path d="M{cx - 360},{CY1 + 5} C{cx - 340},{760} {cx - 270},{700} {cx - 150},{680} L{cx + 150},{680} '
             f'C{cx + 270},{700} {cx + 340},{760} {cx + 360},{CY1 + 5}Z" fill="{HOOD}" stroke="{LINE}" stroke-width="4"/>')
    # hood (behind the head) with cat ears
    for side in (-1, 1):
        s.append(f'<path d="M{cx + side * 70},{232} L{cx + side * 190},{118} L{cx + side * 215},{300}Z" fill="{HOOD}" '
                 f'stroke="{LINE}" stroke-width="4" stroke-linejoin="round"/>')
        s.append(f'<path d="M{cx + side * 110},{236} L{cx + side * 182},{160} L{cx + side * 196},{272}Z" fill="{EAR_IN}"/>')
    s.append(f'<path d="M{cx - 250},{700} C{cx - 290},{520} {cx - 260},{220} {cx},{215} C{cx + 260},{220} {cx + 290},{520} '
             f'{cx + 250},{700} Q{cx},{740} {cx - 250},{700}Z" fill="{HOOD}" stroke="{LINE}" stroke-width="4"/>')
    # hood lining (the opening around the face)
    s.append(f'<path d="M{cx - 205},{690} C{cx - 240},{520} {cx - 215},{270} {cx},{262} C{cx + 215},{270} {cx + 240},{520} '
             f'{cx + 205},{690} Q{cx},{715} {cx - 205},{690}Z" fill="{HOOD_HI}" stroke="{LINE}" stroke-width="3"/>')
    # back hair inside the hood
    s.append(f'<path d="M{cx - 190},{690} C{cx - 215},{520} {cx - 200},{300} {cx},{292} C{cx + 200},{300} {cx + 215},{520} '
             f'{cx + 190},{690} Q{cx},{705} {cx - 190},{690}Z" fill="{HAIR_SH}" stroke="{LINE}" stroke-width="3"/>')
    # neck
    s.append(f'<path d="M{cx - 40},{620} L{cx - 46},{690} Q{cx},{710} {cx + 46},{690} L{cx + 40},{620}Z" fill="{SKIN_SH}" '
             f'stroke="{LINE}" stroke-width="3"/>')
    # face
    fy = 335
    s.append(f'<path d="M{cx - 150},{fy + 90} C{cx - 156},{fy + 190} {cx - 110},{fy + 270} {cx},{fy + 310} '
             f'C{cx + 110},{fy + 270} {cx + 156},{fy + 190} {cx + 150},{fy + 90} C{cx + 150},{fy - 10} {cx - 150},{fy - 10} '
             f'{cx - 150},{fy + 90}Z" fill="{SKIN_C}" stroke="{LINE}" stroke-width="3.5"/>')
    # eyes
    s.append('<defs><linearGradient id="iris" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#6b1f78"/><stop offset="0.5" stop-color="#c84fb0"/>'
             '<stop offset="1" stop-color="#6fe0ee"/></linearGradient></defs>')
    for side in (-1, 1):
        ex, ey = cx + side * 68, fy + 165
        s.append(f'<ellipse cx="{ex}" cy="{ey}" rx="44" ry="50" fill="#ffffff"/>')
        s.append(f'<ellipse cx="{ex + side * 2}" cy="{ey + 4}" rx="36" ry="46" fill="url(#iris)" stroke="{LINE}" stroke-width="2.5"/>')
        s.append(f'<ellipse cx="{ex + side * 2}" cy="{ey + 2}" rx="15" ry="22" fill="#3a1046"/>')
        s.append(f'<ellipse cx="{ex - 13}" cy="{ey - 16}" rx="13" ry="16" fill="#ffffff"/>')
        s.append(f'<circle cx="{ex + 14}" cy="{ey + 22}" r="6" fill="#ffffff"/>')
        s.append(f'<circle cx="{ex - 4}" cy="{ey + 30}" r="3" fill="#ffffff" opacity="0.85"/>')
        # upper lash with an outer flick, small lower lash
        s.append(f'<path d="M{ex - side * 46},{ey - 26} Q{ex},{ey - 64} {ex + side * 50},{ey - 30} L{ex + side * 62},{ey - 40} '
                 f'L{ex + side * 54},{ey - 22} Q{ex},{ey - 52} {ex - side * 46},{ey - 26}Z" fill="{LINE}" '
                 f'stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>')
        s.append(f'<path d="M{ex - side * 18},{ey + 52} Q{ex + side * 10},{ey + 56} {ex + side * 30},{ey + 46}" '
                 f'stroke="{LINE}" stroke-width="3" fill="none" stroke-linecap="round"/>')
        # blush with hatch lines
        bx, by = cx + side * 98, fy + 232
        s.append(f'<ellipse cx="{bx}" cy="{by}" rx="34" ry="15" fill="#ff8fb8" opacity="0.55"/>')
        for k in range(3):
            s.append(f'<path d="M{bx - 16 + 13 * k},{by + 6} l7,-12" stroke="#f0628f" stroke-width="2.6" stroke-linecap="round"/>')
    # nose, cat mouth with a fang
    s.append(f'<path d="M{cx - 2},{fy + 222} l4,3" stroke="{LINE}" stroke-width="2.6" stroke-linecap="round"/>')
    s.append(f'<path d="M{cx - 24},{fy + 248} Q{cx - 12},{fy + 262} {cx},{fy + 248} Q{cx + 12},{fy + 262} {cx + 24},{fy + 248}" '
             f'stroke="{LINE}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    s.append(f'<path d="M{cx + 6},{fy + 253} l4,9 l4,-8" fill="#ffffff" stroke="{LINE}" stroke-width="1.8" stroke-linejoin="round"/>')
    # side locks
    for side in (-1, 1):
        s.append(f'<path d="M{cx + side * 160},{fy + 40} C{cx + side * 190},{fy + 160} {cx + side * 182},{fy + 280} '
                 f'{cx + side * 158},{fy + 345} Q{cx + side * 150},{fy + 312} {cx + side * 132},{fy + 300} '
                 f'Q{cx + side * 128},{fy + 330} {cx + side * 112},{fy + 340} '
                 f'C{cx + side * 130},{fy + 250} {cx + side * 140},{fy + 150} {cx + side * 112},{fy + 70}Z" '
                 f'fill="{HAIR}" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>')
    # bangs: curved strands of varied length, tips swept outward from the parting
    tips = [(-170, 128), (-146, 152), (-124, 92), (-96, 132), (-66, 90), (-34, 124), (-6, 86),
            (24, 120), (52, 84), (82, 126), (112, 92), (140, 150), (170, 128)]
    d = f"M{cx - 168},{fy + 128} C{cx - 196},{fy - 30} {cx - 90},{fy - 40} {cx},{fy - 40} " \
        f"C{cx + 90},{fy - 40} {cx + 196},{fy - 30} {cx + 168},{fy + 128}"
    for i in range(len(tips) - 1, 0, -1):
        (x1, y1), (x0, y0) = tips[i], tips[i - 1]
        mx = (x0 + x1) / 2
        notch = min(y0, y1) - 24
        d += f" Q{cx + x1 - (x1 - mx) * 0.2},{fy + notch + 12} {cx + mx},{fy + notch}" \
             f" Q{cx + x0 + (mx - x0) * 0.2},{fy + notch + 12} {cx + x0},{fy + y0}"
    s.append(f'<path d="{d}Z" fill="{HAIR}" stroke="{LINE}" stroke-width="3.5" stroke-linejoin="round"/>')
    for dx, dy in ((-96, 132), (-34, 124), (24, 120), (82, 126)):
        s.append(f'<path d="M{cx + dx * 0.6},{fy + 10} Q{cx + dx * 0.8},{fy + dy - 70} {cx + dx * 0.9},{fy + dy - 48}" '
                 f'stroke="{HAIR_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    s.append(f'<path d="M{cx - 100},{fy + 30} Q{cx - 40},{fy + 6} {cx + 30},{fy + 22}" stroke="#ffffff" stroke-width="8" '
             f'fill="none" stroke-linecap="round" opacity="0.6"/>')
    s.append(star(cx + 118, fy + 70, 30, "#ffe36e"))
    # hoodie front: drawstrings with aglets, collar seam
    s.append(f'<path d="M{cx - 120},{705} Q{cx},{760} {cx + 120},{705}" stroke="{LINE}" stroke-width="3" fill="none"/>')
    for side in (-1, 1):
        s.append(f'<path d="M{cx + side * 52},{730} C{cx + side * 58},{790} {cx + side * 46},{830} {cx + side * 56},{870}" '
                 f'stroke="#ffc6df" stroke-width="7" fill="none" stroke-linecap="round"/>')
        s.append(f'<rect x="{cx + side * 56 - 7}" y="{866}" width="14" height="24" rx="5" fill="#ffffff" stroke="{LINE}" stroke-width="2.5"/>')
    s.append(sparkle(cx - 170, 820, 18, "#ffe36e"))
    return "".join(s)


import os

VARIANT = os.environ.get("ART", "B")   # B (alert over a notepad) is the cover; A and C were drafts


def px_rect(x, y, w, h, fill):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'


def content_typo():
    """A: an empty document with the title in big bitmap type and a text cursor."""
    s = [px_rect(CX0, CY0, CX1 - CX0, CY1 - CY0, "#ffffff")]
    s.append(f'<text x="{CX0 + 70}" y="{CY0 + 330}" font-size="150" fill="{INK}">ドゥーム</text>')
    s.append(f'<text x="{CX0 + 70}" y="{CY0 + 520}" font-size="150" fill="{INK}">スクロール</text>')
    s.append(px_rect(CX0 + 75, CY0 + 560, 8, 150, INK))
    return "".join(s)


def pixel_moon(x0, y0, P):
    """32x32 bitmap: crescent (outside a shifted circle), 1-px black outline, two-tone fill."""
    N = 32
    inside = set()
    for r in range(N):
        for c in range(N):
            a = (c - 14.5) ** 2 + (r - 17.5) ** 2 <= 13.2 ** 2
            b = (c - 20.5) ** 2 + (r - 12.5) ** 2 <= 11.0 ** 2
            if a and not b:
                inside.add((r, c))
    out = []
    for r, c in inside:
        edge = any((r + dr, c + dc) not in inside for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        d = ((c - 14.5) ** 2 + (r - 17.5) ** 2) ** 0.5
        shade = d > 10.6 and (r - 17.5) + (14.5 - c) > 4
        col = INK if edge else ("#e0b830" if shade else "#ffe36e")
        out.append(f'<rect x="{x0 + c * P}" y="{y0 + r * P}" width="{P + 0.3}" height="{P + 0.3}" fill="{col}"/>')
    zs = [  # two small z's, top right
        (3, 22, ["XXXX", "..X.", ".X..", "XXXX"]),
        (9, 27, ["XXX", ".X.", "XXX"]),
    ]
    for r0, c0, rows in zs:
        for dr, row in enumerate(rows):
            for dc, ch in enumerate(row):
                if ch == "X":
                    out.append(f'<rect x="{x0 + (c0 + dc) * P}" y="{y0 + (r0 + dr) * P}" width="{P + 0.3}" '
                               f'height="{P + 0.3}" fill="{INK}"/>')
    return "".join(out)


def button(x, y, w, h, label, default=False):
    out = ""
    if default:
        out += f'<rect x="{x - 7}" y="{y - 7}" width="{w + 14}" height="{h + 14}" rx="{h / 2 + 7}" fill="none" stroke="{INK}" stroke-width="5"/>'
    out += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="#e4e4e4" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{x + h / 2},{y + 3} H{x + w - h / 2}" stroke="#ffffff" stroke-width="3"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 + 9}" font-size="26" fill="{INK}" text-anchor="middle">{label}</text>')
    return out


def content_alert():
    """B: one Platinum alert dialog: "still awake?" [寝る] [もう少しだけ]."""
    # behind the dialog: a notepad document, a few lines typed at 2 AM, caret waiting
    s = [px_rect(CX0, CY0, CX1 - CX0, CY1 - CY0, "#ffffff")]
    memo = ["午前二時のコンビニの光", "レシートだけ ポケットで鳴る", "既読つかない 吹き出しを", "親指で 何度も なぞる"]
    for i, line in enumerate(memo):
        s.append(f'<text x="{CX0 + 26}" y="{CY0 + 46 + 38 * i}" font-size="25" fill="{INK}">{line}</text>')
    s.append(px_rect(CX0 + 27, CY0 + 46 + 38 * 4 - 24, 2.5, 30, INK))
    # the alert sits dead centre on the screen, like a real modal dialog
    dw, dh = 706, 340
    dx0, dy0 = W / 2 - dw / 2, W / 2 - dh / 2
    dx1, dy1 = dx0 + dw, dy0 + dh
    s.append(px_rect(dx0 + 8, dy0 + 8, dx1 - dx0, dy1 - dy0, "rgba(0,0,0,0.35)"))
    s.append(f'<rect x="{dx0}" y="{dy0}" width="{dx1 - dx0}" height="{dy1 - dy0}" fill="#dddddd" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M{dx0 + 3},{dy1 - 3} V{dy0 + 3} H{dx1 - 3}" stroke="#ffffff" stroke-width="3" fill="none"/>')
    s.append(f'<path d="M{dx0 + 3},{dy1 - 3} H{dx1 - 3} V{dy0 + 3}" stroke="#9a9a9a" stroke-width="3" fill="none"/>')
    # alert icon: a 32x32 pixel crescent moon with "z z", drawn like a System 7/8 icon
    ix, iy = dx0 + 40, dy0 + 44
    s.append(pixel_moon(ix, iy, 3.4))
    s.append(f'<text x="{ix + 130}" y="{dy0 + 92}" font-size="40" fill="{INK}">まだ起きてる？</text>')
    s.append(f'<text x="{ix + 130}" y="{dy0 + 142}" font-size="24" fill="#3c3c3c">午前2時です。スクロールを続けますか？</text>')
    s.append(button(dx1 - 520, dy1 - 90, 170, 52, "寝る"))
    s.append(button(dx1 - 300, dy1 - 90, 240, 52, "もう少しだけ", default=True))
    return "".join(s)


def content_watch():
    """C: an empty window and one big pixel wristwatch cursor, hands at 2:00."""
    s = [px_rect(CX0, CY0, CX1 - CX0, CY1 - CY0, "#ffffff")]
    P = 22   # pixel size
    art = [
        "....XXXXXXX....",
        "....X.....X....",
        "....XXXXXXX....",
        "...XX.....XX...",
        "..X....X....X..",
        ".X.....X.....X.",
        ".X.....X..X..X.",
        ".X.....X.X...XX",
        ".X.....XX....X.",
        ".X...........X.",
        "..X.........X..",
        "...XX.....XX...",
        "....XXXXXXX....",
        "....X.....X....",
        "....XXXXXXX....",
    ]
    ox = (CX0 + CX1) / 2 - len(art[0]) * P / 2
    oy = (CY0 + CY1) / 2 - len(art) * P / 2
    # white fill inside the face, black pixels on top
    s.append(f'<circle cx="{ox + 7.5 * P}" cy="{oy + 7.5 * P}" r="{5.8 * P}" fill="#ffffff"/>')
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch == "X":
                s.append(px_rect(ox + c * P, oy + r * P, P + 0.5, P + 0.5, INK))
    s.append(f'<text x="{(CX0 + CX1) / 2}" y="{CY1 - 60}" font-size="26" fill="#6a6a6a" text-anchor="middle">loading...</text>')
    return "".join(s)


def drawing():
    return {"A": content_typo, "B": content_alert, "C": content_watch}[VARIANT]()


HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Dot; src: url(fonts/DotGothic16-Regular.ttf); }}
html, body {{ margin: 0; padding: 0; background: #636594; }}
svg {{ display: block; }}
text {{ font-family: Dot, monospace; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}">
  <rect width="{W}" height="{W}" fill="#636594"/>
  <!-- menu bar -->
  <rect x="0" y="0" width="{W}" height="34" fill="#eeeeee"/>
  <rect x="0" y="34" width="{W}" height="1.6" fill="{INK}"/>
  <text x="22" y="25" font-size="22" fill="{INK}">&#9834;</text>
  <text x="62" y="25" font-size="19" fill="{INK}">File</text>
  <text x="122" y="25" font-size="19" fill="{INK}">Edit</text>
  <text x="182" y="25" font-size="19" fill="{INK}">View</text>
  <text x="246" y="25" font-size="19" fill="{INK}">Special</text>
  <text x="336" y="25" font-size="19" fill="{INK}">Help</text>
  <text x="{W - 22}" y="25" font-size="19" fill="{INK}" text-anchor="end">2:00 AM</text>
  <!-- window shadow + frame -->
  <rect x="{WX0 + 6}" y="{WY0 + 6}" width="{WX1 - WX0}" height="{WY1 - WY0}" fill="#000" opacity="0.35"/>
  <rect x="{WX0}" y="{WY0}" width="{WX1 - WX0}" height="{WY1 - WY0}" fill="#dddddd" stroke="{INK}" stroke-width="1.8"/>
  <path d="M{WX0 + 2},{WY1 - 2} V{WY0 + 2} H{WX1 - 2}" stroke="#ffffff" stroke-width="2.5" fill="none"/>
  <path d="M{WX0 + 2},{WY1 - 2} H{WX1 - 2} V{WY0 + 2}" stroke="#9a9a9a" stroke-width="2.5" fill="none"/>
  {pinstripes(WX0 + 8, WY0, WX1 - 8, WY0 + TB)}
  {bevel_box(WX0 + 14, WY0 + 10, 18)}
  {bevel_box(WX1 - 60, WY0 + 10, 18, f'<rect x="{WX1 - 56}" y="{WY0 + 14}" width="8" height="8" fill="none" stroke="{INK}" stroke-width="1.2"/>')}
  {bevel_box(WX1 - 34, WY0 + 10, 18, f'<rect x="{WX1 - 30}" y="{WY0 + 18}" width="10" height="2.2" fill="{INK}"/>')}
  <rect x="{W / 2 - 150}" y="{WY0 + 6}" width="300" height="{TB - 12}" fill="#dddddd"/>
  <text x="{W / 2}" y="{WY0 + 27}" font-size="21" fill="{INK}" text-anchor="middle">&#9834; ドゥームスクロール</text>
  <!-- content -->
  <svg x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}" viewBox="{CX0} {CY0} {CX1 - CX0} {CY1 - CY0}">
    {drawing()}
  </svg>
  <rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}" fill="none" stroke="{INK}" stroke-width="1.6"/>
  {scroll_v()}
  {scroll_h()}
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
