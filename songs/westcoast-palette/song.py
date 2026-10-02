"""Sound-palette audition for the 1978 West Coast instrumental (Eb major, 119 BPM,
8th notes nearly straight: the reference measured 52:48, timing spread ~6-11 ms).

Every candidate plays the same 4-bar phrase over the same humanized groove:
    | Abmaj9 | Bb/Ab | Gm7 | Cm9  Fm7/Bb |
Candidates in one category are loudness-matched (each stem is normalised before its
strip and gets the same gain). `python songs/westcoast-palette/song.py` prints the
timestamp table.
"""
import random

from songwriter.instruments import surge
from songwriter.song import Song

BPM = 119
SWING8 = 0.52
SEG_BARS = 4
SEG = SEG_BARS * 4  # beats per segment

# -- harmony: (start beat, length, RH voicing pair, LH root) -------------------------
CHORDS = [
    (0.0, 4.0, ([60, 63, 67], [63, 67, 70]), 44),   # Abmaj9  (Cm triad over Ab)
    (4.0, 4.0, ([62, 65, 70], [65, 70, 72]), 44),   # Bb/Ab   (Ab lydian)
    (8.0, 4.0, ([62, 65, 70], [65, 70, 74]), 43),   # Gm7     (Bb triad over G)
    (12.0, 2.0, ([63, 67, 70], [67, 70, 74]), 48),  # Cm9     (Eb maj7 shape)
    (14.0, 2.0, ([63, 68, 72], [68, 72, 75]), 46),  # Fm7/Bb  (Ab/Bb, the "McDonald chord")
]
GUITAR = {0: [67, 72, 75], 4: [65, 70, 74], 8: [65, 70, 74], 12: [67, 70, 74], 14: [68, 72, 75]}
BRASS = {0: [60, 63, 67, 70], 4: [62, 65, 70, 72], 8: [62, 65, 67, 70], 12: [62, 63, 67, 70],
         14: [60, 63, 68, 72]}
LEAD = [  # (pitch, beat, dur, vel)
    ("Eb4", 1.5, 0.5, 92), ("G4", 2.0, 0.5, 96), ("Bb4", 2.5, 0.5, 100), ("C5", 3.0, 0.5, 104),
    ("D5", 3.5, 2.0, 112),
    ("C5", 5.5, 0.5, 98), ("Bb4", 6.0, 1.0, 102), ("G4", 7.0, 0.5, 94), ("Ab4", 7.5, 0.5, 96),
    ("Bb4", 8.0, 1.5, 108), ("Ab4", 9.5, 0.5, 92), ("G4", 10.0, 0.5, 96), ("F4", 10.5, 0.5, 94),
    ("G4", 11.0, 0.5, 98), ("Bb4", 11.5, 2.0, 108),
    ("G4", 13.5, 0.5, 96), ("F4", 14.0, 2.0, 104),
]
BASS = [  # finger bass, follows the piano's left-hand tresillo with passing notes
    ("Ab1", 0.0, 0.9, 108), ("Ab1", 1.5, 0.4, 90), ("Eb2", 2.0, 0.45, 96), ("Ab2", 3.0, 0.35, 92), ("Eb2", 3.5, 0.45, 88),
    ("Ab1", 4.0, 0.9, 106), ("Ab1", 5.5, 0.4, 88), ("Bb1", 6.0, 0.45, 96), ("C2", 6.5, 0.45, 90), ("Eb2", 7.0, 0.4, 94), ("Ab1", 7.5, 0.45, 96),
    ("G1", 8.0, 0.9, 108), ("G1", 9.5, 0.4, 88), ("D2", 10.0, 0.45, 96), ("Bb1", 11.0, 0.4, 92), ("B1", 11.5, 0.45, 94),
    ("C2", 12.0, 0.9, 108), ("G1", 13.5, 0.4, 90), ("Bb1", 14.0, 0.9, 104), ("Bb1", 15.0, 0.4, 92), ("A1", 15.5, 0.45, 94),
]

