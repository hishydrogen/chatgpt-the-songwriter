"""8-bar groove sketch, three versions back to back (Eb major, 119 BPM, 8ths at 52:48).

Same harmony in every version, twice through:
    | Abmaj9 | Bb/Ab | Gm7 | Cm9  Fm7/Bb |
A  "Bounce"         left-hand tresillo octaves (1, 2&, 4) under a right hand rocking
                    between two voicings, top voice climbing Bb-C-D-Eb; 8th hats with
                    snare ghosts (the measured feel of the reference).
B  "Floppy pushes"  right hand only on the off-beats, held chords pushed across the bar;
                    two drummers on one backbeat (the Templeman + Knudsen "floppy feel"),
                    Rhodes pad underneath, bleating bass with 16th pickups.
C  "16th drive"     pulsing 16th-note right hand, busy 16th hats, driving 8th bass.
`python songs/westcoast-groove/song.py` prints the timestamp table.
"""
import random

from songwriter.instruments import surge
from songwriter.song import Song

BPM = 119
SWING8 = 0.52
BARS = 8

# instrument picks from the palette checkpoint: drums B (open room), bass A, piano C
# (Steinway + OB-8 double), Rhodes B (Suitcase tremolo), guitar A (single-coil clean)
PIANO = "piano.splendid"
OB_DOUBLE = surge("Brass/OB-8 Jump")   # None to drop the synth double
RHODES = "epiano.rhodes"
BASS = "bass.darkblack"
GUITAR = "guitar.green_twang"
KIT_CC = {71: 30, 105: 127, 109: 70, 111: 50}   # kick damping, overheads, room, vintage mic

# (start beat, length, (voicing 1, voicing 2), left-hand root)
CHORDS = [
    (0.0, 4.0, ([60, 63, 67], [63, 67, 70]), 44),   # Abmaj9
    (4.0, 4.0, ([62, 65, 70], [65, 70, 72]), 44),   # Bb/Ab
    (8.0, 4.0, ([62, 65, 70], [65, 70, 74]), 43),   # Gm7
    (12.0, 2.0, ([63, 67, 70], [67, 70, 74]), 48),  # Cm9
    (14.0, 2.0, ([63, 68, 72], [68, 72, 75]), 46),  # Fm7/Bb
]
# four-note shells for held chords (Rhodes pad, pushes)
SHELLS = {0.0: [55, 60, 63, 67], 4.0: [58, 62, 65, 70], 8.0: [58, 62, 65, 70], 12.0: [58, 62, 63, 67],
          14.0: [56, 60, 63, 68]}
GUITAR_V = {0.0: [67, 72, 75], 4.0: [65, 70, 74], 8.0: [65, 70, 74], 12.0: [67, 70, 74], 14.0: [68, 72, 75]}

VERSIONS = [("A: Bounce", "a"), ("B: Floppy pushes (double drums)", "b"), ("C: 16th drive", "c")]


def ms(rng, sd_ms, bias_ms=0.0):
    return rng.gauss(bias_ms, sd_ms) / 1000 * BPM / 60


def chord_at(beat):
    for c in CHORDS:
        if c[0] <= beat % 16 < c[0] + c[1]:
            return c
    return CHORDS[0]


