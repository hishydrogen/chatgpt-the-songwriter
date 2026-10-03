"""Last Summer (working title) - an early-2010s vocaloid rock song in the spirit of
siinamota's "少女A" (2013): style, harmony vocabulary, groove and sound only; all material
is original. D major, 170 BPM, straight 8ths and 16ths, a wall of double-tracked
distorted guitars, piano, and a sung Japanese vocal (UTAU voicebank through
songwriter.voice). Theme: the summer you can't go back to.

Material (chords, hook, lyrics) lives here; the palette and groove sketches import it.
"""
from __future__ import annotations

from songwriter.song import chord_notes, note_number

BPM = 170
KEY = "D"

# -- harmony ---------------------------------------------------------------------------
# Chorus: IV-V-iii-vi ("王道進行"), a rising ii-iii-IV-V, again, and an unresolved end on vi.
CHORUS = ["Gmaj7", "A", "F#m7", "Bm7", "Em7", "F#m7", "Gmaj7", "A",
          "Gmaj7", "A", "F#m7", "Bm7", "Em7", "A", "Bm7", "Bm7"]

# -- melody ----------------------------------------------------------------------------
# (pitch or "r", lyric, beats); one mora per note.
#   かえりたい かえりたいよ / ビー玉に とじこめた夏
#   君の声も 青い空も / まだ ここで 光ってる
HOOK = [
    ("A4", "か", .5), ("B4", "え", .5), ("D5", "り", .5), ("E5", "た", 1.5), ("D5", "い", .5), ("r", "", .5),
    ("A4", "か", .5), ("B4", "え", .5), ("C#5", "り", .5), ("E5", "た", 1.0), ("D5", "い", .5),
    ("C#5", "よ", .75), ("r", "", .25),
    ("C#5", "び", 1.0), ("B4", "だ", .5), ("A4", "ま", .5), ("A4", "に", .5), ("r", "", .5),
    ("F#4", "と", .5), ("A4", "じ", .5),
    ("B4", "こ", .5), ("D5", "め", .5), ("D5", "た", .5), ("B4", "な", 1.0), ("A4", "つ", .5), ("r", "", 1.0),
    ("B4", "き", .5), ("B4", "み", .5), ("A4", "の", .5), ("B4", "こ", .5), ("D5", "え", 1.0), ("B4", "も", .5),
    ("r", "", .5),
    ("C#5", "あ", .5), ("C#5", "お", .5), ("B4", "い", .5), ("C#5", "そ", .5), ("E5", "ら", 1.0),
    ("C#5", "も", .5), ("r", "", .5),
    ("D5", "ま", .5), ("D5", "だ", 1.0), ("r", "", .5), ("B4", "こ", .5), ("D5", "こ", .5), ("E5", "で", 1.0),
    ("C#5", "ひ", .5), ("E5", "か", .5), ("r", "", .25), ("E5", "て", .75), ("E5", "る", 1.0), ("r", "", 1.0),
]
assert sum(d for *_, d in HOOK) == 8 * 4

# -- voicing helpers ---------------------------------------------------------------------


def pcs(name: str, tr: int = 0) -> set[int]:
    """Pitch classes of a chord symbol (slash bass excluded)."""
    return {(p + tr) % 12 for p in chord_notes(name.split("/")[0], 4)}


def root_of(name: str, lo: str = "E1", hi: str = "D#2", tr: int = 0) -> int:
    """Root (or slash bass) between lo and hi."""
    sym = name.split("/")[1] if "/" in name else name
    letter = sym[:2] if len(sym) > 1 and sym[1] in "#b" else sym[:1]
    n = note_number(f"{letter}1") + tr
    while n < note_number(lo):
        n += 12
    while n > note_number(hi):
        n -= 12
    return n


def power(name: str, tr: int = 0, octave: bool = True) -> list[int]:
    """Guitar power chord: root on the low E or A string (E2-D#3), fifth, octave."""
    r = root_of(name, "E2", "D#3", tr)
    return [r, r + 7, r + 12] if octave else [r, r + 7]


def voicing(name: str, top: int, n: int = 3, tr: int = 0) -> list[int]:
    """Top note plus the n nearest chord tones below it, no semitone between neighbours
    (the top's pitch class is doubled only when the chord has too few notes)."""
    ps = pcs(name, tr)
    out, p = [top], top - 1
    while len(out) < n + 1 and p > top - 20:
        if p % 12 in ps and out[-1] - p != 1 and (p % 12 != top % 12 or len(ps) < n + 1):
            out.append(p)
        p -= 1
    return sorted(out)
