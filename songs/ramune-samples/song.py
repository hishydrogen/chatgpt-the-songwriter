"""Samples before redoing checkpoint 3 of ラムネ ("Last Summer"): the user asked for Kumi
instead of Hikari One, a stronger dance-rock groove and fewer groove types.

Part 1 - Kumi (筆墨クミ) sings the chorus hook, plain and strong voice, at the chorus key (D)
         and at the last-chorus key (E, a step up, top note F#5), over the dance-rock groove
         the user liked (palette pick B of songs/summer-groove).
Part 2 - three stronger dance-rock grooves, each 8 bars with the riff and 8 bars under the
         sung hook:
    1 "tambourine + upstrokes"  tambourine 16ths, left guitar cutting 16ths, right guitar
                                open upstroke stabs on every &, octave bass with ghosts
    2 "disco hats + gallop"     clap on the snare, tss-ka 16th hats, galloping bass, both
                                guitars chugging palm-muted 16ths with open accents
    3 "sprint four"             an extra kick on the a of 2, 16th hats, a snare run every other
                                bar, left guitar tremolo, right guitar cutting
`python songs/ramune-samples/song.py` prints the timestamp table.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("last_summer", Path(__file__).parent.parent / "last-summer" / "song.py")
ls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ls)

HOOK_PROG = ls.CHORUS[:8]
_b, LAST8 = 0.0, []
for _n in ls.LAST_MEL:            # first 8 bars of the last chorus
    if _b >= 32 - 1e-9:
        break
    LAST8.append(_n)
    _b += _n[2]

KUMI = [
    ("kumi A: plain", HOOK_PROG, 0, ls.HOOK, None),
    ("kumi B: strong", HOOK_PROG, 0, ls.HOOK, ls.STRONG),
    ("kumi C: plain, last-chorus key", ls.LAST[:8], 2, LAST8, None),
    ("kumi D: strong, last-chorus key", ls.LAST[:8], 2, LAST8, ls.STRONG),
]
GROOVES = [("1", "tamb", "tambourine + upstrokes"), ("2", "disco", "disco hats + gallop"),
           ("3", "sprint", "sprint four")]
FORM = [(k[0], k[1], k[2]) for k in KUMI]
for num, style, desc in GROOVES:
    FORM += [(f"groove {num}: {desc}", ls.RIFF_PROG, 0), (f"groove {num} + vocal", HOOK_PROG, 0)]


def compose():
    a = ls.Arranger(FORM, title="Ramune samples")
    s = a.s
    vox_cfg = None
    for label, prog, tr, mel, x in KUMI:          # part 1: the groove from the sketch (B)
        b0, n, tr = a.span(label)
        a.drums_four(b0, n, fill="snare" if "C" not in label else "toms")
        a.bass_octaves(b0, n)
        a.gtr_cut(b0, n, vel=.95)
        a.arpeggio(b0, n, vel=.9)
        t = s.track(label, ls.VOX)
        t.opts.update(ls.VOX_OPTS)
        b = b0
        for p, lyr, d in mel:
            if p != "r":
                t.note(ls.note_number(p) + tr, b, d, 100, lyric=lyr, x=dict(x) if x else None)
            b += d
    for num, style, desc in GROOVES:              # part 2: stronger dance rock
        for label in (f"groove {num}: {desc}", f"groove {num} + vocal"):
            b0, n, tr = a.span(label)
            vocal = label.endswith("vocal")
            a.drums_dance(b0, n, style, fill="toms" if vocal else "flams")
            a.bass_dance(b0, n, style)
            a.gtr_dance(b0, n, style)
            if vocal:
                a.arpeggio(b0, n, vel=.85)
                a.strings(b0, n, vel=.85)
                a.sing(b0, ls.HOOK, tr)
            else:
                a.lead_line(b0, ls.RIFF, tr)
                a.glock_line(b0, ls.RIFF, tr)
    a.mix()
    for label, *_ in KUMI:
        s.mix["tracks"][label] = dict(s.mix["tracks"]["vocal"])
    a.prune()
    s.length_beats = s.bar(a.total_bars) + 4
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