SEGMENTS = [  # (label, category, what)
    ("drums A: dry 1978 (damped kick, close mics)", "drums", "drums_a"),
    ("drums B: open studio room", "drums", "drums_b"),
    ("bass A: finger, warm (darkblack)", "bass", "bass.darkblack"),
    ("bass B: finger, bright (darkblack)", "bass", "bass.darkblack_bright"),
    ("bass C: short-scale (babyblue)", "bass", "bass.babyblue"),
    ("piano A: Yamaha C5 (Salamander)", "piano", "piano.salamander"),
    ("piano B: Steinway (Splendid)", "piano", "piano.splendid"),
    ("piano C: Steinway + OB-8 synth double", "piano", "piano.splendid+ob"),
    ("rhodes A: dry", "rhodes", "rhodes_dry"),
    ("rhodes B: Suitcase tremolo", "rhodes", "rhodes_trem"),
    ("guitar A: single-coil clean (green)", "guitar", "guitar.green_twang"),
    ("guitar B: humbucker clean (black)", "guitar", "guitar.black_twang"),
    ("guitar C: muted chops (green stac)", "guitar", "guitar.green_stac"),
    ("brass A: horns + trombones (warm)", "brass", "brass_a"),
    ("brass B: trumpets + trombones (full)", "brass", "brass_b"),
    ("brass C: harmon trumpets + horns (soft)", "brass", "brass_c"),
    ("lead A: synth, Minimoog-like (glide)", "lead", "lead_mini"),
    ("lead B: synth, soft retro (glide)", "lead", "lead_retro"),
    ("lead C: tenor sax", "lead", "lead_tenor"),
    ("lead D: Rhodes melody (octaves)", "lead", "lead_rhodes"),
    ("lead E (bonus): alto sax", "lead", "lead_alto"),
]
BED = {"drums": (), "bass": ("drums",), "piano": ("drums", "bass"), "rhodes": ("drums", "bass"),
       "guitar": ("drums", "bass", "piano"), "brass": ("drums", "bass", "piano"),
       "lead": ("drums", "bass", "piano")}

LEAD_SYNTH_A = surge("Kuniklo/Leads/Mini", portamento_ms=55, play_mode="mono_st_fp")
LEAD_SYNTH_B = surge("Vospi/Leads/Nice And Elegant Retro", portamento_ms=45, play_mode="mono_st_fp")
OB = surge("Brass/OB-8 Jump")


def ms(rng, sd_ms, bias_ms=0.0):
    """Timing offset in beats for a human player (sd and push/lag in milliseconds)."""
    return (rng.gauss(bias_ms, sd_ms)) / 1000 * BPM / 60


def groove_events():
    """4-bar drum groove: 8th hats accented on the beat, backbeat a hair late, ghost
    notes on the snare, a short tom fill into the next segment. Returns
    (voice, hit, beat, vel) with deterministic human timing."""
    rng = random.Random(1978)
    ev = []
    kicks = [(0, 1.5, 2.0), (0, 2.0, 3.5), (0, 1.5, 2.0), (0, 2.0, 2.5)]
    ghosts = [(1.75, 3.75), (0.75, 2.5, 3.75), (1.75, 2.75), (0.75, 1.75)]
    for bar in range(SEG_BARS):
        b0 = bar * 4
        for pos in kicks[bar]:
            ev.append(("kick", "kick", b0 + pos + ms(rng, 4), 112 if pos == 0 else rng.randint(88, 98)))
        for pos in (1.0, 3.0):
            if bar == 3 and pos == 3.0:
                continue
            ev.append(("snare", "snare", b0 + pos + ms(rng, 4, 4), rng.randint(112, 120)))
        for pos in ghosts[bar]:
            ev.append(("snare", "snare", b0 + pos + ms(rng, 6), rng.randint(26, 40)))
        for k in range(8):
            pos = k * 0.5
            if bar == 3 and pos >= 3.0:
                break
            hit = "hh_half" if (bar in (1,) and pos == 3.5) else "hh_closed"
            vel = (rng.randint(94, 104) if k % 2 == 0 else rng.randint(70, 80))
            ev.append(("hats", hit, b0 + pos + ms(rng, 4, 2 if k % 2 else 0), vel))
    # fill on beat 4 of bar 4: snare, two high toms, low tom
    for pos, voice, hit, vel in ((3.0, "snare", "snare", 110), (3.25, "toms", "tom_high", 100),
                                 (3.5, "toms", "tom_high", 96), (3.75, "toms", "tom_low", 106)):
        ev.append((voice, hit, 12 + pos + ms(rng, 5), vel))
    return ev


