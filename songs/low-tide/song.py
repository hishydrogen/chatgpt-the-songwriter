"""Low Tide: an original 74-bar instrumental, all groove A.

BBBB palette: vintage-mic drums, Darkblack finger bass, Wurlitzer, Emily guitar.
86 BPM throughout. A's kick pattern, late snare and bass rhythm remain the basis
of every section. Development comes from melody, harmony, replies and dynamics.
Checkpoint 4 retains the approved arrangement and full-stop ending.
"""
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from songwriter.song import Song, note_number  # noqa: E402
from songwriter.instruments import get_instrument  # noqa: E402

BPM = 86
GROOVE = "A"
CORE = ["Em9", "Em9", "Am9", "B7", "Em9", "G6", "Am9", "B7"]
REFRAIN = ["Em9", "G6", "Am9", "B7", "Cmaj7", "Am9", "B7", "Em9"]
FORM = [  # name, role, per-bar harmony, performance intensity
    ("intro", "intro", CORE[:4], .88),
    ("theme 1", "theme", CORE + CORE[:4], .96),
    ("refrain 1", "refrain", REFRAIN, 1.03),
    ("turnaround", "turn", ["Em9", "B7"], .94),
    ("theme 2", "theme2", CORE + CORE[:4], .99),
    ("refrain 2", "refrain", REFRAIN, 1.06),
    ("Wurlitzer bridge", "bridge", ["Am9", "Am9", "G6", "G6", "Cmaj7", "Am9", "F#m7b5", "B7"], .92),
    ("guitar solo", "solo", CORE, 1.02),
    ("final refrain", "final", REFRAIN, 1.09),
    ("outro", "outro", ["Em9", "Am9", "B7", "Em9"], .94),
]
CHORD_LINE = [ch for _, _, chords, _ in FORM for ch in chords]
assert len(CHORD_LINE) == 74
CH = {
    # voiced keyboard chord, bass notes in A rhythm, safe melody pitch classes,
    # playable upper three-string guitar shape
    "Em9": ([55, 59, 62, 66], ["E2", "B1", "D2", "G2", "E2"], {2, 4, 6, 7, 11}, [55, 59, 64]),
    "Am9": ([55, 60, 64, 69], ["A1", "E2", "G2", "C2", "A1"], {0, 4, 7, 9, 11}, [60, 64, 69]),
    "B7": ([57, 63, 66, 71], ["B1", "F#2", "A2", "D#2", "B1"], {3, 6, 9, 11}, [63, 66, 69]),
    "G6": ([55, 59, 62, 64], ["G1", "D2", "E2", "B2", "G1"], {2, 4, 7, 11}, [59, 62, 67]),
    "Cmaj7": ([55, 59, 64, 67], ["C2", "G1", "B1", "E2", "C2"], {0, 4, 7, 11}, [64, 67, 71]),
    "F#m7b5": ([57, 60, 64, 66], ["F#1", "C2", "E2", "A2", "F#1"], {0, 4, 6, 9}, [60, 64, 69]),
}
KIT_CC = {71: 112, 76: 58, 81: 57, 86: 58, 101: 127, 102: 18, 103: 127,
          104: 15, 105: 42, 106: 24, 107: 0, 109: 8, 111: 96}
