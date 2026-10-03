"""Sound-palette audition for "Last Summer" (2010s vocaloid rock after siinamota's "少女A";
D major, 170 BPM, straight 8ths).

Part 1 - voices: every UTAU voicebank sings the same 8-bar chorus over the same band.
Part 2 - distorted guitars: the same 8-bar riff (4 bars palm-muted, 4 bars open), each tone
         double-tracked hard left/right over drums and bass.
Part 3+ - clean guitar, piano, colour, bass, drums: each candidate plays the same 4 bars.
Section list with timestamps: `python songs/summer-palette/song.py`.
"""
import importlib.util
import random
from pathlib import Path

from songwriter.instruments import surge
from songwriter.song import Song, note_number

_spec = importlib.util.spec_from_file_location("last_summer", Path(__file__).parent.parent / "last-summer" / "song.py")
ls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ls)

PROG8 = ls.CHORUS[:8]
PROG4 = ls.CHORUS[:4]
VOX_OPTS = {"vibrato_cents": 28, "port_pre": 0.03, "port_post": 0.045, "consonant": 0.85,
            "breath_gap": 0.3, "tail_gap": 0.15}

VOICES = [
    ("voice A: Kumi", "voice.kumi", {}),
    ("voice B: Kumi strong", "voice.kumi", {"style": "S"}),
    ("voice C: Hikari One", "voice.hikari", {}),
    ("voice D: Milk", "voice.milk", {}),
    ("voice E: Viki Hopper", "voice.viki", {}),
]

# guitar rigs (guitarix via scripts/lv2host): TS9 boost -> tube amp, tonestack, cabinet
TS9 = {"type": "ts9", "fslider2_": 0.12, "fslider1_": 750, "fslider0_": 2}
RIGS = {
    "guitar A: Marshall crunch": [TS9, {"type": "amp", "PreGain": 6, "Distortion": 55, "Drive": 0.4,
                                         "model": 0, "t_model": 4, "c_model": 0, "Presence": 6}],
    "guitar B: Mesa high gain": [TS9, {"type": "amp", "PreGain": 10, "Distortion": 75, "Drive": 0.5,
                                        "model": 0, "t_model": 9, "c_model": 13, "Presence": 5}],
    "guitar C: Vox crunch": [{"type": "amp", "PreGain": 2, "Distortion": 35, "Drive": 0.3,
                              "model": 0, "t_model": 8, "c_model": 9, "Presence": 5}],
}
CLEAN_RIG = [{"type": "amp", "PreGain": -6, "Distortion": 4, "Drive": 0.1, "model": 0, "t_model": 2,
              "c_model": 6, "Presence": 4}]
EDGE_RIG = [{"type": "amp", "PreGain": 0, "Distortion": 18, "Drive": 0.25, "model": 0, "t_model": 8,
             "c_model": 9, "Presence": 5}]
BASS_RIG = {"chain": [{"type": "amp", "PreGain": 0, "Distortion": 30, "Drive": 0.35, "model": 0,
                       "t_model": 16, "c_model": 3, "Presence": 4}], "dry": 0.5}

CLEANS = [
    ("clean A: DI into a clean amp + chorus", "guitar.emily_di", {"amp": CLEAN_RIG, "chorus": {"rate_hz": 0.8, "depth_ms": 2.5, "mix": 0.45}}),
    ("clean B: Gretsch twang", "guitar.green_twang", {}),
    ("clean C: edge-of-breakup arpeggio", "guitar.emily_di", {"amp": EDGE_RIG}),
]
PIANOS = [
    ("piano A: Salamander (bright)", "piano.salamander"),
    ("piano B: Splendid (mellow)", "piano.splendid"),
    ("piano C: upright (intimate)", "piano.upright"),
]
COLOURS = [
    ("colour A: string section", "strings"),
    ("colour B: glockenspiel", "perc.glockenspiel"),
    ("colour C: music box (synth)", surge("Plucks/Magic Music Box")),
    ("colour D: synth strings", surge("Polysynths/Juno-60 Strings")),
]
BASSES = [
    ("bass A: finger, bright", "bass.darkblack_bright", {}),
    ("bass B: short-scale, warm", "bass.babyblue", {}),
    ("bass C: drive bass", "bass.darkblack_bright", {"amp": BASS_RIG}),
]
KITS = {
    "drums.drskit": {"tom1": "tom_high", "tom2": "tom_mid", "tom3": "tom_low"},
    "drums.virtuosity": {"tom1": "tom_high", "tom2": "tom_high_off", "tom3": "tom_low"},
}
DRUMS = [("drums A: DRSKit (rock)", "drums.drskit"), ("drums B: Virtuosity (natural)", "drums.virtuosity")]
# loudness trims (dB) from scripts/audition_levels.py: candidates within +/-1 dB
TRIM = {"voice A: Kumi": 0.5, "guitar C: Vox crunch": 1.2, "clean A: DI into a clean amp + chorus": 2.0,
        "clean B: Gretsch twang": -2.6, "colour A: string section": -1.6, "colour D: synth strings": 1.1,
        "bass B: short-scale, warm": -1.0}


