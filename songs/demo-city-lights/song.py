"""City Lights - 55-second city-pop demo of the toolchain.

Intro (4) - Verse (8) - Chorus (8) - Outro (2), F major, 96 BPM.
"""
from songwriter.instruments import surge
from songwriter.song import Song, chord_notes

INTRO = ["Bbmaj7", "Am7", "Gm9", "C13"]
VERSE = ["Bbmaj7", "Am7", "Gm7", "C7sus4", "Bbmaj7", "Am7", "Dm9", "C9"]
CHORUS = ["Bbmaj7", "C/Bb", "Am7", "Dm7", "Gm9", "C13", "Fmaj9", "C7sus4"]

# (note, beat-in-bar, length) per chorus bar
MELODY = [
    [("A4", 0, 1), ("C5", 1, .5), ("D5", 1.5, .5), ("F5", 2, 1.5), ("E5", 3.5, .5)],
    [("D5", 0, 1), ("C5", 1, .5), ("A4", 1.5, 1), ("G4", 2.5, 1.5)],
    [("G4", 0, .5), ("A4", .5, .5), ("C5", 1, 1), ("E5", 2, 1), ("D5", 3, 1)],
    [("C5", 0, 2.5), ("A4", 2.5, .5), ("C5", 3, 1)],
    [("D5", 0, 1), ("F5", 1, 1), ("A5", 2, 1), ("G5", 3, .5), ("F5", 3.5, .5)],
    [("E5", 0, 1.5), ("D5", 1.5, .5), ("C5", 2, 1), ("A4", 3, 1)],
    [("G4", 0, .5), ("A4", .5, .5), ("C5", 1, 1), ("E5", 2, 2)],
    [("F5", 0, 3)],
]


def root_of(sym: str) -> str:
    sym = sym.split("/")[-1] if "/" in sym else sym
    return sym[:2] if len(sym) > 1 and sym[1] in "b#" else sym[0]


