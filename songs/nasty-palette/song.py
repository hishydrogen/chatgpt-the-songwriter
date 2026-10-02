"""Sound-palette audition for the Control-era track: every candidate plays the same
2-bar figure over the same LinnDrum-style groove (103 BPM, ~61% 16th swing, F minor).
Section list with timestamps is printed by `python songs/nasty-palette/song.py`.
"""
from songwriter.instruments import surge
from songwriter.song import Song

BPM = 103
SWING = 0.61

# 2-bar bass riff, F minor: (note, beat, dur, vel)
RIFF = [
    ("F1", 0.0, 0.45, 118), ("F1", 0.75, 0.2, 84), ("Ab1", 1.5, 0.22, 100), ("F2", 1.75, 0.2, 112),
    ("F1", 2.25, 0.4, 108), ("C2", 3.0, 0.22, 96), ("Eb2", 3.5, 0.2, 100), ("E2", 3.75, 0.2, 92),
    ("F1", 4.0, 0.45, 118), ("F1", 4.75, 0.2, 84), ("Ab1", 5.5, 0.22, 100), ("Bb1", 5.75, 0.22, 104),
    ("B1", 6.25, 0.2, 96), ("C2", 6.5, 0.45, 112), ("Eb2", 7.25, 0.2, 98), ("C2", 7.5, 0.3, 100),
]
# answer motif (timpani / bells / metal): lands in the gaps of the riff
MOTIF = [("C4", 2.5, 0.3, 110), ("Eb4", 2.75, 0.3, 100), ("F4", 3.0, 0.5, 116),
         ("Ab4", 6.75, 0.25, 104), ("G4", 7.0, 0.25, 100), ("F4", 7.25, 0.6, 116)]
# stab rhythm: Fm7 / Ab-Eb voicing pushes on the 16th before the beat
STABS = [(1.75, 0.2, 116), (2.5, 0.35, 104), (5.75, 0.2, 116), (6.5, 0.15, 100), (7.0, 0.35, 110)]
STAB_CHORD = ["Ab3", "C4", "Eb4", "F4"]

SECTIONS = [  # (track name, instrument, what to play)
    ("drums dry", None, "drums_dry"),
    ("drums processed", None, "drums_fx"),
    ("bass A: FM bass, 8-bit Mirage", "mirage.bass_fm", "riff"),
    ("bass B: OB-8 brass played low, 8-bit (car-horn trick)", "mirage.bass_brass", "riff"),
    ("bass C: finger bass, 8-bit", "mirage.bass_finger", "riff"),
    ("bass D: DX7 + OB-8 layer (clean)", "layer", "riff"),
    ("bass E: FM slap (clean)", surge("Basses/FM Slap"), "riff"),
    ("timpani (Mirage)", "mirage.timpani", "motif"),
    ("metal (Mirage)", "mirage.metal", "motif"),
    ("orch hit major", "fairlight.orchhit", "hits"),
    ("orch hit minor", "fairlight.orchhit_m", "hits"),
    ("stab A: JX-10 Double Brass", surge("Brass/JX-10 Double Brass"), "stabs"),
    ("stab B: OB-8 Jump", surge("Brass/OB-8 Jump"), "stabs"),
    ("stab C: Toto Brass", surge("Brass/Toto Brass"), "stabs"),
    ("stab D: Retro minor stab", surge("Chords/Minor Chord Retro Stab"), "stab1"),
    ("bell A: DX Tonez", surge("Rozzer/Keys/DX Tonez"), "motif_hi"),
    ("bell B: The 1980s", surge("Plucks/The 1980s"), "motif_hi"),
    ("bell C: FM Bell 2", surge("Plucks/Bell 2"), "motif_hi"),
]
BARS_PER = 2


def drums(s, kick, snare, hats, b0, bars, full=True):
    for bar in range(bars):
        b = b0 + s.bar(bar)
        for pos in ((0, 0.75, 2.5, 2.75) if bar % 2 == 0 else (0, 0.75, 2.5, 3.5)):
            kick.hit("kick", b + pos, 120 if pos == 0 else 104)
        for pos in (1, 3):
            snare.hit("snare", b + pos, 120)
            if full:
                snare.hit("clap", b + pos, 112)
        for k in range(16):
            pos = k * 0.25
            if bar % 2 == 1 and pos == 3.5:
                hats.hit("hh_open", b + pos, 96)
            else:
                hats.hit("hh_closed", b + pos, (110, 70, 92, 66)[k % 4])
        if full:
            hats.hit("cowbell", b + 1.5, 70)