# Each note is (beat within bar, pitch, duration); the accepted A riff is retained.
MAIN = [
    [(.5, "B3", .30), (1.5, "D4", .28), (2.25, "E4", .50), (3.25, "G4", .30)],
    [(.25, "F#4", .25), (.75, "E4", .70), (2.25, "B3", .25), (3, "D4", .28), (3.5, "E4", .34)],
    [(.75, "G4", .40), (1.5, "A4", .35), (2.25, "C5", .35), (3, "B4", .40)],
    [(.5, "A4", .25), (1.25, "F#4", .40), (2, "D#4", .45), (3, "B3", .65)],
    [(.5, "B3", .30), (1.5, "D4", .28), (2.25, "E4", .50), (3.25, "F#4", .30)],
    [(.25, "G4", .60), (1.25, "E4", .25), (2.25, "D4", .50), (3.25, "B3", .30)],
    [(.5, "E4", .30), (1.5, "G4", .30), (2.25, "B4", .35), (3, "C5", .40)],
    [(.25, "D#4", .30), (.75, "F#4", .40), (1.75, "A4", .30), (2.5, "F#4", .30), (3.25, "B3", .55)],
]
# A three-note rhythmic motif becomes a higher, singable refrain over new harmony.
HOOK = [
    [(.5, "E4", .42), (1.5, "G4", .45), (2.25, "B4", 1.30)],
    [(.25, "D5", .45), (1, "B4", .50), (2.25, "G4", 1.20)],
    [(.5, "C5", .45), (1.5, "B4", .40), (2.25, "A4", 1.20)],
    [(.5, "F#4", .42), (1.5, "D#4", .45), (2.25, "B3", 1.20)],
    [(.5, "E4", .42), (1.5, "G4", .45), (2.25, "B4", 1.30)],
    [(.25, "C5", .45), (1, "B4", .50), (2.25, "A4", 1.20)],
    [(.5, "A4", .42), (1.5, "F#4", .45), (2.25, "B4", .65), (3.25, "D#5", .30)],
    [(.125, "E5", 1.15), (1.5, "D5", .30), (2.25, "B4", .40), (3.25, "E4", .50)],
]
SOLO = [
    [(.25, "E4", .45), (1, "G4", .25), (1.5, "A4", .14), (1.75, "B4", .55), (2.75, "D5", .35), (3.5, "B4", .40)],
    [(.25, "G4", .45), (1, "E4", .35), (1.75, "F#4", .35), (2.5, "D4", .35), (3.25, "B3", .55)],
    [(.25, "A4", .35), (.75, "C5", .35), (1.25, "B4", .18), (1.5, "A4", .50), (2.25, "G4", .50), (3.25, "E4", .50)],
    [(.25, "F#4", .45), (1, "A4", .25), (1.5, "B4", .50), (2.25, "D#5", .35), (3.25, "B4", .55)],
    [(.25, "E5", .80), (1.25, "D5", .35), (2, "B4", .50), (3, "G4", .65)],
    [(.5, "D5", .60), (1.5, "B4", .40), (2.25, "G4", .40), (3, "E4", .65)],
    [(.25, "C5", .60), (1.25, "A4", .40), (2, "B4", .30), (2.5, "G4", .30), (3.25, "E4", .50)],
    [(.25, "A4", .35), (1, "F#4", .35), (1.75, "D#4", .35), (2.5, "B3", .90)],
]
ANSWER = {"Em9": ["G4", "B4", "F#4"], "Am9": ["E4", "G4", "B4"],
          "B7": ["F#4", "D#4", "B3"], "G6": ["B4", "G4", "E4"],
          "Cmaj7": ["E4", "G4", "B4"], "F#m7b5": ["A4", "C5", "E5"]}


def time(rng, beat, bias=0, spread=4):
    return max(0, beat + rng.gauss(bias, spread) * BPM / 60000)


def velocity(rng, value, intensity):
    return round(value * intensity) + rng.randint(-3, 3)