def comp_events(vel_scale=1.0, octave=0):
    """The two-handed bounce: left hand octaves on a 3+3+2 tresillo (1, 2&, 4), right hand
    rocking between two voicings on the remaining 8ths, pushing the next chord on 4&.
    Returns (pitches, beat, dur, vel) plus pedal (down, up) pairs."""
    rng = random.Random(119)
    notes, pedal = [], []
    for i, (start, length, (v1, v2), root) in enumerate(CHORDS):
        nxt = CHORDS[(i + 1) % len(CHORDS)]
        lh = [root - 12, root]
        if length == 4.0:
            rh = [(0.5, v1, 0.3, 84), (1.0, v2, 0.45, 100), (2.0, v1, 0.3, 82), (2.5, v2, 0.3, 90)]
            lhp = [(0.0, 0.75, 100), (1.5, 0.45, 88), (3.0, 0.45, 92)]
        else:  # half-bar chord
            rh = [(0.5, v1, 0.3, 84), (1.0, v2, 0.45, 96)] if start % 4 == 0 else [(0.0, v1, 0.3, 90), (0.5, v2, 0.3, 88)]
            lhp = [(0.0, 0.75, 100)] if start % 4 == 0 else [(-0.5, 1.0, 96), (1.0, 0.45, 90)]
        for pos, v, d, vel in rh:
            notes.append(([p + 12 * octave for p in v], start + pos + ms(rng, 5), d, int(vel * vel_scale)))
        for pos, d, vel in lhp:
            notes.append((lh, start + pos + ms(rng, 5), d, int(vel * vel_scale)))
        if start + length in (4.0, 8.0, 12.0, 16.0):   # 4& push of the next chord
            notes.append(([p + 12 * octave for p in nxt[2][0]], start + length - 0.5 + ms(rng, 5, -3), 0.85,
                          int(104 * vel_scale)))
        pedal.append((start + 0.02, start + 0.45))
    return notes, pedal


def place(track, notes, b0, transpose=0):
    for pitches, beat, dur, vel in notes:
        track.notes_at([p + transpose for p in pitches], b0 + beat, dur, vel)


