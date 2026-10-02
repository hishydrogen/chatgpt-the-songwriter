"""Groove sketch for Neon Night: the riff and groove, three versions back to back, each
8 bars on its own and then 8 bars with the sung hook on top (132 BPM, F major).

    | Bbmaj7 | C | Am7 | Dm7 | Gm7 | C/E | Fmaj7 Dbmaj7 | Gm7 C7sus4 |
A  "House riff"      tresillo house piano + supersaw doubling the riff; four-on-the-floor
                     kick, off-beat octave bass.
B  "Pump"            supersaw on every 8th, pumping against the kick; the piano riff plays
                     only every other bar (call and response); 3-3-2 syncopated bass.
C  "Dance funk"      16th piano comping, saw stabs on the & of 2 and the e of 4,
                     J-pop dance beat with a syncopated punch kick, slap bass in 16ths.
`python songs/neon-groove/song.py` prints the timestamp table.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("neon_night", Path(__file__).parent.parent / "neon-night" / "song.py")
nn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nn)

FORM = [
    ("A house riff", nn.CHORUS, 0), ("A + vocal", nn.CHORUS, 0),
    ("B pump", nn.CHORUS, 0), ("B + vocal", nn.CHORUS, 0),
    ("C dance funk", nn.CHORUS, 0), ("C + vocal", nn.CHORUS, 0),
]


def compose():
    a = nn.Arranger(FORM, title="Neon groove sketch")
    for name, _, _ in FORM:
        b0, n, tr = a.span(name)
        if name.startswith("A"):
            a.drums_house(b0, n)
            a.bass_house(b0, n)
            a.riff(b0, n)
        elif name.startswith("B"):
            a.drums_house(b0, n)
            a.bass_sync(b0, n)
            a.saw_pump(b0, n)
            for bar in range(0, n, 2):
                a.riff(b0 + bar * 4, 1, saw=False, pickups=False)
        else:
            a.drums_dance(b0, n)
            a.bass_funk(b0, n)
            a.piano_funk(b0, n)
            a.saw_stabs(b0, n)
        if name.endswith("vocal"):
            a.sing(b0, nn.HOOK)
    a.mix()
    a.s.length_beats = a.s.bar(a.total_bars) + 4
    return a.s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