def compose() -> Song:
    s = Song("City Lights", bpm=96, key="F")
    rhodes = s.track("rhodes", "epiano.rhodes")
    pad = s.track("pad", surge("Pads/Pad 5"))
    bass = s.track("bass", "bass.darkblack")
    drums = s.track("drums", "drums.virtuosity")
    gtr = s.track("guitar", "guitar.funky_mute")
    vln = s.track("violins", "strings.violins_sus")
    vla = s.track("violas", "strings.violas_sus")
    vc = s.track("celli", "strings.celli_sus")
    sax = s.track("sax", "sax.alto")

    s.marker(0, "intro"); s.marker(s.bar(4), "verse"); s.marker(s.bar(12), "chorus"); s.marker(s.bar(20), "outro")
    sections = [(0, INTRO, "intro"), (4, VERSE, "verse"), (12, CHORUS, "chorus"), (20, ["Bbmaj7", "Fmaj9"], "outro")]

    for start, chords, sec in sections:
        for i, ch in enumerate(chords):
            b = s.bar(start + i)
            last = sec == "outro" and i == len(chords) - 1
            # Rhodes: sustained voicing + push on the "and" of 2 (city-pop comping)
            if sec in ("intro", "outro"):
                rhodes.chord(ch, b, 8 if last else 3.9, vel=58, octave=3, strum=0.03)
                rhodes.sustain(b, b + (8 if last else 3.9))
            else:
                rhodes.chord(ch, b, 1.4, vel=66, octave=3, strum=0.01)
                rhodes.chord(ch, b + 1.5, 0.4, vel=54, octave=3)
                rhodes.chord(ch, b + 2.5, 1.4, vel=60, octave=3)
            # pad: upper structure, whole bar
            if sec != "verse" or i >= 4:
                pad.chord(ch, b, 8 if last else 4, vel=64, octave=4)

            r = root_of(ch)
            if sec in ("verse", "chorus"):
                # bass: root, octave pop, approach note into the next bar
                bass.note(f"{r}1", b, 0.9, 98).note(f"{r}2", b + 1, 0.2, 72)
                bass.note(f"{r}1", b + 1.75, 0.5, 84).note(f"{r}1", b + 2.5, 0.75, 90)
                bass.note(f"{r}2", b + 3.25, 0.2, 70).note(f"{r}1", b + 3.5, 0.45, 82)
                # drums
                drums.hit("kick", b, 108).hit("kick", b + 1.75, 86).hit("kick", b + 2.5, 98)
                drums.hit("snare", b + 1, 104).hit("snare", b + 3, 108)
                drums.hit("snare_off", b + 2.75, 34)  # ghost note
                for k in range(16):
                    pos = b + k * 0.25
                    if sec == "chorus" and k in (6, 14):
                        drums.hit("hh_half", pos, 72)
                    else:
                        drums.hit("hh_closed", pos, (84, 50, 66, 48)[k % 4])
                if i == 0:
                    drums.hit("crash", b, 96 if sec == "chorus" else 82)
                # guitar: muted 16th chops on the off-beats
                top = sorted(chord_notes(ch, 4))[-3:]
                for off in (0.5, 1.75, 2.5, 3.5):
                    gtr.notes_at(top, b + off, 0.12, vel=78 if off in (0.5, 2.5) else 64)
            elif sec == "intro":
                drums.hit("hh_closed", b + 1, 52).hit("hh_closed", b + 3, 56)
                if i == 3:  # fill into the verse
                    for k, d in enumerate(["snare", "snare", "tom_high", "tom_high", "tom_low", "tom_low"]):
                        drums.hit(d, b + 2.5 + k * 0.25, 70 + 6 * k)
            else:  # outro
                if i == 0:
                    drums.hit("crash", b, 80).hit("kick", b, 100)
                    bass.note(f"{r}1", b, 3.5, 90)
                else:
                    bass.note("F1", b, 7, 90)
                    drums.hit("ride_bell", b, 60)

            # strings: chorus + outro, three-part voicing from the chord
            if sec in ("chorus", "outro"):
                notes = sorted(chord_notes(ch, 3))
                vc.note(f"{r}2", b, 8 if last else 4, 70)
                vla.note(notes[1] + 12, b, 8 if last else 4, 64)
                vln.note(notes[-1] + 12, b, 8 if last else 4, 66)
                vln.note(notes[-2] + 24, b, 8 if last else 4, 58)

    # alto sax melody in the chorus
    for i, bar in enumerate(MELODY):
        for note, pos, dur in bar:
            v = 92 if pos in (0, 2) else 82
            sax.note(note, s.bar(12 + i) + pos, dur * 0.95, v)

    rhodes.humanize(9, 5)
    bass.humanize(5, 4)
    drums.humanize(4, 7, skip_downbeats=True)
    gtr.humanize(5, 6)
    sax.humanize(10, 4)
    for t in (vln, vla, vc):
        t.humanize(15, 3)

    s.mix = {
        "tracks": {
            "drums": {"gain": 0, "eq": [("hpf", 30), ("bell", 80, -3, 2.0), ("bell", 450, -2.5, 1.0),
                              ("bell", 5000, 1.5, 0.8), ("hshelf", 9000, 3)],
                      "comp": {"threshold": -20, "ratio": 3, "attack": 12, "release": 90},
                      "saturate": {"drive_db": 4, "mix": 0.35}, "sends": {"room": -12}},
            "bass": {"gain": -0.5, "eq": [("hpf", 32), ("bell", 220, -2.5, 1.2), ("bell", 900, 2, 1.0)],
                     "comp": {"threshold": -24, "ratio": 4, "attack": 25, "release": 140},
                     "tube": {"drive": 1.5}, "duck": {"by": "drums", "depth": 2}, "mono": True},
            "rhodes": {"gain": -4, "eq": [("hpf", 110), ("bell", 320, -3, 0.9), ("bell", 2500, 1.5, 0.8)],
                       "comp": {"threshold": -22, "ratio": 2.5, "attack": 20, "release": 150},
                       "tube": {"drive": 2.5}, "width": 1.15, "sends": {"plate": -12, "dly": -18}},
            "guitar": {"gain": -8, "eq": [("hpf", 200), ("bell", 1200, -3, 1.2), ("bell", 3500, 2, 1.0)], "pan": -0.6,
                       "sends": {"room": -14}},
            "pad": {"gain": -13, "eq": [("hpf", 300), ("lpf", 9000)], "duck": {"by": "drums", "depth": 3},
                    "sends": {"hall": -8}},
            "violins": {"gain": -8, "eq": [("hpf", 200), ("bell", 3500, -1.5, 1.0)], "width": 0.6, "pan": -0.25,
                        "sends": {"hall": -6}},
            "violas": {"gain": -10, "eq": [("hpf", 160), ("bell", 400, -2, 1.0)], "pan": 0.3,
                       "sends": {"hall": -6}},
            "celli": {"gain": -10, "eq": [("hpf", 70), ("bell", 250, -2, 1.0)], "pan": 0.15,
                      "sends": {"hall": -8}},
            "sax": {"gain": -3.5, "eq": [("hpf", 150), ("bell", 600, -1.5, 1.0), ("bell", 2800, 1.5, 1.0), ("hshelf", 7000, 1.5)],
                    "comp": {"threshold": -24, "ratio": 3, "attack": 8, "release": 120},
                    "sends": {"plate": -9, "dly": -14}},
        },
        "fx": {
            "room": {"type": "reverb", "kind": "room", "decay": 0.6, "predelay": 4, "hpf": 200},
            "plate": {"type": "reverb", "kind": "plate", "decay": 1.8, "predelay": 30, "hpf": 250, "lpf": 8000},
            "hall": {"type": "reverb", "kind": "hall", "decay": 2.6, "predelay": 25, "hpf": 200, "lpf": 7500},
            "dly": {"type": "delay", "beats": 0.75, "feedback": 0.28, "hpf": 400, "lpf": 4000},
        },
        "master": {"eq": [("bell", 250, -1, 0.8), ("hshelf", 8000, 2)],
                   "glue": {"threshold": -16, "ratio": 2, "attack": 30, "release": 250},
                   "target_lufs": -14},
    }
    return s