def compose() -> Song:
    s = Song("Palette audition (West Coast 1978)", bpm=BPM, key="Eb")
    drum_sets = {
        "a": {v: s.track(f"{v}", "drums.virtuosity") for v in ("kick", "snare", "hats", "toms")},
        "b": {v: s.track(f"{v} B", "drums.virtuosity") for v in ("kick", "snare", "hats", "toms")},
    }
    # mic mix via the kit's CCs: A = damped kick, close mics, less overhead; B = open, room + vintage mic
    for v, t in drum_sets["a"].items():
        t.cc(71, 96, 0).cc(105, 80, 0).cc(109, 0, 0)
    for v, t in drum_sets["b"].items():
        t.cc(71, 30, 0).cc(105, 127, 0).cc(109, 70, 0).cc(111, 50, 0)
    bed_bass = s.track("bass", "bass.darkblack")
    bed_piano = s.track("piano", "piano.salamander")
    groove = groove_events()
    comp, pedal = comp_events()
    comp_soft, _ = comp_events(vel_scale=0.8)

    def drums(b0, kit="a"):
        for voice, hit, beat, vel in groove:
            drum_sets[kit][voice].hit(hit, b0 + beat, vel)

    def bass(track, b0):
        rng = random.Random(41)
        for n, beat, d, v in BASS:
            track.note(n, b0 + beat + ms(rng, 5, 2), d, v + rng.randint(-4, 4))

    def piano(track, b0, notes=comp):
        place(track, notes, b0)
        for down, up in pedal:
            track.sustain(b0 + down, b0 + up)

    def lead(track, b0, transpose=0, sax=False, vib=None):
        rng = random.Random(7)
        if sax:   # legato mode, gentle breath noise, expression swell over the phrase
            track.cc(64, 127, b0).cc(80, 50, b0)
            track.cc_ramp(11, b0 + 1.4, b0 + 4.0, 90, 122).cc_ramp(11, b0 + 4.0, b0 + 16, 122, 100)
        for n, beat, d, v in LEAD:
            st = b0 + beat + ms(rng, 6, 3)
            track.note(n, st, d + (0.06 if sax or vib else -0.04), v)
            if d >= 1.5:
                if sax:
                    track.cc_ramp(1, st + 0.3, st + d, 0, 80, step=0.25).cc(1, 0, st + d + 0.05)
                elif vib:
                    track.vibrato(st + 0.25, st + d, **vib)
        for p in list(track.notes)[-len(LEAD):]:
            p.pitch += transpose
        if sax:
            track.cc(64, 0, b0 + SEG - 0.1)

    for i, (label, cat, what) in enumerate(SEGMENTS):
        b0 = i * SEG
        s.marker(b0, label)
        bed = BED[cat]
        if "drums" in bed or cat == "drums":
            drums(b0, "b" if what == "drums_b" else "a")
        if "bass" in bed:
            bass(bed_bass, b0)
        if "piano" in bed:
            piano(bed_piano, b0, comp_soft)
        if cat == "bass":
            bass(s.track(label, what), b0)
        elif cat == "piano":
            inst = what.split("+")[0]
            piano(s.track(label, inst), b0)
            if what.endswith("+ob"):
                place(s.track(f"{label} | OB-8", OB), [n for n in comp if len(n[0]) == 3], b0)
        elif cat == "rhodes":
            piano(s.track(label, "epiano.rhodes"), b0)
        elif cat == "guitar":
            t = s.track(label, what)
            rng = random.Random(5)
            for start, chord in GUITAR.items():
                span = 4.0 if start % 4 == 0 and start != 12 else 2.0
                for pos, d, v in ((1.0, 0.15, 98), (1.75, 0.1, 64), (2.5, 0.2, 86), (3.0, 0.15, 94), (3.75, 0.1, 66)):
                    rel = pos if span == 4.0 else pos % 2.0
                    if span == 2.0 and not (start % 4 == 0 and pos < 2.0 or start % 4 == 2 and pos >= 2.0):
                        continue
                    t.notes_at(chord, b0 + start - (start % 4) + pos + ms(rng, 5), d, v, strum=0.012)
        elif cat == "brass":
            parts = {"brass_a": [("trombones", "brass.trombone_sus", (0, 1)), ("horns", "brass.horn_sus", (2, 3))],
                     "brass_b": [("trombones", "brass.trombone_sus", (0, 1)), ("trumpets", "brass.trumpet_sus", (2, 3))],
                     "brass_c": [("horns", "brass.horn_sus", (0, 1)), ("harmon tpts", "brass.trumpet_harmon", (2, 3))]}[what]
            for name, inst, idx in parts:
                t = s.track(f"{label} | {name}", inst)
                rng = random.Random(len(name))
                # "ooh" pads with swells on bars 1-2, a short answer figure in bar 3, rising into bar 4
                for start, chord in BRASS.items():
                    pitches = [chord[k] for k in idx]
                    if start in (0, 4):
                        t.notes_at(pitches, b0 + start + 0.5 + ms(rng, 8), 3.4, 84)
                        t.cc_ramp(11, b0 + start + 0.5, b0 + start + 2.5, 70, 118).cc_ramp(11, b0 + start + 2.5, b0 + start + 3.9, 118, 96)
                    elif start == 8:
                        t.cc(11, 112, b0 + start)
                        t.notes_at(pitches, b0 + start + 1.5 + ms(rng, 6), 0.4, 104)
                        t.notes_at(pitches, b0 + start + 2.0 + ms(rng, 6), 1.3, 96)
                    elif start == 12:
                        t.notes_at(pitches, b0 + start + ms(rng, 6), 1.6, 92)
                    else:
                        t.notes_at(pitches, b0 + start + ms(rng, 6), 1.9, 100)
                        t.cc_ramp(11, b0 + start, b0 + start + 1.9, 90, 124)
        elif cat == "lead":
            if what == "lead_mini":
                lead(s.track(label, LEAD_SYNTH_A), b0, vib={"rate_hz": 5.3, "cents": 18})
            elif what == "lead_retro":
                lead(s.track(label, LEAD_SYNTH_B), b0, vib={"rate_hz": 5.0, "cents": 10})
            elif what == "lead_tenor":
                lead(s.track(label, "sax.tenor"), b0, sax=True)
            elif what == "lead_alto":
                lead(s.track(label, "sax.alto"), b0, sax=True)
            elif what == "lead_rhodes":
                t = s.track(label, "epiano.rhodes")
                rng = random.Random(7)
                for n, beat, d, v in LEAD:
                    st = b0 + beat + ms(rng, 6, 3)
                    t.note(n, st, d, v).note(n, st, d, v - 10)
                for nn in t.notes[-2 * len(LEAD)::2]:
                    nn.pitch += 12
                t.sustain(b0 + 3.5, b0 + 5.4).sustain(b0 + 11.5, b0 + 13.4).sustain(b0 + 14.0, b0 + 15.9)

    for t in s.tracks.values():
        t.swing(SWING8, grid=0.5)
    s.length_beats = len(SEGMENTS) * SEG + 4

    drums_mix = {
        "kick": {"gain": -1, "eq": [("hpf", 30), ("bell", 65, 3, 1.2), ("bell", 380, -4, 1.4), ("bell", 3500, 2, 1.0)],
                 "comp": {"threshold": -18, "ratio": 3, "attack": 15, "release": 90}, "tape": {"drive_db": 5}},
        "snare": {"gain": -2, "eq": [("hpf", 90), ("bell", 220, 2, 1.0), ("bell", 900, -2, 2.0), ("hshelf", 6000, -2)],
                  "comp": {"threshold": -20, "ratio": 3, "attack": 10, "release": 120}, "tape": {"drive_db": 5},
                  "sends": {"plate": -14, "room": -16}},
        "hats": {"gain": -10, "eq": [("hpf", 300), ("hshelf", 9000, -2)], "pan": 0.35, "tape": {"drive_db": 3}},
        "toms": {"gain": -4, "eq": [("hpf", 60), ("bell", 600, -3, 1.0)], "width": 1.0, "sends": {"room": -14}},
    }
    tracks = {}
    for v, cfg in drums_mix.items():
        tracks[v] = cfg
        b = dict(cfg)
        b["sends"] = {**cfg.get("sends", {}), "room": -8}
        tracks[f"{v} B"] = b
    tracks.update({
        "bass": {"gain": -3, "eq": [("hpf", 35), ("bell", 90, 1.5, 1.0), ("bell", 700, 1, 1.0)],
                 "comp": {"threshold": -20, "ratio": 3, "attack": 20, "release": 120}, "tape": {"drive_db": 4},
                 "mono": True},
        "piano": {"gain": -6, "eq": [("hpf", 90), ("bell", 300, -2, 1.0)], "width": 0.7, "mono_below": 150,
                  "sends": {"plate": -16}},
    })
    for label, cat, what in SEGMENTS:
        if cat == "bass":
            tracks[label] = dict(tracks["bass"])
        elif cat == "piano":
            tracks[label] = {"gain": -2.5 if what.endswith("+ob") else -2, "eq": [("hpf", 70), ("bell", 300, -2, 1.0)],
                             "width": 0.7, "mono_below": 150, "sends": {"plate": -16}}
            if what.endswith("+ob"):
                tracks[f"{label} | OB-8"] = {"gain": -11, "eq": [("hpf", 200), ("lpf", 4000)],
                                             "chorus": {"rate_hz": 0.5, "depth_ms": 2.0, "mix": 0.35}}
        elif cat == "rhodes":
            cfg = {"gain": -2, "eq": [("hpf", 70), ("bell", 250, -2, 1.0), ("bell", 2500, 1.5, 1.0)],
                   "tape": {"drive_db": 4}, "sends": {"plate": -18}}
            if what == "rhodes_trem":
                cfg["tremolo"] = {"rate_hz": 4.2, "depth": 0.45}
            tracks[label] = cfg
        elif cat == "guitar":
            tracks[label] = {"gain": -4, "eq": [("hpf", 150), ("bell", 400, -2, 1.0)],
                             "comp": {"threshold": -24, "ratio": 4, "attack": 5, "release": 80},
                             "chorus": {"rate_hz": 0.8, "depth_ms": 2.5, "mix": 0.4}, "pan": -0.3,
                             "sends": {"plate": -14}}
        elif cat == "brass":
            for name in ("trombones", "horns", "trumpets", "harmon tpts"):
                tracks[f"{label} | {name}"] = {"gain": -4, "eq": [("hpf", 120), ("bell", 350, -2, 1.0)],
                                               "width": 1.3, "sends": {"plate": -10}}
        elif cat == "lead":
            tracks[label] = {"gain": 0.6 if what == "lead_mini" else 0, "eq": [("hpf", 150)], "comp": {"threshold": -22, "ratio": 2.5, "attack": 15, "release": 150},
                             "sends": {"plate": -12, "dly": -18}}
    s.mix = {
        "tracks": tracks,
        "fx": {
            "plate": {"type": "reverb", "kind": "plate", "decay": 1.8, "predelay": 25, "hpf": 250, "lpf": 8000},
            "room": {"type": "reverb", "kind": "room", "decay": 0.6, "predelay": 5, "hpf": 200, "lpf": 7000},
            "dly": {"type": "delay", "beats": 0.75, "feedback": 0.25, "hpf": 400, "lpf": 3500},
        },
        "master": {"glue": {"threshold": -18, "ratio": 2, "attack": 30, "release": 250}, "target_lufs": -14},
    }
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
