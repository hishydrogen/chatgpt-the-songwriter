"""8-bar groove sketch, three bass versions back to back (A, B, A+B layer).

Bars 1-4: drums + riff + Mirage timpani answers. Bars 5-8: Toto stabs moving over the
static F (Fm7 -> Db/F -> Eb/F), DX bell doubling the answer, minor orch hits, fill.
"""
from songwriter.instruments import surge
from songwriter.song import Song

BPM = 103
SWING = 0.61
RIFF = [  # 2 bars, F minor: (note, beat, dur, vel)
    ("F1", 0.0, 0.45, 118), ("F1", 0.75, 0.2, 84), ("Ab1", 1.5, 0.22, 100), ("F2", 1.75, 0.2, 112),
    ("F1", 2.25, 0.4, 108), ("C2", 3.0, 0.22, 96), ("Eb2", 3.5, 0.2, 100), ("E2", 3.75, 0.2, 92),
    ("F1", 4.0, 0.45, 118), ("F1", 4.75, 0.2, 84), ("Ab1", 5.5, 0.22, 100), ("Bb1", 5.75, 0.22, 104),
    ("B1", 6.25, 0.2, 96), ("C2", 6.5, 0.45, 112), ("Eb2", 7.25, 0.2, 98), ("C2", 7.5, 0.3, 100),
]
ANSWER = [("C4", 2.5, 0.3, 110), ("Eb4", 2.75, 0.3, 100), ("F4", 3.0, 0.5, 116),
          ("Ab4", 6.75, 0.25, 104), ("G4", 7.0, 0.25, 100), ("F4", 7.25, 0.6, 116)]
STAB_RHYTHM = [(1.75, 0.2, 116), (2.5, 0.35, 104), (5.75, 0.2, 116), (6.5, 0.15, 100), (7.0, 0.35, 110)]
STAB_CHORDS = {4: ["Ab3", "C4", "Eb4", "F4"], 6: ["Ab3", "Db4", "F4"]}  # per 2-bar half
VERSIONS = [
    ("A: FM bass 8-bit", ["mirage.bass_fm"]),
    ("B: OB-8 brass low 8-bit", ["mirage.bass_brass"]),
    ("A+B layer", ["mirage.bass_brass", "mirage.bass_fm"]),
]


