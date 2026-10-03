"""Checkpoint 2: three written eight-bar grooves, alone and with the same scat.

User's locked palette: Milk, Splendid Steinway, upright bass, DRSKit.
The first checkpoint remains the source of the original harmony, scat and
performance conventions. Every instrumental take is repeated exactly under the
voice, so this comparison changes the arrangement rather than the singer.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

from songwriter.song import note_number as N

_spec = importlib.util.spec_from_file_location(
    "scat_palette", Path(__file__).resolve().parents[1] / "scat-jazz-palette/song.py")
palette = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(palette)
BPM, SWING = palette.BPM, palette.SWING
HARMONY, HOOK = palette.HARMONY, palette.HOOK
chord_at, performed, velocity = palette.chord_at, palette.performed, palette.velocity
VERSIONS = [("A", "Airborne swing"), ("B", "Syncopated pocket"), ("C", "Brass conversation")]
VOICE_LABEL = "scat - Milk"
SELECTED = {"voice": "voice.milk", "keys": "piano.splendid",
            "bass": "bass.upright_pizz", "drums": "drums.drskit"}

# Deliberate top-line cells: same rhythmic identity, following each new chord.
RIFF_PITCHES = [
    ["G4", "A4", "C5"], ["F#4", "A4", "C5"],
    ["A4", "Bb4", "D5"], ["G4", "A4", "D5"],
    ["E4", "G4", "C5"], ["A4", "Bb4", "D5"],
    ["G4", "A4", "C5"], ["F4", "G4", "A4"],
]
WALKING = [
    ["F1", "A1", "C2", "E2"], ["D2", "F#2", "A1", "F#1"],
    ["G1", "Bb1", "D2", "Db2"], ["C2", "E2", "G1", "Ab1"],
    ["A1", "C2", "D2", "F#1"], ["G1", "Bb1", "C2", "E2"],
    ["F1", "A1", "Bb1", "Db2"], ["G1", "D2", "C2", "E2"],
]


class Sketch(palette.Palette):
    def __init__(self):
        self.s = palette.PaletteSong("Floating scat - groove sketches", bpm=BPM, key="F")
        self.beat, self.sections, self.mix = 0, [], {}
        self.piano = self.track("Steinway comp", SELECTED["keys"], 0, -8,
                                eq=[("hpf", 135), ("bell", 340, -2.5, .8),
                                    ("hshelf", 5500, 1.5, .7)],
                                width=.55, mono_below=150, sends={"room": -17})
        self.riff = self.track("Steinway answering riff", SELECTED["keys"], 8, -13,
                               eq=[("hpf", 230), ("bell", 750, -1.5, .9)],
                               width=.50, pan=-.08, sends={"room": -17})
        self.bass = self.track("upright bass", SELECTED["bass"], 1, -9,
                               eq=[("hpf", 35), ("bell", 220, -2, .8)], mono=True,
                               comp={"threshold": -19, "ratio": 2,
                                     "attack": 24, "release": 130})
        self.guitar = self.track("muted guitar", "guitar.green_stac", 2, -18,
                                 eq=[("hpf", 220), ("lpf", 7000)], pan=-.32,
                                 sends={"room": -19})
        self.horns = [
            self.track("trombone punctuation", "brass.trombone_stac", 3, -18, pan=-.25),
            self.track("French horn inner voice", "brass.horn_stac", 4, -20, pan=.04),
            self.track("muted trumpet answers", "brass.trumpet_harmon", 5, -19, pan=.28),
        ]
        for t in self.horns:
            self.mix[t.name].update(eq=[("hpf", 185), ("bell", 700, -1.5, .8)],
                                    sends={"room": -14})
        self.sax = self.track("tenor replies", "sax.tenor", 6, -17,
                              eq=[("hpf", 185), ("bell", 650, -2, .8)], pan=.16,
                              sends={"plate": -18})
        dc = {
            "kick": (-12, 0, [("hpf", 35), ("bell", 70, -2, 1)]),
            "snare": (-12, -.06, [("hpf", 155)]),
            "ride": (-13, .24, [("hpf", 500), ("hshelf", 8000, -1, .7)]),
            "hats": (-17, -.22, [("hpf", 650)]),
            "toms": (-16, -.14, [("hpf", 90)]),
            "cymbals": (-22, .12, [("hpf", 550)]),
        }
        self.kit = {part: self.track("DRSKit " + part, SELECTED["drums"], 9, gain,
                                    pan=pan, eq=eq, width=.5 if part in ("ride", "cymbals") else 1,
                                    sends={"room": -18 if part != "kick" else -24})
                    for part, (gain, pan, eq) in dc.items()}
        # The main drum kit is always the chosen DRSKit. Virtuosity supplies only
        # the separate hand percussion, which DRSKit does not contain.
        self.shaker = self.track("shaker", "drums.virtuosity", 9, -24,
                                 eq=[("hpf", 700)], pan=-.26, sends={"room": -22})
        self.bongo = self.track("bongo conversation", "drums.virtuosity", 9, -23,
                                eq=[("hpf", 300)], pan=.30, sends={"room": -20})

    def hit(self, part, name, start, beat, vel):
        role = "hat" if part == "hats" else part
        self.kit[part].hit(name, start + performed(beat, role), velocity(vel, beat), .12)

    def drum_groove(self, start, style):
        for bar in range(8):
            b = bar * 4
            kicks = {
                "A": [(0, 55), (1, 35), (2, 59), (3, 38)],
                "B": [(0, 72), (1.5, 62), (2.5, 67), (3.5, 44)],
                "C": [(0, 69), (1, 42), (2, 73), (2.5, 48), (3.5, 63)],
            }[style]
            if style == "B" and bar % 2 == 0:
                kicks = kicks[:3]
            for pos, v in kicks:
                self.hit("kick", "kick", start, b + pos, v)
            for pos in (1, 3):
                self.hit("snare", "snare", start, b + pos,
                         (74 if style == "A" else 83 if style == "B" else 91) + (4 if pos == 3 else 0))
            ghosts = {"A": (.5, 2.5) if bar % 2 else (2.75,),
                      "B": (.75, 2.25, 3.75) if bar % 2 else (.75, 2.75),
                      "C": (.75, 1.75, 2.75)}[style]
            for pos in ghosts:
                if style == "C" and bar in (3, 7) and pos == 2.75:
                    continue  # the written fill replaces this ghost stroke
                self.hit("snare", "snare", start, b + pos, 25 if style != "C" else 30)
            if style == "B":
                for k in range(8):
                    opened = bar in (1, 5) and k == 7
                    self.hit("hats", "hh_half" if opened else "hh_closed", start,
                             b + k * .5, 60 if opened else 65 if k % 2 else 78)
            else:
                ride = ((0, 73), (1, 52), (1.5, 63), (2, 77), (3, 54), (3.5, 69))
                for pos, v in ride:
                    name = "ride_bell" if style == "C" and bar in (2, 5) and pos in (0, 2) else "ride"
                    self.hit("ride", name, start, b + pos, v + (7 if style == "C" else 0))
                for pos in (1, 3):
                    self.hit("hats", "hh_pedal", start, b + pos, 57)
            if style == "C" and bar in (0, 4):
                self.hit("cymbals", "crash_tip", start, b, 68 if bar == 0 else 78)
            if bar in (3, 7):
                fills = {
                    "A": [(3.12, "tom_high", 57), (3.38, "tom_mid", 64), (3.76, "tom_low", 72)],
                    "B": [(2.75, "snare", 40), (3.12, "tom_high", 67),
                          (3.50, "tom_mid", 72), (3.76, "tom_low", 81)],
                    "C": [(2.75, "snare", 55), (3.00, "tom_high", 71),
                          (3.25, "tom_high", 64), (3.50, "tom_mid", 79), (3.76, "tom_low", 87)],
                }[style]
                for pos, name, v in fills:
                    self.hit("snare" if name == "snare" else "toms", name, start,
                             b + pos, v + (4 if bar == 7 else 0))

    def bass_groove(self, start, style):
        for bar, pitches in enumerate(WALKING):
            b = bar * 4
            if style == "B":
                # Charleston/tresillo accents with a short connection into the
                # next root; the second-half chords still get their own roots.
                events = [(0, pitches[0], .95, 92), (1.5, pitches[1], .33, 76),
                          (2, pitches[2], .65, 87), (3.25, pitches[3], .28, 72)]
            else:
                events = [(j, pitch, (.82, .67, .84, .64)[j], (94, 80, 90, 78)[j])
                          for j, pitch in enumerate(pitches)]
                if style == "C" and bar in (1, 3, 5):
                    events[-1] = (3, pitches[-1], .30, 77)
                    events.append((3.5, pitches[-1], .27, 64))
            for pos, pitch, dur, vel in events:
                if bar == 7 and pos >= 3:
                    dur = min(dur, .31)
                self.bass.note(pitch, start + performed(b + pos, "bass"), dur,
                               velocity(vel, b + pos))
        self.bass.note("F1", start + performed(31.5, "bass"), .63, 91)
        self.bass.cc(11, 108, start)

    def piano_groove(self, start, style):
        for bar in range(8):
            b = bar * 4
            patterns = {
                "A": [(0, .28, 70), (1.5, .22, 63), (2.5, .26, 72)],
                "B": [(0, .23, 73), (.75, .16, 52), (1.5, .25, 78),
                      (2.5, .25, 74), (3.25, .16, 57)],
                "C": [(.5, .23, 75), (1.5, .20, 66), (2, .27, 79), (3.5, .27, 76)],
            }[style]
            # Spell out split chords and the borrowed minor-IV colour rather
            # than cycling a bar-long chord through every accompaniment hit.
            if bar >= 4:
                patterns = [(0, .27, 72), (1.5, .21, 63), (2, .28, 75), (3.5, .22, 71)]
                if style == "B":
                    patterns += [(.75, .14, 51), (2.75, .14, 55)]
            for pos, dur, v in patterns:
                beat = b + pos
                pitches = [N(p) for p in chord_at(beat)[3]]
                if style == "B":
                    pitches = pitches[:3]  # thinner, more percussive attack
                onset = start + performed(beat, "piano")
                for j, pitch in enumerate(pitches):
                    roll = (0, .012, .020, .016)[j]
                    self.piano.note(pitch, onset + roll, dur - roll,
                                    velocity(v + (3 if j == len(pitches) - 1 else -2), beat, j))
                self.piano.sustain(onset + .025, onset + min(.28, dur + .035))
            # Three short notes form the band's recurring face. Most cells sit
            # in the vocal's end-of-line gap, with only a low-key bar-3 reply.
            if bar in (0, 4):
                cell = list(zip((3.38, 3.61, 3.83), RIFF_PITCHES[bar]))
            elif style == "B" and bar in (2, 6):
                cell = [(1.76, RIFF_PITCHES[bar][0])]
            elif style == "C" and bar in (1, 5):
                cell = [(2.76, RIFF_PITCHES[bar][0])]
            else:
                cell = []
            for pos, pitch in cell:
                # Bar 5 is on D7b9 here; keep its answering line in that chord.
                if bar == 4:
                    pitch = {3.38: "F#4", 3.61: "A4", 3.83: "C5"}[pos]
                self.riff.note(pitch, start + performed(b + pos, "piano"), .13,
                               velocity(78 if style != "C" else 86, b + pos))
        self.piano.cc(64, 0, start + 31.99)

    def colour_groove(self, start, style):
        for bar in range(8):
            b = bar * 4
            guitar_pattern = (1, 3) if style == "A" else (.5, 1.5, 2.5, 3.5) if style == "B" else (1, 2.5, 3)
            for pos in guitar_pattern:
                beat = b + pos
                guide = [N(p) for p in chord_at(beat)[3][:2]]
                self.guitar.notes_at(guide, start + performed(beat, "guitar"),
                                     .13, velocity(58 if style == "A" else 66, beat), strum=.015)
            if style == "B" or bar % 2:
                for k in range(8):
                    beat = b + k * .5
                    self.shaker.hit("shaker", start + performed(beat, "shaker"),
                                    velocity((52 if style == "B" else 42) + (5 if k % 2 == 0 else 0), beat), .1)
            if style == "B":
                for pos, name, v in ((.75, "bongo_lo", 57), (1.75, "bongo_hi", 47),
                                     (2.75, "bongo_lo", 51), (3.5, "bongo_hi", 61)):
                    beat = b + pos
                    self.bongo.hit(name, start + performed(beat, "bongo"), velocity(v, beat), .12)
            elif bar in (3, 7):
                for pos, name in ((3.12, "bongo_lo"), (3.74, "bongo_hi")):
                    beat = b + pos
                    self.bongo.hit(name, start + performed(beat, "bongo"), velocity(47, beat), .1)
        if style == "A":
            horn_events = [(16.06, .18), (25.73, .18), (31.53, .52)]
        elif style == "B":
            horn_events = [(3.73, .17), (16.06, .18), (23.79, .15), (31.53, .52)]
        else:
            horn_events = [(2.77, .17), (6.78, .16), (10.76, .18), (16.06, .18),
                           (18.76, .16), (22.76, .18), (25.73, .18), (31.53, .52)]
        for beat, dur in horn_events:
            v = [N(p) for p in chord_at(beat)[3]]
            pitches = [v[0] - 12, v[1] - 12, v[-1] - 12]
            for j, (t, pitch) in enumerate(zip(self.horns, pitches)):
                onset = start + performed(beat, "horn", j) + .006 * j
                t.note(pitch, onset, dur, velocity(85 if style == "C" else 75, beat, j))
                t.cc_ramp(11, onset, onset + min(.16, dur), 79, 108, step=.05)
        # Tenor never competes with the pianist's 3-note answers. Its legato
        # response fits between the end of bar 4 and the next scat pickup.
        sax_line = [(16.05, "G4", .15), (16.26, "E4", .20)]
        if style == "C":
            sax_line = [(16.05, "C5", .15), (16.26, "A4", .20)]
        self.sax.cc(64, 127, start + 16.02)
        self.sax.cc(80, 10, start + 16.02)
        self.sax.bend(-650, start + 16.02)
        self.sax.bend(0, start + 16.11)
        for beat, pitch, dur in sax_line:
            self.sax.note(pitch, start + performed(beat, "sax"), dur, velocity(85, beat))
        self.sax.cc_ramp(11, start + 16.02, start + 16.49, 77, 105, step=.09)
        self.sax.cc(64, 0, start + 16.50)

    def arrange(self, start, style):
        self.drum_groove(start, style)
        self.bass_groove(start, style)
        self.piano_groove(start, style)
        self.colour_groove(start, style)


def compose():
    a = Sketch()
    for style, title in VERSIONS:
        for role in ("band", "vocal"):
            b = a.section(f"{style} - {title} - {role}", 8, role)
            a.sections[-1]["version"] = style
            a.arrange(b, style)
            if role == "vocal":
                a.sing(VOICE_LABEL, SELECTED["voice"], b)
        a.s.marker(a.beat, f"{style} - release")
        a.beat += 4  # one silent bar lets the final vocal and ambience finish
    a.s.length_beats = a.beat
    # A scat solo should float inside the ensemble; keep the singer 4-6 dB
    # above the loudest individual band member in all three vocal passages.
    a.mix[VOICE_LABEL]["gain"] = -3.5
    a.s.mix = {"tracks": a.mix, "fx": {
        "room": {"type": "reverb", "kind": "room", "decay": .65, "predelay": 8,
                 "hpf": 300, "lpf": 7800},
        "plate": {"type": "reverb", "kind": "plate", "decay": .90, "predelay": 22,
                  "hpf": 350, "lpf": 8500},
        "slap": {"type": "delay", "beats": .22, "feedback": .12, "hpf": 650, "lpf": 5500}},
        "master": {"target_lufs": -14, "ceiling": -1, "mono_below": 100,
                   "glue": {"threshold": -16, "ratio": 1.5, "attack": 30, "release": 170}}}
    a.s.groove_sections = a.sections
    return a.s


if __name__ == "__main__":
    s = compose()
    for sec in s.groove_sections:
        print(f"{s.seconds(sec['beat']):6.2f}-{s.seconds(sec['beat'] + 32):6.2f}  {sec['label']}")
    print(len(s.tracks), "tracks;", sum(len(t.notes) for t in s.tracks.values()), "notes")