class Arrangement:
    def __init__(self):
        self.song = Song("Low Tide", bpm=BPM, key="Em")
        self.kit = {v: self.song.track(v, "drums.virtuosity") for v in ("kick", "snare", "hats", "toms")}
        for track in self.kit.values():
            for cc, value in KIT_CC.items():
                track.cc(cc, value, 0)
        self.bass = self.song.track("bass", "bass.darkblack")
        self.keys = self.song.track("Wurlitzer chords", "epiano.wurlitzer")
        self.answer = self.song.track("Wurlitzer replies", "epiano.wurlitzer")
        self.lead = self.song.track("guitar lead", "guitar.emily_di")
        self.rhythm = self.song.track("guitar chords", "guitar.emily_di")
        self.bass.cc(21, 0, 0).cc(113, 0, 0).cc(114, 0, 0)
        for track in (self.lead, self.rhythm):
            track.cc(70, 8, 0).bend(0, 0)

    def drum_bar(self, bar, local, role, intensity, last):
        rng = random.Random(19690926 + bar * 19)
        b = bar * 4
        closing = role == "outro" and last
        kicks = (0, 2.5) if local % 2 == 0 else (0, 1.75, 2.5)
        if closing:
            kicks = (0,)
        for p in kicks:
            self.kit["kick"].hit("kick", time(rng, b + p, 0, 3), velocity(rng, 94 if p < 1 else 84, intensity))
        for p in (1, 3):
            if (closing and p == 3) or (last and p == 3 and not closing):
                continue
            self.kit["snare"].hit("snare", time(rng, b + p, 12, 4),
                                  velocity(rng, 62 if closing else 91, intensity))
        if not last:
            self.kit["snare"].hit("snare", time(rng, b + 2.75, 6, 5), velocity(rng, 35, intensity))
        for p, v in ((0, 51), (.5, 34), (1, 47), (2, 51), (2.5, 33), (3, 47)):
            if (closing and p > 1) or (last and p >= 3):
                continue
            self.kit["hats"].hit("hh_closed", time(rng, b + p, 3, 3), velocity(rng, v, intensity))
        if not closing and (local % 4 == 3 or last):
            # Keep the A fill's two-hit rhythm; vary its orchestration and touch.
            order = ("tom_high", "tom_low") if (bar // 4) % 2 == 0 else ("tom_low", "tom_high")
            for p, hit, v in ((3.25, order[0], 68), (3.625, order[1], 74)):
                self.kit["toms"].hit(hit, time(rng, b + p, 6, 4), velocity(rng, v, intensity), dur=.16)

    def bass_bar(self, bar, chord, intensity, closing):
        rng = random.Random(19690820 + bar * 23)
        b = bar * 4
        notes = CH[chord][1]
        if closing:
            self.bass.note(notes[0], time(rng, b + .125, 3, 5), 2.80, velocity(rng, 87, intensity))
            return
        for i, p in enumerate((.125, 1.25, 2.25, 3.25, 3.75)):
            self.bass.note(notes[i], time(rng, b + p, 3, 5), [.46, .28, .35, .22, .16][i],
                           velocity(rng, [93, 82, 88, 80, 82][i], intensity))

    def keys_bar(self, bar, local, role, chord, intensity, closing):
        rng = random.Random(19690730 + bar * 29)
        b = bar * 4
        if role == "intro" and local < 2:
            return
        rhythm = [(.5, .65, 62), (2.5, .45, 55)] if not closing else [(.35, 3.30, 58)]
        for p, dur, v in rhythm:
            beat = time(rng, b + p, 5, 5)
            self.keys.notes_at(CH[chord][0], beat, dur, velocity(rng, v, intensity), strum=.012)
            self.keys.sustain(beat, beat + dur - .03)
        responding = (role in ("theme", "theme2") and local % 8 in (4, 6)) or (role == "bridge" and local < 6)
        if responding:
            for i, pitch in enumerate(ANSWER[chord]):
                self.answer.note(pitch, time(rng, b + (1.5, 2.25, 3.25)[i], 5, 5),
                                 (.35, .30, .35)[i], velocity(rng, 68 if i < 2 else 62, intensity))

    def guitar_bar(self, bar, local, role, chord, intensity, closing):
        rng = random.Random(19690721 + bar * 31)
        b = bar * 4
        if role in ("theme", "theme2"):
            if local % 8 in (4, 6):
                return
            phrase = MAIN[local % 8]
        elif role in ("refrain", "final"):
            phrase = HOOK[local]
        elif role == "solo":
            phrase = SOLO[local]
        elif role == "bridge":
            if local < 6:
                return
            phrase = [(.5, "E4", .35), (1.5, "F#4", .50), (2.5, "A4", .30), (3.25, "C5", .35)] if local == 6 else MAIN[7]
        elif role == "intro":
            if local < 3:
                return
            phrase = [(.75, "F#4", .45), (2.25, "D#4", .30), (3, "B3", .55)]
        elif role == "turn":
            phrase = MAIN[0] if local == 0 else MAIN[3]
        else:  # outro: echoes become the final, held tonic
            phrase = [(.5, ANSWER[chord][0], .40), (2.25, ANSWER[chord][2], .70)]
            if closing:
                phrase = [(.35, "E4", 3.20)]
        for i, (p, pitch, dur) in enumerate(phrase):
            assert note_number(pitch) % 12 in CH[chord][2] or (role == "solo" and dur <= .18), (bar, chord, pitch)
            beat = time(rng, b + p, 5, 5)
            base = 88 if role in ("refrain", "final", "solo") else 83
            if role == "theme2" and local >= 8 and i == 2:
                dur = min(dur + .08, 3.85 - p)
            self.lead.note(pitch, beat, dur, velocity(rng, base + (4 if i == 2 else 0), intensity))
            if dur >= .6:
                self.lead.vibrato(beat + .18, beat + dur - .04, rate_hz=4.8,
                                  cents=12 if role == "solo" else 8)
        if role in ("refrain", "final"):
            for p in (.5, 2.5):
                self.rhythm.notes_at(CH[chord][3], time(rng, b + p, 5, 5), .23,
                                     velocity(rng, 55, intensity), strum=.018)


def mixing():
    amp = [{"type": "amp", "PreGain": -8, "Distortion": 4, "Drive": .08,
            "model": 0, "t_model": 8, "c_model": 9, "Presence": 2}]
    tracks = {
        "kick": {"gain": -4, "eq": [("hpf", 33), ("bell", 78, -.5, 1), ("bell", 280, -3, 1), ("lpf", 4000, 1)]},
        "snare": {"gain": -6.3, "eq": [("hpf", 105), ("bell", 230, 1, 1), ("bell", 750, -2, 1.1), ("lpf", 6500, 1)],
                  "sends": {"tight_room": -25}},
        "hats": {"gain": -17, "eq": [("hpf", 450), ("lpf", 7600, 1)], "pan": -.13},
        "toms": {"gain": -8, "eq": [("hpf", 60), ("bell", 420, -2, 1), ("lpf", 5300, 1)],
                 "pan": -.10, "sends": {"tight_room": -25}},
        "bass": {"gain": -2.5, "eq": [("hpf", 38), ("bell", 110, .7, .8), ("bell", 330, -2.5, 1), ("lpf", 2400, 1)],
                 "comp": {"threshold": -23, "ratio": 2.4, "attack": 25, "release": 155},
                 "tape": {"drive_db": 1, "bump_db": .1, "mix": .25}, "mono": True},
        "Wurlitzer chords": {"gain": -8, "eq": [("hpf", 145), ("bell", 330, -3.5, 1.1), ("lpf", 6000, 1)],
                             "tape": {"drive_db": .6, "bump_db": 0, "mix": .2}, "mono": True, "pan": .20,
                             "sends": {"small_plate": -24}},
        "Wurlitzer replies": {"gain": -3.5, "eq": [("hpf", 190), ("bell", 330, -3.5, 1.1), ("lpf", 5800, 1)],
                              "comp": {"threshold": -23, "ratio": 1.8, "attack": 25, "release": 140},
                              "mono": True, "pan": .20, "sends": {"small_plate": -21}},
        "guitar lead": {"gain": -1.5, "amp": amp, "eq": [("hpf", 160), ("bell", 380, -3, 1), ("lpf", 5300, 1)],
                        "comp": {"threshold": -23, "ratio": 1.8, "attack": 25, "release": 140},
                        "mono": True, "pan": -.18, "sends": {"small_plate": -21}},
        "guitar chords": {"gain": -13, "amp": amp, "eq": [("hpf", 200), ("bell", 450, -3, 1), ("lpf", 4800, 1)],
                          "mono": True, "pan": .13, "sends": {"small_plate": -27}},
    }
    for voice in ("kick", "snare", "hats", "toms"):
        tracks[voice].update({"mono": True, "tape": {"drive_db": .8, "bump_db": .1, "mix": .35}})
    return {"tracks": tracks,
            "fx": {"tight_room": {"type": "reverb", "kind": "room", "decay": .32, "predelay": 3,
                                  "hpf": 220, "lpf": 4800, "width_pct": 55},
                   "small_plate": {"type": "reverb", "kind": "plate", "decay": .7, "predelay": 20,
                                   "hpf": 250, "lpf": 4100, "width_pct": 55}},
            "master": {"glue": {"threshold": -19, "ratio": 1.5, "attack": 35, "release": 170},
                       "target_lufs": -14, "ceiling": -1.3, "mono_below": 150}}


def compose():
    arrangement = Arrangement()
    bar = 0
    for label, role, chords, intensity in FORM:
        arrangement.song.marker(bar * 4, label)
        for local, chord in enumerate(chords):
            last = local == len(chords) - 1
            closing = role == "outro" and last
            arrangement.drum_bar(bar, local, role, intensity, last)
            arrangement.bass_bar(bar, chord, intensity, closing)
            arrangement.keys_bar(bar, local, role, chord, intensity, closing)
            arrangement.guitar_bar(bar, local, role, chord, intensity, closing)
            bar += 1
    song = arrangement.song
    song.length_beats = bar * 4
    song.mix = mixing()
    for track in song.tracks.values():
        instrument = get_instrument(track.instrument)
        assert track.notes and all(instrument.range[0] <= n.pitch <= instrument.range[1] for n in track.notes), track.name
        assert all(0 <= n.start and n.start + n.dur < song.end_beat for n in track.notes), track.name
        if not track.instrument.startswith("drums."):
            for note in track.notes:
                chord = CHORD_LINE[int(note.start // 4)]
                assert note.pitch % 12 in CH[chord][2] or note.dur <= .18, (track.name, chord, note)
    return song


if __name__ == "__main__":
    song = compose()
    for beat, label in song.markers:
        print(f"{song.seconds(beat):6.2f}s  {label}")
    print(f"{song.seconds(song.end_beat) + 3:.2f}s including release tail")