class Sketch:
    def __init__(self):
        s = self.s = Song("Groove sketch (West Coast 1978)", bpm=BPM, key="Eb")
        self.kick, self.snare, self.snare2, self.hats, self.toms, self.cym, self.perc = (
            s.track(n, "drums.virtuosity") for n in ("kick", "snare", "snare 2", "hats", "toms", "cymbals", "perc"))
        for t in (self.kick, self.snare, self.snare2, self.hats, self.toms, self.cym, self.perc):
            for cc, v in KIT_CC.items():
                t.cc(cc, v, 0)
        self.piano = s.track("piano", PIANO)
        self.ob = s.track("OB-8 double", OB_DOUBLE) if OB_DOUBLE else None
        self.rhodes = s.track("rhodes", RHODES)
        self.bass = s.track("bass", BASS)
        self.gtr = s.track("guitar", GUITAR)

    # -- drums ------------------------------------------------------------------------------
    def drums(self, b0, style, seed):
        rng = random.Random(seed)
        self.cym.hit("crash", b0 + ms(rng, 4), 96)
        for bar in range(BARS):
            o = b0 + bar * 4
            last = bar == BARS - 1
            if style == "c":
                kicks = (0, 1.5, 2.0, 3.25) if bar % 2 == 0 else (0, 0.75, 2.0, 3.5)
            elif style == "b":
                kicks = (0, 2.0, 2.5) if bar % 2 == 0 else (0, 1.75, 2.0)
            else:
                kicks = ((0, 1.5, 2.0), (0, 2.0, 3.5), (0, 1.5, 2.0), (0, 2.0, 2.5))[bar % 4]
            for pos in kicks:
                if last and pos > 2.5:
                    continue
                self.kick.hit("kick", o + pos + ms(rng, 4), 112 if pos == 0 else rng.randint(88, 100))
            for pos in (1.0, 3.0):
                if last and pos == 3.0:
                    continue
                self.snare.hit("snare", o + pos + ms(rng, 4, 4), rng.randint(112, 120))
                if style == "b":   # second drummer, a hair behind, slightly softer: the floppy backbeat
                    self.snare2.hit("snare", o + pos + ms(rng, 5, 14), rng.randint(100, 112))
            ghosts = {"a": ((1.75, 3.75), (0.75, 2.5, 3.75)), "b": ((2.75,), (1.75, 3.25)),
                      "c": ((0.75, 1.75, 2.25, 3.75), (1.25, 1.75, 2.75, 3.5))}[style][bar % 2]
            for pos in ghosts:
                if not (last and pos >= 2.5):
                    self.snare.hit("snare", o + pos + ms(rng, 6), rng.randint(24, 40))
            step = 0.25 if style == "c" else 0.5
            for k in range(int(4 / step)):
                pos = k * step
                if last and pos >= 2.5:
                    break
                if style == "c":
                    vel = (rng.randint(96, 106), rng.randint(58, 66), rng.randint(80, 88), rng.randint(56, 64))[k % 4]
                else:
                    vel = rng.randint(94, 104) if k % 2 == 0 else rng.randint(70, 80)
                hit = "hh_half" if (bar % 4 == 3 and pos == 3.5) or (style == "b" and pos == 1.5 and bar % 2) else "hh_closed"
                self.hats.hit(hit, o + pos + ms(rng, 4, 2 if (k % 2) else 0), vel)
            if style == "b":   # congas fill the 16ths the hats leave open
                for pos, hit, v in ((0.75, "conga_mute", 70), (1.25, "conga_hi", 84), (1.5, "conga_hi", 74),
                                    (2.75, "conga_mute", 68), (3.0, "conga_lo", 86), (3.5, "conga_hi", 78)):
                    self.perc.hit(hit, o + pos + ms(rng, 6), v + rng.randint(-6, 6))
        # a different fill per version on beats 3-4 of the last bar
        o = b0 + (BARS - 1) * 4
        fill = {"a": [(2.5, "snare", 104), (3.0, "tom_high", 108), (3.25, "tom_high", 96), (3.5, "tom_low", 110), (3.75, "tom_low", 100)],
                "b": [(2.75, "snare", 90), (3.0, "snare", 112), (3.5, "tom_low", 112), (3.75, "kick", 104)],
                "c": [(2.5 + k * 0.125, ("snare", "snare", "tom_high", "tom_high", "tom_low", "tom_low", "snare", "snare")[k],
                       80 + k * 5) for k in range(8)]}[style]
        for pos, hit, v in fill:
            tr = self.toms if hit.startswith("tom") else self.kick if hit == "kick" else self.snare
            tr.hit(hit, o + pos + ms(rng, 5), v)

    # -- keys --------------------------------------------------------------------------------
    def keys_bounce(self, b0, seed):
        rng = random.Random(seed)
        for rep in range(BARS // 4):
            ob = b0 + rep * 16
            for i, (start, length, (v1, v2), root) in enumerate(CHORDS):
                nxt = CHORDS[(i + 1) % len(CHORDS)]
                lh = [root - 12, root]
                if length == 4.0:
                    rh = [(0.5, v1, 0.3, 84), (1.0, v2, 0.45, 100), (2.0, v1, 0.3, 82), (2.5, v2, 0.3, 90)]
                    lhp = [(0.0, 0.75, 100), (1.5, 0.45, 88), (3.0, 0.45, 92)]
                elif start % 4 == 0:
                    rh, lhp = [(0.5, v1, 0.3, 84), (1.0, v2, 0.45, 96)], [(0.0, 0.75, 100)]
                else:
                    rh, lhp = [(0.0, v1, 0.3, 90), (0.5, v2, 0.3, 88)], [(-0.5, 1.0, 96), (1.0, 0.45, 90)]
                for pos, v, d, vel in rh:
                    self.piano_hit(v, ob + start + pos + ms(rng, 5), d, vel)
                for pos, d, vel in lhp:
                    self.piano.notes_at(lh, ob + start + pos + ms(rng, 5), d, vel)
                if start + length in (4.0, 8.0, 12.0, 16.0) and not (rep == BARS // 4 - 1 and start + length == 16.0):
                    self.piano_hit(nxt[2][0], ob + start + length - 0.5 + ms(rng, 5, -3), 0.85, 104)
                self.piano.sustain(ob + start + 0.02, ob + start + 0.45)

    def keys_pushes(self, b0, seed):
        rng = random.Random(seed)
        for rep in range(BARS // 4):
            ob = b0 + rep * 16
            for i, (start, length, (v1, v2), root) in enumerate(CHORDS):
                shell = SHELLS[start]
                nxt = SHELLS[CHORDS[(i + 1) % len(CHORDS)][0]]
                if length == 4.0:
                    hits = [(0.5, shell, 1.0, 90), (1.5, shell, 0.45, 80), (2.5, shell, 0.9, 88)]
                    lh = [(0.0, 1.5, 98), (2.0, 1.0, 86)]
                else:
                    hits = [(0.5, shell, 1.0, 88)] if start % 4 == 0 else [(0.5, shell, 0.45, 84)]
                    lh = [(0.0, 1.5, 98)] if start % 4 == 0 else [(0.0, 1.0, 92)]
                for pos, v, d, vel in hits:
                    self.piano_hit(v, ob + start + pos + ms(rng, 6, 3), d, vel)
                for pos, d, vel in lh:
                    fifth = root + 7 if pos > 0 else root
                    self.piano.notes_at([fifth - 12, fifth], ob + start + pos + ms(rng, 5), d, vel)
                if start + length in (4.0, 8.0, 12.0, 16.0) and not (rep == BARS // 4 - 1 and start + length == 16.0):
                    self.piano_hit(nxt, ob + start + length - 0.5 + ms(rng, 6, -4), 1.2, 104)
                self.piano.sustain(ob + start + 0.02, ob + start + length - 0.1)
                # Rhodes pad: the chord held, an octave lower, soft
                self.rhodes.notes_at(shell, ob + start + ms(rng, 8), length - 0.1, 56)

    def keys_16ths(self, b0, seed):
        rng = random.Random(seed)
        pattern = (0.0, 0.5, 0.75, 1.0, 1.5, 1.75, 2.0, 2.5, 2.75, 3.0, 3.5, 3.75)
        for rep in range(BARS // 4):
            ob = b0 + rep * 16
            for i, (start, length, (v1, v2), root) in enumerate(CHORDS):
                for pos in pattern:
                    if pos >= length:
                        break
                    v = v2 if pos % 1.0 == 0.5 else v1
                    vel = 96 if pos % 1.0 == 0.5 else 70 if pos % 1.0 == 0.75 else 80
                    self.piano_hit(v, ob + start + pos + ms(rng, 4), 0.18, vel + rng.randint(-5, 5))
                for pos in (0.0, 2.0):
                    if pos < length:
                        self.piano.notes_at([root - 12, root], ob + start + pos + ms(rng, 4), 0.9, 98)
                for pos in (1.75, 3.75):
                    if pos < length:
                        self.piano.notes_at([root - 12, root], ob + start + pos + ms(rng, 4), 0.2, 84)

    def piano_hit(self, voicing, beat, dur, vel):
        self.piano.notes_at(voicing, beat, dur, vel)
        if self.ob is not None:
            self.ob.notes_at(voicing, beat, dur, max(1, vel - 10))

    # -- bass ----------------------------------------------------------------------------------
    def bass_line(self, b0, style, seed):
        rng = random.Random(seed)
        lines = {
            "a": [("Ab1", 0.0, 0.9), ("Ab1", 1.5, 0.4), ("Eb2", 2.0, 0.45), ("Ab2", 3.0, 0.35), ("Eb2", 3.5, 0.45),
                  ("Ab1", 4.0, 0.9), ("Ab1", 5.5, 0.4), ("Bb1", 6.0, 0.45), ("C2", 6.5, 0.45), ("Eb2", 7.0, 0.4), ("Ab1", 7.5, 0.45),
                  ("G1", 8.0, 0.9), ("G1", 9.5, 0.4), ("D2", 10.0, 0.45), ("Bb1", 11.0, 0.4), ("B1", 11.5, 0.45),
                  ("C2", 12.0, 0.9), ("G1", 13.5, 0.4), ("Bb1", 14.0, 0.9), ("Bb1", 15.0, 0.4), ("A1", 15.5, 0.45)],
            "b": [("Ab1", 0.0, 1.4), ("Ab2", 1.5, 0.2), ("Eb2", 1.75, 0.2), ("Ab1", 2.0, 0.9), ("C2", 3.0, 0.4), ("Eb2", 3.5, 0.4),
                  ("Ab1", 4.0, 1.4), ("Ab2", 5.5, 0.2), ("F2", 5.75, 0.2), ("D2", 6.0, 0.9), ("C2", 7.0, 0.4), ("Ab1", 7.5, 0.4),
                  ("G1", 8.0, 1.4), ("G2", 9.5, 0.2), ("F2", 9.75, 0.2), ("D2", 10.0, 0.9), ("Bb1", 11.0, 0.4), ("B1", 11.5, 0.4),
                  ("C2", 12.0, 1.4), ("Bb1", 13.75, 0.2), ("Bb1", 14.0, 0.9), ("F2", 15.0, 0.4), ("A1", 15.5, 0.4)],
            "c": [(n, 0.5 * k + 4 * bar, 0.4) for bar, (lo, hi) in enumerate((("Ab1", "Ab2"), ("Ab1", "Ab2"), ("G1", "G2"), ("C2", "C3")))
                  for k, n in enumerate((lo, lo, hi, lo, lo, hi, lo, hi))],
        }
        line = lines[style]
        if style == "c":   # last bar halves: Cm9 then Bb
            line = [(n if p < 14 else ("Bb1" if n in ("C2",) else "Bb2"), p, d) for n, p, d in line]
        for rep in range(BARS // 4):
            for n, p, d in line:
                vel = 104 if p % 4 == 0 else rng.randint(86, 98)
                self.bass.note(n, b0 + rep * 16 + p + ms(rng, 5, 2), d, vel)

    # -- guitar --------------------------------------------------------------------------------
    def guitar(self, b0, style, seed):
        rng = random.Random(seed)
        for bar in range(BARS):
            o = b0 + bar * 4
            if style == "c":   # palm-muted 16th scratches, accents on the 8th off-beats
                for k in range(16):
                    pos = k * 0.25
                    st = chord_at(bar * 4 + pos)[0]
                    vel = 92 if k % 4 == 2 else 52 if k % 2 else 66
                    self.gtr.notes_at(GUITAR_V[st], o + pos + ms(rng, 4), 0.07, vel + rng.randint(-6, 6), strum=0.006)
                continue
            pattern = ((1.0, 0.15, 98), (1.75, 0.1, 64), (2.5, 0.2, 86), (3.0, 0.15, 94), (3.75, 0.1, 66)) if style == "a" \
                else ((1.5, 0.3, 90), (3.5, 0.25, 84))
            for pos, d, v in pattern:
                st = chord_at(bar * 4 + pos)[0]
                self.gtr.notes_at(GUITAR_V[st], o + pos + ms(rng, 5), d, v, strum=0.012)


def compose() -> Song:
    k = Sketch()
    s = k.s
    for i, (label, style) in enumerate(VERSIONS):
        b0 = i * BARS * 4
        s.marker(b0, label)
        k.drums(b0, style, 100 + i)
        {"a": k.keys_bounce, "b": k.keys_pushes, "c": k.keys_16ths}[style](b0, 200 + i)
        k.bass_line(b0, style, 300 + i)
        k.guitar(b0, style, 400 + i)
    for t in s.tracks.values():
        t.swing(SWING8, grid=0.5)
    s.length_beats = len(VERSIONS) * BARS * 4 + 4
    s.mix = {
        "tracks": {
            "kick": {"gain": -3, "eq": [("hpf", 40), ("bell", 70, 1, 1.2), ("bell", 380, -4, 1.4), ("bell", 3500, 2, 1.0)],
                     "comp": {"threshold": -18, "ratio": 3, "attack": 15, "release": 90}, "tape": {"drive_db": 5},
                     "sends": {"room": -8}},
            "snare": {"gain": -2, "eq": [("hpf", 90), ("bell", 220, 2, 1.0), ("bell", 900, -2, 2.0), ("hshelf", 6000, -2)],
                      "comp": {"threshold": -20, "ratio": 3, "attack": 10, "release": 120}, "tape": {"drive_db": 5},
                      "sends": {"plate": -14, "room": -8}},
            "snare 2": {"gain": -9, "eq": [("hpf", 120), ("bell", 220, 2, 1.0), ("hshelf", 6000, -3)], "pan": -0.15,
                        "tape": {"drive_db": 5}, "sends": {"room": -14}},
            "hats": {"gain": -10, "eq": [("hpf", 300), ("hshelf", 9000, -2)], "pan": 0.35, "tape": {"drive_db": 3},
                     "sends": {"room": -8}},
            "toms": {"gain": -4, "eq": [("hpf", 60), ("bell", 600, -3, 1.0)], "sends": {"room": -8}},
            "cymbals": {"gain": -12, "eq": [("hpf", 400)], "width": 1.1},
            "perc": {"gain": -14, "eq": [("hpf", 150)], "pan": -0.4, "sends": {"room": -12}},
            "piano": {"gain": -1.5, "eq": [("hpf", 70), ("bell", 300, -2, 1.0)], "width": 0.7, "mono_below": 150,
                      "sends": {"plate": -16}},
            "OB-8 double": {"gain": -12, "eq": [("hpf", 200), ("lpf", 4000)], "chorus": {"rate_hz": 0.5, "depth_ms": 2.0, "mix": 0.35}},
            "rhodes": {"gain": -12, "eq": [("hpf", 120), ("bell", 250, -2, 1.0)], "tremolo": {"rate_hz": 4.2, "depth": 0.3},
                       "sends": {"plate": -16}},
            "bass": {"gain": -4.5, "eq": [("hpf", 40), ("bell", 700, 1.5, 1.0)],
                     "comp": {"threshold": -20, "ratio": 3, "attack": 20, "release": 120}, "tape": {"drive_db": 4}, "mono": True},
            "guitar": {"gain": -8, "eq": [("hpf", 150), ("bell", 400, -2, 1.0)],
                       "comp": {"threshold": -24, "ratio": 4, "attack": 5, "release": 80},
                       "chorus": {"rate_hz": 0.8, "depth_ms": 2.5, "mix": 0.4}, "pan": -0.35, "sends": {"plate": -14}},
        },
        "fx": {
            "plate": {"type": "reverb", "kind": "plate", "decay": 1.8, "predelay": 25, "hpf": 250, "lpf": 8000},
            "room": {"type": "reverb", "kind": "room", "decay": 0.6, "predelay": 5, "hpf": 200, "lpf": 7000},
        },
        # 1978 balance (reference: bass band -6.8 dB and sub -16.5 dB under the mids)
        "master": {"eq": [("lshelf", 120, -6, 0.7), ("hpf", 28)],
                   "glue": {"threshold": -18, "ratio": 2, "attack": 30, "release": 250}, "target_lufs": -14},
    }
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
