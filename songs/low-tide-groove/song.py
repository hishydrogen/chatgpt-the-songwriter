"""Checkpoint 2: three original eight-bar grooves with the selected BBBB palette.

The guitar amp and tape colour are gentler than checkpoint 1 at the user's request.
Same tempo, harmony and central melodic idea; the rhythm and space vary. No reference
audio or reference riff is used. One silent bar separates each eight-bar sketch.
"""
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from songwriter.song import Song, note_number  # noqa: E402
from songwriter.instruments import get_instrument  # noqa: E402

BPM = 86
BARS = 8
STEP = 36
VERSIONS = [
    ("groove A: late pocket", "A"),
    ("groove B: forward syncopation", "B"),
    ("groove C: toms and space", "C"),
]
PROGRESSION = ["Em9", "Em9", "Am9", "B7", "Em9", "G6", "Am9", "B7"]
# The Am9 ninth is carried by the melody; keep the accompaniment free of a
# close B/C semitone cluster so the Wurlitzer stays smooth.
VOICINGS = {"Em9": [55, 59, 62, 66], "Am9": [55, 60, 64, 69],
            "B7": [57, 63, 66, 71], "G6": [55, 59, 62, 64]}
BASS_NOTES = {"Em9": ["E2", "B1", "D2", "G2", "E2"],
              "Am9": ["A1", "E2", "G2", "C2", "A1"],
              "B7": ["B1", "F#2", "A2", "D#2", "B1"],
              "G6": ["G1", "D2", "E2", "B2", "G1"]}
ALLOWED = {"Em9": {2, 4, 6, 7, 11}, "Am9": {0, 4, 7, 9, 11},
           "B7": {3, 6, 9, 11}, "G6": {2, 4, 7, 11}}
# (position within bar, note, length). The first two bars are the face of the song.
GUITAR_PHRASE = [
    [(.5, "B3", .30), (1.5, "D4", .28), (2.25, "E4", .50), (3.25, "G4", .30)],
    [(.25, "F#4", .25), (.75, "E4", .70), (2.25, "B3", .25), (3, "D4", .28), (3.5, "E4", .34)],
    [(.75, "G4", .40), (1.5, "A4", .35), (2.25, "C5", .35), (3, "B4", .40)],
    [(.5, "A4", .25), (1.25, "F#4", .40), (2, "D#4", .45), (3, "B3", .65)],
    [(.5, "B3", .30), (1.5, "D4", .28), (2.25, "E4", .50), (3.25, "F#4", .30)],
    [(.25, "G4", .60), (1.25, "E4", .25), (2.25, "D4", .50), (3.25, "B3", .30)],
    [(.5, "E4", .30), (1.5, "G4", .30), (2.25, "B4", .35), (3, "C5", .40)],
    [(.25, "D#4", .30), (.75, "F#4", .40), (1.75, "A4", .30),
     (2.5, "F#4", .30), (3.25, "B3", .55)],
]
KIT_CC = {71: 112, 76: 58, 81: 57, 86: 58, 101: 127, 102: 18, 103: 127,
          104: 15, 105: 42, 106: 24, 107: 0, 109: 8, 111: 96}


def played(rng, beat, bias_ms=0, spread_ms=4):
    return max(0, beat + rng.gauss(bias_ms, spread_ms) * BPM / 60000)


