"""Groove sketch for "Last Summer": the face riff and the groove, three versions back to
back, each 8 bars on its own (riff) and then 8 bars under the sung hook (170 BPM, D major).

    riff:  | Gmaj7 | A | F#m7 | Bm7 | Gmaj7 | A | Bm7 | Bm7 |
    hook:  | Gmaj7 | A | F#m7 | Bm7 | Em7 | F#m7 | Gmaj7 | A |
A  "8-beat drive"   rock 8-beat, open power-chord 8ths (Mesa, left/right), root 8ths on the
                    drive bass, rock piano; the riff on lead guitar doubled by glockenspiel.
B  "Dance rock"     four-on-the-floor kick, open hats on the &, 16th guitar cutting,
                    octave bass, crunch arpeggio guitar; the riff on upright piano + glock.
C  "16-beat sprint" syncopated kick, 16th hats and ghost snares, tremolo-picked guitars,
                    16th piano arpeggios, strings; the riff on lead guitar + glock.
`python songs/summer-groove/song.py` prints the timestamp table.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("last_summer", Path(__file__).parent.parent / "last-summer" / "song.py")
ls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ls)

HOOK_PROG = ls.CHORUS[:8]
FORM = [
    ("A 8-beat drive", ls.RIFF_PROG, 0), ("A + vocal", HOOK_PROG, 0),
    ("B dance rock", ls.RIFF_PROG, 0), ("B + vocal", HOOK_PROG, 0),
    ("C 16-beat sprint", ls.RIFF_PROG, 0), ("C + vocal", HOOK_PROG, 0),
]


def compose():
    a = ls.Arranger(FORM, title="Summer groove sketch")
    fills = iter(["toms", "flams", "snare", "toms", "flams", "snare"])
    for name, _, _ in FORM:
        b0, n, tr = a.span(name)
        vocal = name.endswith("vocal")
        if name.startswith("A"):
            a.drums_8beat(b0, n, fill=next(fills), ride=vocal)
            a.bass_8ths(b0, n)
            a.gtr_wall(b0, n, vel=0.95 if vocal else 1.0)
            a.piano_8ths(b0, n, vel=0.65)
            if vocal:
                a.strings(b0, n, vel=0.9)
            else:
                a.lead_line(b0, ls.RIFF)
                a.glock_line(b0, ls.RIFF)
        elif name.startswith("B"):
            a.drums_four(b0, n, fill=next(fills))
            a.bass_octaves(b0, n)
            a.gtr_cut(b0, n, vel=0.95)
            a.arpeggio(b0, n, vel=0.9)
            if not vocal:
                a.piano_riff(b0, ls.RIFF)
                a.glock_line(b0, ls.RIFF)
        else:
            a.drums_sprint(b0, n, fill=next(fills))
            a.bass_drive16(b0, n)
            a.gtr_trem(b0, n, vel=0.95)
            a.piano_arp16(b0, n, vel=0.7)
            a.strings(b0, n, vel=0.9)
            if not vocal:
                a.lead_line(b0, ls.RIFF)
                a.glock_line(b0, ls.RIFF)
        if vocal:
            a.sing(b0, ls.HOOK, tr)
    a.mix()
    a.prune()
    a.s.length_beats = a.s.bar(a.total_bars) + 4
    return a.s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