def compose() -> Song:
    s = Song("Palette audition", bpm=BPM, key="Fm")
    kick = s.track("kick", "drums.linn86")
    snare = s.track("snare", "drums.linn86")
    hats = s.track("hats", "drums.linn86")
    dry_k = s.track("dry kick", "drums.linn86")
    dry_s = s.track("dry snare", "drums.linn86")
    dry_h = s.track("dry hats", "drums.linn86")
    sec_len = s.bar(BARS_PER)

    for i, (label, inst, what) in enumerate(SECTIONS):
        b0 = i * sec_len
        s.marker(b0, label)
        if what == "drums_dry":
            drums(s, dry_k, dry_s, dry_h, b0, BARS_PER, full=False)
            continue
        drums(s, kick, snare, hats, b0, BARS_PER)
        if what == "drums_fx":
            continue
        if inst == "layer":
            parts = [s.track("bass D dx", surge("Basses/FM Bass 1")), s.track("bass D ob", surge("Basses/Square Bass"))]
        else:
            parts = [s.track(label, inst)]
        for t in parts:
            if what == "riff":
                for n, p, d, v in RIFF:
                    t.note(n, b0 + p, d, v)
            elif what in ("motif", "motif_hi"):
                for n, p, d, v in MOTIF:
                    t.note(n if what == "motif" else n.replace("4", "5"), b0 + p, d, v)
            elif what == "hits":
                for p, d, v in STABS:
                    t.note("F4", b0 + p, d, v)
            elif what == "stabs":
                for p, d, v in STABS:
                    t.notes_at(STAB_CHORD, b0 + p, d, v)
            elif what == "stab1":
                for p, d, v in STABS:
                    t.note("F4", b0 + p, d, v)

    for t in s.tracks.values():
        t.swing(SWING, grid=0.25)
    s.length_beats = len(SECTIONS) * sec_len + 2

    drum_strip = {"tape": {"drive_db": 7}}
    s.mix = {
        "tracks": {
            "dry kick": {"gain": 0}, "dry snare": {"gain": -2}, "dry hats": {"gain": -8},
            "kick": {"gain": -2, "eq": [("hpf", 30), ("bell", 60, 2, 1.0)], **drum_strip,
                     "comp": {"threshold": -18, "ratio": 4, "attack": 15, "release": 80}},
            "snare": {"gain": -3, "eq": [("hpf", 120), ("bell", 5000, 2, 1.0)], **drum_strip,
                      "sends": {"gate": -4}},
            "hats": {"gain": -11, "eq": [("hpf", 400)], "pan": 0.25, **drum_strip},
        },
        "fx": {"gate": {"type": "gated", "decay": 2.0, "hold_ms": 230, "release_ms": 40,
                        "kind": "room", "size": 18, "hpf": 250, "lpf": 9000},
               "plate": {"type": "reverb", "kind": "plate", "decay": 1.6, "predelay": 15, "hpf": 300}},
        "master": {"glue": {"threshold": -16, "ratio": 2, "attack": 20, "release": 200},
                   "target_lufs": -14},
    }
    for label, inst, what in SECTIONS[2:]:
        names = ["bass D dx", "bass D ob"] if inst == "layer" else [label]
        for n in names:
            cfg = {"gain": -3 if what == "riff" else -6, "sends": {"plate": -12}}
            if what == "riff":
                cfg.update({"eq": [("hpf", 30)], "comp": {"threshold": -20, "ratio": 4, "attack": 10, "release": 100},
                            "tape": {"drive_db": 8}, "mono": True, "sends": {}})
                if n == "bass D ob":
                    cfg["gain"] = -7
            if what in ("stabs", "stab1"):
                cfg.update({"chorus": {"rate_hz": 0.5, "depth_ms": 2.0, "mix": 0.4}, "eq": [("hpf", 200)]})
            s.mix["tracks"][n] = cfg
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