class Palette:
    def __init__(self):
        s = self.s = Song("Summer palette", bpm=ls.BPM, key=ls.KEY)
        self.rng = random.Random(2013)
        self.kit = self.kit_tracks("bed", "drums.drskit")
        self.bed_bass = s.track("bed bass", "bass.darkblack_bright")
        self.bed_gtr = [s.track("bed guitar L", "guitar.emily_di"), s.track("bed guitar R", "guitar.emily_di")]
        self.bed_piano = s.track("bed piano", "piano.salamander")
        self.beat = 0.0

    def kit_tracks(self, prefix, inst):
        s = self.s
        return {k: s.track(f"{prefix} {k}", inst) for k in ("kick", "snare", "hats", "cymbals", "toms")} | {"inst": inst}

    # -- feel ------------------------------------------------------------------------
    def T(self, beat, ms=4.0):
        return max(0.0, beat + self.rng.gauss(0, ms) / 1000 * ls.BPM / 60)

    def V(self, vel, spread=4):
        return int(max(1, min(127, vel + self.rng.randint(-spread, spread))))

    def section(self, label, bars):
        self.s.marker(self.beat, label)
        b0 = self.beat
        self.beat += self.s.bar(bars)
        return b0

    def chords(self, prog, b0):
        return [(c, b0 + 4 * i) for i, c in enumerate(prog)]

    # -- band ------------------------------------------------------------------------
    def drums(self, kit, b0, bars, fill=True, crash=True, vel=1.0):
        """8-beat rock: kick 1, &2, 3 (+&4 every other bar), snare 2 and 4, 8th hats."""
        toms = KITS[kit["inst"]]
        for bar in range(bars):
            b = b0 + 4 * bar
            last = fill and bar == bars - 1
            kicks = (0, 1.5, 2) if bar % 2 == 0 else (0, 1.5, 2, 3.5)
            for k in kicks:
                if last and k >= 2:
                    continue
                kit["kick"].hit("kick", self.T(b + k), self.V((118 if k in (0, 2) else 104) * vel))
            for k in (1, 3):
                if last and k == 3:
                    continue
                kit["snare"].hit("snare", self.T(b + k), self.V(116 * vel))
            for i in range(8):
                if last and i >= 4:
                    break
                kit["hats"].hit("hh_closed", self.T(b + i * 0.5), self.V((100, 76)[i % 2] * vel))
            if last:  # snare-tom fill over beats 3-4
                fill_hits = [("snare", 2.0), ("snare", 2.25), (toms["tom1"], 2.5), (toms["tom1"], 2.75),
                             (toms["tom2"], 3.0), (toms["tom2"], 3.25), (toms["tom3"], 3.5), (toms["tom3"], 3.75)]
                for i, (d, p) in enumerate(fill_hits):
                    kit["snare" if d == "snare" else "toms"].hit(d, self.T(b + p), self.V(96 + 3 * i))
                kit["kick"].hit("kick", self.T(b + 2.0), self.V(110))
        if crash:
            kit["cymbals"].hit("crash", self.T(b0), self.V(110 * vel))

    def bass(self, t, prog, b0, vel=1.0):
        """Root 8ths, an octave pop on the & of 4, a lead-in to the next root."""
        for i, (c, b) in enumerate(self.chords(prog, b0)):
            r = ls.root_of(c)
            nxt = ls.root_of(prog[(i + 1) % len(prog)])
            for k in range(8):
                p = r + 12 if k == 7 else r
                if k == 7 and i == len(prog) - 1:
                    p = nxt - 2 if nxt - 2 >= note_number("E1") else nxt + 1
                t.note(p, self.T(b + k * 0.5, 5), 0.42, self.V((112 if k % 2 == 0 else 98) * vel))

    def riff(self, tracks, prog, b0, palm=True, vel=1.0):
        """Power-chord 8ths. palm=True: palm-muted chugs with open accents on 1, &2 and 4."""
        for side, t in enumerate(tracks):
            rng = random.Random(7 + side)          # two different takes
            for c, b in self.chords(prog, b0):
                notes = ls.power(c)
                for k in range(8):
                    p = b + k * 0.5
                    accent = (not palm) or k in (0, 3, 6)
                    t.cc(70, 0 if accent else 127, max(0.0, p - 0.03))
                    dur = 0.46 if accent else 0.22
                    when = p + rng.gauss(0, 0.006) * ls.BPM / 60
                    for j, n in enumerate(notes):
                        t.note(n, max(0.0, when + j * 0.004), dur, int(min(127, (122 if accent else 104) * vel
                                                                           + rng.randint(-4, 4))))

    def arpeggio(self, t, prog, b0, vel=1.0):
        """Let-ring 8th arpeggios on open-sounding voicings (root low, colour tones up top)."""
        for c, b in self.chords(prog, b0):
            r = ls.root_of(c, "E2", "D#3")
            v = ls.voicing(c, note_number("F#5") if c != "A" else note_number("E5"), 3)
            shape = [r, v[0], v[1], v[2], v[3], v[2], v[1], v[0]]
            for k, n in enumerate(shape):
                t.note(n, self.T(b + k * 0.5, 6), 1.4, self.V((96 if k % 4 == 0 else 84) * vel))

    def piano(self, t, prog, b0, vel=1.0):
        """Rock piano: left-hand root octaves on quarters, right-hand chords on 8ths."""
        for c, b in self.chords(prog, b0):
            r = ls.root_of(c, "C2", "B2")
            rh = ls.voicing(c, note_number("F#5") if "A" not in c[:1] else note_number("E5"), 3)
            for k in range(4):
                t.notes_at([r, r + 12], self.T(b + k), 0.9, self.V(92 * vel))
            for k in range(8):
                t.notes_at(rh, self.T(b + k * 0.5), 0.4, self.V((90 if k % 2 == 0 else 74) * vel))

    def strings(self, tracks, prog, b0, vel=1.0):
        """Sustained chords, the top voice moving by step. tracks: [(track, role)] with role
        "top" (upper two voices), "mid" (lower two) or "root" (bass note), or "all"."""
        tops = ["F#5", "E5", "E5", "D5", "D5", "C#5", "D5", "E5"]
        for i, (c, b) in enumerate(self.chords(prog, b0)):
            v = ls.voicing(c, note_number(tops[i % len(tops)]), 3)
            parts = {"top": v[2:], "mid": v[:2], "root": [ls.root_of(c, "C3", "B3")],
                     "all": [ls.root_of(c, "C3", "B3")] + v}
            for t, role in tracks:
                for n in parts[role]:
                    t.note(n, b + 0.02, 3.9, self.V(84 * vel))

    def bells(self, t, prog, b0, vel=1.0):
        """Counter-melody, 8ths, in the bell register."""
        line = [["D6", "A5", "F#6", "A5", "E6", "A5", "D6", "B5"],
                ["C#6", "A5", "E6", "A5", "C#6", "E5", "A5", "E6"],
                ["C#6", "A5", "F#6", "A5", "E6", "C#6", "A5", "C#6"],
                ["D6", "B5", "F#6", "B5", "D6", "A5", "B5", "F#5"]]
        for i, (c, b) in enumerate(self.chords(prog, b0)):
            for k, n in enumerate(line[i % 4]):
                t.note(n, self.T(b + k * 0.5, 3), 0.45, self.V((96 if k % 2 == 0 else 80) * vel))

    def sing(self, t, b0, x):
        b = b0
        for p, lyr, d in ls.HOOK:
            if p != "r":
                t.note(p, b, d, 100, lyric=lyr, x=dict(x) if x else None)
            b += d