def drums(kit, start, style):
    rng = random.Random(19690926)
    for bar in range(BARS):
        b = start + 4 * bar
        if style == "A":
            kicks = (0, 2.5) if bar % 2 == 0 else (0, 1.75, 2.5)
            hats = [(0, 51), (.5, 34), (1, 47), (2, 51), (2.5, 33), (3, 47)]
            snare_delay = 12
            tom_hits = [(3.25, "tom_high", 68), (3.625, "tom_low", 74)] if bar in (3, 7) else []
        elif style == "B":
            kicks = (0, 1.5, 2.5) if bar % 2 == 0 else (0, 1.75, 3.5)
            hats = [(p * .5, 50 if p % 2 == 0 else 36) for p in range(8)]
            snare_delay = 4
            tom_hits = [(3.0, "tom_high", 65), (3.5, "tom_low", 75)] if bar in (3, 7) else []
        else:
            kicks = (0, 2.5) if bar % 2 == 0 else (.25, 2.25)
            hats = [(.5, 41), (2.5, 43)]
            snare_delay = 14
            tom_hits = [(1.75, "tom_low", 60), (3.5, "tom_high", 66)]
            if bar in (3, 7):
                tom_hits += [(3.75, "tom_low", 73)]
        for p in kicks:
            kit["kick"].hit("kick", played(rng, b + p, 0, 3), 94 if p < 1 else 84)
        for p in (1, 3):
            # In the last bar the fill takes the last backbeat's space.
            if bar == 7 and p == 3:
                continue
            kit["snare"].hit("snare", played(rng, b + p, snare_delay, 4), 91 + rng.randint(-3, 3))
        if style != "C" and bar != 7:
            kit["snare"].hit("snare", played(rng, b + 2.75, 6, 5), 35)
        for p, velocity in hats:
            if bar == 7 and p >= 3:
                continue
            kit["hats"].hit("hh_closed", played(rng, b + p, 3, 3), velocity)
        for p, hit, velocity in tom_hits:
            kit["toms"].hit(hit, played(rng, b + p, 6, 4), velocity, dur=.16)


def bass(track, start, style):
    rng = random.Random(19690820)
    positions = {"A": [.125, 1.25, 2.25, 3.25, 3.75],
                 "B": [0, 1.5, 2.5, 3, 3.5], "C": [.125, 1.5, 2.5, 3.25, 3.75]}[style]
    for bar, chord in enumerate(PROGRESSION):
        for i, (p, note) in enumerate(zip(positions, BASS_NOTES[chord])):
            if style == "C" and i in (1, 4):
                continue
            duration = [.46, .28, .35, .22, .16][i] * (1.18 if style == "C" else 1)
            velocity = [93, 82, 88, 80, 82][i] + rng.randint(-3, 3)
            track.note(note, played(rng, start + bar * 4 + p, 3, 5), duration, velocity)
    track.cc(21, 0, start).cc(113, 0, start).cc(114, 0, start)


def keys(track, start, style):
    rng = random.Random(19690730)
    rhythm = {"A": [(.5, .65, 62), (2.5, .45, 55)],
              "B": [(.75, .55, 64), (2.25, .45, 59)], "C": [(.5, 1.05, 57)]}[style]
    for bar, chord in enumerate(PROGRESSION):
        for p, duration, velocity in rhythm:
            beat = played(rng, start + bar * 4 + p, 5, 5)
            track.notes_at(VOICINGS[chord], beat, duration, velocity + rng.randint(-2, 2), strum=.012)
            track.sustain(beat, beat + duration - .03)


def guitar(track, start, style):
    rng = random.Random(19690721)
    for bar, phrase in enumerate(GUITAR_PHRASE):
        chord = PROGRESSION[bar]
        for i, (p, pitch, duration) in enumerate(phrase):
            assert note_number(pitch) % 12 in ALLOWED[chord], (bar, chord, pitch)
            if style == "C" and bar % 2 == 0 and i == 1:
                continue
            if style == "B":
                p -= .125
                duration *= .92
            elif style == "C":
                duration *= 1.12
            beat = played(rng, start + bar * 4 + p, 5, 5)
            velocity = 83 + (7 if i == 2 else 0) + rng.randint(-3, 3)
            track.note(pitch, beat, duration, velocity)
            if duration >= .6:
                track.vibrato(beat + .16, beat + duration - .03, rate_hz=4.8, cents=8)
    track.cc(70, 8, start).bend(0, start)