def compose() -> Song:
    s = Song("Groove sketch", bpm=BPM, key="Fm")
    kick, snare, hats, perc, toms = (s.track(n, "drums.linn86") for n in ("kick", "snare", "hats", "perc", "toms"))
    timp = s.track("timpani", "mirage.timpani")
    bell = s.track("bell", surge("Rozzer/Keys/DX Tonez"))
    stab = s.track("stab", surge("Brass/Toto Brass"))
    orch = s.track("orch", "fairlight.orchhit_m")

    for vi, (label, basses) in enumerate(VERSIONS):
        v0 = s.bar(8 * vi)
        s.marker(v0, label)
        btracks = [s.track(f"bass {vi}{chr(97 + k)}", inst) for k, inst in enumerate(basses)]
        for bar in range(8):
            b = v0 + s.bar(bar)
            hook = bar >= 4
            last = bar == 7
            # drums: four-on-nothing pounding kick, snare+clap 2/4, swung 16th hats
            for pos in ((0, 0.75, 2.5, 2.75) if bar % 2 == 0 else (0, 0.75, 2.5, 3.5)):
                if not (last and pos > 2):
                    kick.hit("kick", b + pos, 120 if pos == 0 else 104)
            for pos in (1, 3):
                if last and pos == 3:
                    continue
                snare.hit("snare", b + pos, 120).hit("clap", b + pos, 112)
                if hook:
                    snare.hit("metal3", b + pos, 100)
            for k in range(16):
                pos = k * 0.25
                if last and pos >= 2:
                    break
                if bar % 2 == 1 and pos == 3.5:
                    hats.hit("hh_open", b + pos, 96)
                else:
                    hats.hit("hh_closed", b + pos, (110, 70, 92, 66)[k % 4])
            perc.hit("cowbell", b + 1.5, 72)
            if hook:
                for k in range(8):
                    perc.hit("tambourine", b + k * 0.5 + 0.5 * (k % 2 == 0) * 0, 84 if k % 2 else 64)
            if last:  # fill: toms into the downbeat
                for k, (d, v) in enumerate([("tom_high", 112), ("tom_high", 100), ("tom_mid", 112),
                                            ("tom_mid", 104), ("tom_low", 118), ("tom_low", 110),
                                            ("snare", 120), ("snare", 124)]):
                    (toms if d.startswith("tom") else snare).hit(d, b + 2 + k * 0.25, v)
        # bass riff x4
        for rep in range(4):
            for t in btracks:
                for n, p, d, v in RIFF:
                    t.note(n, v0 + s.bar(2 * rep) + p, d, v)
        # answers: timpani always, bell doubles an octave up in the hook
        for rep in range(4):
            h0 = v0 + s.bar(2 * rep)
            for n, p, d, v in ANSWER:
                if rep == 3 and p > 6:
                    continue
                timp.note(n.replace("4", "3"), h0 + p, d, v)
                if rep >= 2:
                    bell.note(n.replace("4", "5"), h0 + p, d, v - 10)
        # stabs in the hook, chord moves over the static riff
        for rep, chord in ((2, STAB_CHORDS[4]), (3, STAB_CHORDS[6])):
            h0 = v0 + s.bar(2 * rep)
            for p, d, v in STAB_RHYTHM:
                if rep == 3 and p > 6:
                    continue
                stab.notes_at(chord, h0 + p, d, v)
        # orch hits: hook downbeat and the end of the fill
        orch.note("F4", v0 + s.bar(4), 0.5, 120)
        orch.note("F4", v0 + s.bar(7) + 1.0, 0.3, 112)
        orch.note("Db4", v0 + s.bar(7) + 1.5, 0.3, 116)

    for t in s.tracks.values():
        t.swing(SWING, grid=0.25)
    s.length_beats = s.bar(24) + 4

    bass_cfg = {"gain": -6, "eq": [("hpf", 32), ("bell", 120, 1.5, 1.0)],
                "comp": {"threshold": -20, "ratio": 4, "attack": 8, "release": 90},
                "tape": {"drive_db": 8}, "mono": True}
    s.mix = {
        "tracks": {
            "kick": {"gain": -1, "eq": [("hpf", 30), ("bell", 62, 1.0, 1.0), ("bell", 3000, 3, 1.0)],
                     "comp": {"threshold": -16, "ratio": 4, "attack": 12, "release": 70}, "tape": {"drive_db": 7}},
            "snare": {"gain": -1, "eq": [("hpf", 120), ("bell", 220, 2, 1.0), ("bell", 5000, 2.5, 1.0)],
                      "tape": {"drive_db": 7}, "sends": {"gate": -3}},
            "hats": {"gain": -12, "eq": [("hpf", 500), ("hshelf", 8000, 2)], "pan": 0.3, "tape": {"drive_db": 5}},
            "perc": {"gain": -13, "eq": [("hpf", 400)], "pan": -0.35, "sends": {"plate": -16}},
            "toms": {"gain": -5, "eq": [("hpf", 60)], "width": 1.3, "sends": {"gate": -6}},
            "timpani": {"gain": -4.5, "eq": [("hpf", 60), ("bell", 3000, 2, 1.0)], "pan": -0.15,
                        "sends": {"hall": -8}},
            "bell": {"gain": -8.5, "eq": [("hpf", 400)], "pan": 0.3, "chorus": {"mix": 0.3},
                     "sends": {"plate": -8, "dly": -14}},
            "stab": {"gain": -3.5, "eq": [("hpf", 180), ("bell", 350, -2, 1.0), ("bell", 2500, 2, 1.0)],
                     "comp": {"threshold": -20, "ratio": 3, "attack": 5, "release": 80},
                     "chorus": {"rate_hz": 0.5, "depth_ms": 2.0, "mix": 0.45}, "sends": {"plate": -10}},
            "orch": {"gain": -5, "eq": [("hpf", 90)], "width": 1.2, "sends": {"plate": -8, "hall": -12}},
        },
        "fx": {
            "gate": {"type": "gated", "decay": 2.0, "hold_ms": 230, "release_ms": 40, "kind": "room",
                     "size": 18, "hpf": 250, "lpf": 9000},
            "plate": {"type": "reverb", "kind": "plate", "decay": 1.5, "predelay": 15, "hpf": 300, "lpf": 9000},
            "hall": {"type": "reverb", "kind": "hall", "decay": 2.4, "predelay": 20, "hpf": 150, "lpf": 7000},
            "dly": {"type": "delay", "beats": 0.75, "feedback": 0.3, "hpf": 500, "lpf": 5000},
        },
        "master": {"eq": [("lshelf", 90, -2.5, 0.7), ("bell", 1500, 1, 0.7)],
                   "glue": {"threshold": -16, "ratio": 2, "attack": 20, "release": 200},
                   "target_lufs": -14},
    }
    for vi, (_, basses) in enumerate(VERSIONS):
        for k, inst in enumerate(basses):
            cfg = dict(bass_cfg)
            if len(basses) == 2:
                cfg["gain"] = -7.5 if k == 0 else -10.5
            s.mix["tracks"][f"bass {vi}{chr(97 + k)}"] = cfg
    return s