def compose() -> Song:
    a = Palette()
    s = a.s
    mixer = {}
    # part 1: voices over the full band
    for label, inst, x in VOICES:
        b0 = a.section(label, 8)
        a.drums(a.kit, b0, 4, fill=True)
        a.drums(a.kit, b0 + 16, 4, fill=True)
        a.bass(a.bed_bass, PROG8, b0, 0.95)
        a.riff(a.bed_gtr, PROG8[:4], b0, palm=True, vel=0.9)
        a.riff(a.bed_gtr, PROG8[4:], b0 + 16, palm=False, vel=0.85)
        a.piano(a.bed_piano, PROG8, b0, 0.8)
        t = s.track(label, inst)
        t.opts.update(VOX_OPTS)
        a.sing(t, b0, x)
        mixer[label] = {"gain": -1.0, "eq": [("hpf", 150), ("bell", 280, -2.5, 1.0), ("bell", 750, -2.0, 1.0),
                                             ("bell", 3200, 2.5, 1.0), ("hshelf", 9000, 2.5)],
                        "comp": {"threshold": -22, "ratio": 3.5, "attack": 4, "release": 70},
                        "sends": {"plate": -12, "dly": -20}}
    a.beat += s.bar(1)
    # part 2: distorted guitar rigs, double-tracked
    for label, rig in RIGS.items():
        b0 = a.section(label, 8)
        a.drums(a.kit, b0, 4)
        a.drums(a.kit, b0 + 16, 4)
        a.bass(a.bed_bass, PROG8, b0, 0.95)
        pair = [s.track(f"{label} | L", "guitar.emily_di"), s.track(f"{label} | R", "guitar.emily_di")]
        a.riff(pair, PROG8[:4], b0, palm=True)
        a.riff(pair, PROG8[4:], b0 + 16, palm=False)
        for side, t in zip((-1, 1), pair):
            mixer[t.name] = {"amp": rig, "gain": -5.5, "pan": side * 0.9,
                             "eq": [("hpf", 90), ("bell", 220, -2, 1.0), ("bell", 3000, 1.0, 1.0), ("lpf", 9000)]}
    a.beat += s.bar(1)
    # part 3: clean guitars over drums (lighter) and bass
    for label, inst, cfg in CLEANS:
        b0 = a.section(label, 4)
        a.drums(a.kit, b0, 4, vel=0.85)
        a.bass(a.bed_bass, PROG4, b0, 0.9)
        t = s.track(label, inst)
        a.arpeggio(t, PROG4, b0)
        mixer[label] = {**cfg, "gain": -3.5, "eq": [("hpf", 140), ("bell", 300, -2, 1.0), ("hshelf", 5000, 1.5)],
                        "width": 0.8, "sends": {"plate": -14, "dly": -18}}
    a.beat += s.bar(1)
    # part 4: pianos over drums, bass and quiet guitars
    for label, inst in PIANOS:
        b0 = a.section(label, 4)
        a.drums(a.kit, b0, 4)
        a.bass(a.bed_bass, PROG4, b0, 0.9)
        a.riff(a.bed_gtr, PROG4, b0, palm=True, vel=0.85)
        a.piano(s.track(label, inst), PROG4, b0)
        mixer[label] = {"gain": -3.5, "eq": [("hpf", 110), ("bell", 320, -2.5, 1.0), ("hshelf", 6000, 2.0)],
                        "comp": {"threshold": -20, "ratio": 3, "attack": 8, "release": 90},
                        "width": 0.6, "mono_below": 200, "sends": {"plate": -16}}
    a.beat += s.bar(1)
    # part 5: colour layers over the full band
    for label, inst in COLOURS:
        b0 = a.section(label, 4)
        a.drums(a.kit, b0, 4)
        a.bass(a.bed_bass, PROG4, b0, 0.9)
        a.riff(a.bed_gtr, PROG4, b0, palm=False, vel=0.8)
        a.piano(a.bed_piano, PROG4, b0, 0.7)
        if inst == "strings":
            parts = [(s.track(f"{label} | violins", "strings.violins_sus"), "top"),
                     (s.track(f"{label} | violas", "strings.violas_sus"), "mid"),
                     (s.track(f"{label} | celli", "strings.celli_sus"), "root")]
            a.strings(parts, PROG4, b0)
            for t, *_ in parts:
                mixer[t.name] = {"gain": -7, "eq": [("hpf", 150), ("bell", 400, -2, 1.0)], "width": 0.7,
                                 "sends": {"hall": -10}}
        elif "strings" in label:
            t = s.track(label, inst)
            a.strings([(t, "all")], PROG4, b0)
            mixer[label] = {"gain": -4.5, "eq": [("hpf", 200), ("bell", 400, -2, 1.0)], "width": 0.9,
                            "sends": {"hall": -12}}
        else:
            t = s.track(label, inst)
            a.bells(t, PROG4, b0)
            mixer[label] = {"gain": -5, "eq": [("hpf", 400)], "width": 0.8, "sends": {"plate": -12, "dly": -16}}
    a.beat += s.bar(1)
    # part 6: basses over drums and guitars
    for label, inst, cfg in BASSES:
        b0 = a.section(label, 4)
        a.drums(a.kit, b0, 4)
        a.riff(a.bed_gtr, PROG4, b0, palm=True, vel=0.85)
        a.bass(s.track(label, inst), PROG4, b0)
        mixer[label] = {**cfg, "gain": -2.5, "eq": [("hpf", 35), ("bell", 800, 1.5, 1.0)],
                        "comp": {"threshold": -20, "ratio": 4, "attack": 6, "release": 80}, "mono": True}
    a.beat += s.bar(1)
    # part 7: drum kits over bass and guitars
    for label, inst in DRUMS:
        b0 = a.section(label, 4)
        kit = a.kit_tracks(label + " |", inst)
        a.drums(kit, b0, 4)
        a.bass(a.bed_bass, PROG4, b0, 0.9)
        a.riff(a.bed_gtr, PROG4, b0, palm=True, vel=0.85)
        for k, cfg in drum_strips().items():
            mixer[f"{label} | {k}"] = cfg
    s.length_beats = a.beat + 4
    for name, cfg in mixer.items():
        cand = name.split(" | ")[0]
        if cand in TRIM:
            cfg["gain"] = cfg.get("gain", 0) + TRIM[cand]

    bed = {f"bed {k}": cfg for k, cfg in drum_strips().items()}
    bed.update({
        "bed bass": {"gain": -7, "eq": [("hpf", 35), ("bell", 800, 1.5, 1.0)],
                     "comp": {"threshold": -20, "ratio": 4, "attack": 6, "release": 80}, "mono": True},
        "bed guitar L": {"amp": RIGS["guitar A: Marshall crunch"], "gain": -10, "pan": -0.9,
                         "eq": [("hpf", 90), ("bell", 220, -2, 1.0), ("lpf", 9000)]},
        "bed guitar R": {"amp": RIGS["guitar A: Marshall crunch"], "gain": -10, "pan": 0.9,
                         "eq": [("hpf", 90), ("bell", 220, -2, 1.0), ("lpf", 9000)]},
        "bed piano": {"gain": -12, "eq": [("hpf", 110), ("bell", 320, -2.5, 1.0), ("hshelf", 6000, 2.0)],
                      "width": 0.6, "mono_below": 200},
    })
    s.mix = {
        "tracks": {**bed, **mixer},
        "fx": {
            "plate": {"type": "reverb", "kind": "plate", "decay": 1.5, "predelay": 20, "hpf": 300, "lpf": 9000},
            "room": {"type": "reverb", "kind": "room", "decay": 0.7, "predelay": 5, "hpf": 250, "lpf": 8000},
            "hall": {"type": "reverb", "kind": "hall", "decay": 2.2, "predelay": 25, "hpf": 250, "lpf": 8000},
            "dly": {"type": "delay", "beats": 0.75, "feedback": 0.3, "hpf": 500, "lpf": 5000},
        },
        "master": {"glue": {"threshold": -16, "ratio": 2, "attack": 20, "release": 200}, "target_lufs": -14},
    }
    return s


def drum_strips():
    return {
        "kick": {"gain": -6, "eq": [("hpf", 30), ("bell", 60, 2, 1.2), ("bell", 350, -3, 1.0), ("bell", 4000, 2, 1.0)],
                 "comp": {"threshold": -18, "ratio": 4, "attack": 10, "release": 80}},
        "snare": {"gain": -7, "eq": [("hpf", 90), ("bell", 200, 1.5, 1.0), ("bell", 5000, 2, 1.0)],
                  "comp": {"threshold": -18, "ratio": 4, "attack": 8, "release": 100}, "sends": {"room": -10}},
        "hats": {"gain": -15, "eq": [("hpf", 400)], "pan": 0.25},
        "cymbals": {"gain": -14, "eq": [("hpf", 300)], "width": 0.75},
        "toms": {"gain": -9, "eq": [("hpf", 70), ("bell", 400, -2, 1.0)], "width": 0.8, "sends": {"room": -10}},
    }


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