def mix_tracks(label):
    tracks = {}
    drums_cfg = {
        "kick": {"gain": -4, "eq": [("hpf", 33), ("bell", 78, -.5, 1),
                                     ("bell", 280, -3, 1), ("lpf", 4000, 1)]},
        "snare": {"gain": -6.3, "eq": [("hpf", 105), ("bell", 230, 1, 1),
                                         ("bell", 750, -2, 1.1), ("lpf", 6500, 1)],
                  "sends": {"tight_room": -25}},
        "hats": {"gain": -17, "eq": [("hpf", 450), ("lpf", 7600, 1)], "pan": -.13},
        "toms": {"gain": -8, "eq": [("hpf", 60), ("bell", 420, -2, 1), ("lpf", 5300, 1)],
                 "pan": -.10, "sends": {"tight_room": -25}},
    }
    for voice, cfg in drums_cfg.items():
        cfg.update({"mono": True, "tape": {"drive_db": .8, "bump_db": .1, "mix": .35}})
        tracks[f"{label} | {voice}"] = cfg
    tracks[f"{label} | bass"] = {
        "gain": -2.5, "eq": [("hpf", 38), ("bell", 110, .7, .8), ("bell", 330, -2.5, 1),
                             ("lpf", 2400, 1)],
        "comp": {"threshold": -23, "ratio": 2.4, "attack": 25, "release": 155},
        "tape": {"drive_db": 1, "bump_db": .1, "mix": .25}, "mono": True}
    tracks[f"{label} | keys"] = {
        "gain": -8, "eq": [("hpf", 145), ("bell", 330, -3.5, 1.1), ("lpf", 6000, 1)],
        "tape": {"drive_db": .6, "bump_db": 0, "mix": .2}, "mono": True, "pan": .20,
        "sends": {"small_plate": -24}}
    tracks[f"{label} | guitar"] = {
        "gain": -1.5,
        "amp": [{"type": "amp", "PreGain": -8, "Distortion": 4, "Drive": .08,
                 "model": 0, "t_model": 8, "c_model": 9, "Presence": 2}],
        "eq": [("hpf", 160), ("bell", 380, -3, 1), ("lpf", 5300, 1)],
        "comp": {"threshold": -23, "ratio": 1.8, "attack": 25, "release": 140},
        "mono": True, "pan": -.18, "sends": {"small_plate": -21}}
    return tracks


def compose():
    song = Song("Low Tide - Checkpoint 2", bpm=BPM, key="Em")
    tracks_cfg = {}
    for i, (label, style) in enumerate(VERSIONS):
        start = i * STEP
        song.marker(start, label)
        kit = {v: song.track(f"{label} | {v}", "drums.virtuosity")
               for v in ("kick", "snare", "hats", "toms")}
        for track in kit.values():
            for cc, value in KIT_CC.items():
                track.cc(cc, value, 0)
        drums(kit, start, style)
        bass(song.track(f"{label} | bass", "bass.darkblack"), start, style)
        keys(song.track(f"{label} | keys", "epiano.wurlitzer"), start, style)
        guitar(song.track(f"{label} | guitar", "guitar.emily_di"), start, style)
        tracks_cfg.update(mix_tracks(label))
    trims_file = Path(__file__).with_name("loudness_trims.json")
    trims = json.loads(trims_file.read_text()) if trims_file.exists() else {}
    for label, _ in VERSIONS:
        for name, cfg in tracks_cfg.items():
            if name.startswith(label + " |"):
                cfg["gain"] += trims.get(label, 0)
    song.length_beats = len(VERSIONS) * STEP
    song.mix = {
        "tracks": tracks_cfg,
        "fx": {"tight_room": {"type": "reverb", "kind": "room", "decay": .32, "predelay": 3,
                              "hpf": 220, "lpf": 4800, "width_pct": 55},
               "small_plate": {"type": "reverb", "kind": "plate", "decay": .7, "predelay": 20,
                               "hpf": 250, "lpf": 4100, "width_pct": 55}},
        "master": {"glue": {"threshold": -19, "ratio": 1.5, "attack": 35, "release": 170},
                   "target_lufs": -14, "ceiling": -1.3, "mono_below": 150}}
    for i, (label, _) in enumerate(VERSIONS):
        begin, end = i * STEP, i * STEP + 32
        for name, track in song.tracks.items():
            if not name.startswith(label + " |"):
                continue
            # Keep a humanized opening hit inside its own audition segment.
            for note in track.notes:
                note.start = max(begin, note.start)
            inst = get_instrument(track.instrument)
            assert track.notes and all(inst.range[0] <= n.pitch <= inst.range[1] for n in track.notes), name
            assert all(begin <= n.start and n.start + n.dur < end for n in track.notes), name
    return song


if __name__ == "__main__":
    song = compose()
    for beat, label in song.markers:
        print(f"{song.seconds(beat):6.2f}s  {label}")
