#!/usr/bin/env python3
"""Original jazz sleeve: a cream vocal ribbon dancing across a cobalt field.

Outline the lettering, then render the vector original to a 3000-square JPEG.
The design depicts no voicebank character and uses no stock or reference image.
"""
from pathlib import Path
import subprocess

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
@font-face {font-family:Fraunces;src:url(fonts/Fraunces-Italic.ttf);font-style:italic}
@font-face {font-family:Josefin;src:url(fonts/JosefinSans.ttf)}
html,body {margin:0;width:1000px;height:1000px;overflow:hidden;background:#173b86}
svg {display:block}
.title {font-family:Fraunces;font-style:italic;font-size:75px;font-weight:450;
  font-variation-settings:"SOFT" 60,"WONK" 0,"opsz" 144;letter-spacing:-1px}
.artist {font-family:Josefin;font-size:18px;font-weight:400;letter-spacing:4px}
.feature {font-family:Josefin;font-size:23px;font-weight:400;letter-spacing:1px}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000"
  role="img" aria-label="Swing, Milk! An ivory ribbon dances across a cobalt jazz sleeve.">
<rect width="1000" height="1000" fill="#173b86"/>
<g fill="#f9edd4">
  <text class="title" x="72" y="140">Swing, Milk!</text>
  <text class="artist" x="77" y="181">CLAUDE THE SONGWRITER</text>
</g>
<!-- A single, asymmetric ribbon: slow arcs and short curls mirror the scat phrasing. -->
<path fill="#f9edd4" d="M 790,309
 C 688,276 559,287 503,357
 C 447,427 491,474 586,471
 C 689,468 744,496 731,562
 C 713,650 586,706 465,684
 C 365,666 300,699 320,754
 C 338,804 449,817 530,781
 C 483,847 320,863 266,792
 C 208,715 289,629 416,631
 C 540,633 651,615 668,555
 C 681,510 601,522 546,518
 C 419,509 378,430 435,352
 C 504,258 680,244 790,309 Z"/>
<!-- A lifted counterstroke makes the central shape feel suspended. -->
<path fill="#f9edd4" d="M 440,627
 C 434,569 409,537 360,505
 C 337,490 310,482 287,484
 C 355,456 418,489 448,538
 C 471,575 481,609 479,638 Z"/>
<circle cx="803" cy="391" r="33" fill="#ed7043"/>
<ellipse cx="807" cy="510" rx="12" ry="19" transform="rotate(26 807 510)" fill="#ed7043"/>
<ellipse cx="755" cy="710" rx="10" ry="17" transform="rotate(38 755 710)" fill="#ed7043"/>
<text class="feature" x="927" y="928" text-anchor="end" fill="#f9edd4">feat. Milk</text>
</svg></body></html>"""


def lettering(text, font_name, size, spacing, x, y, location, right=False):
    font = TTFont(HERE / "fonts" / font_name)
    glyphs = font.getGlyphSet(location=location)
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    advance = 0
    paths = []
    for char in text:
        glyph = glyphs[cmap[ord(char)]]
        pen = SVGPathPen(glyphs)
        glyph.draw(pen)
        paths.append(f'<path transform="translate({advance:.4f},0)" d="{pen.getCommands()}"/>')
        advance += glyph.width + spacing / scale
    if right:
        x -= (advance - spacing / scale) * scale
    font.close()
    return f'<g transform="translate({x:.4f},{y}) scale({scale:.8f},-{scale:.8f})">' + "".join(paths) + "</g>"


def main():
    (HERE / "cover.html").write_text(HTML)
    svg = HTML[HTML.index("<svg"):HTML.index("</svg>") + len("</svg>")]
    svg = svg.replace('width="1000" height="1000" viewBox=', 'width="3000" height="3000" viewBox=', 1)
    svg = svg.replace('<text class="title" x="72" y="140">Swing, Milk!</text>',
                      lettering("Swing, Milk!", "Fraunces-Italic.ttf", 75, -1, 72, 140,
                                {"wght": 450, "SOFT": 60, "WONK": 0, "opsz": 144}))
    svg = svg.replace('<text class="artist" x="77" y="181">CLAUDE THE SONGWRITER</text>',
                      lettering("CLAUDE THE SONGWRITER", "JosefinSans.ttf", 18, 4, 77, 181, {"wght": 400}))
    svg = svg.replace('<text class="feature" x="927" y="928" text-anchor="end" fill="#f9edd4">feat. Milk</text>',
                      '<g fill="#f9edd4">' + lettering("feat. Milk", "JosefinSans.ttf", 23, 1,
                                                         927, 928, {"wght": 400}, right=True) + '</g>')
    (HERE / "cover.svg").write_text(svg)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "cover.svg"),
                    "-frames:v", "1", str(HERE / "cover.png")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "cover.png"),
                    "-q:v", "2", str(HERE / "cover.jpg")], check=True)
    print("Original cover exported: 3000 x 3000 PNG and JPEG")


if __name__ == "__main__":
    main()
