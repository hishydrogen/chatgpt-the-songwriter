"""Mirage - a Control-era (1986) Minneapolis instrumental. F minor, 103 BPM, ~61% 16th swing.

Intro 8 | Verse 16 | Pre 4 | Hook 8 | Verse 16 | Pre 4 | Hook 8 | Breakdown 8 | Hook 16 | Outro 4
The riff is the song: an 8-bit layered bass (OB-8 brass played low + Mirage FM bass),
Mirage timpani answering in the gaps, Toto-style brass stabs moving over a static F,
DX bell doubling the answers, minor orchestra hits on the big moments.
"""
from songwriter.instruments import surge
from songwriter.song import Song

BPM = 103
SWING = 0.61

# -- material ------------------------------------------------------------------
RIFF = [  # 2 bars in F: (semitones above the riff root F1, beat, dur, vel)
    (0, 0.0, 0.45, 118), (0, 0.75, 0.2, 84), (3, 1.5, 0.22, 100), (12, 1.75, 0.2, 112),
    (0, 2.25, 0.4, 108), (7, 3.0, 0.22, 96), (10, 3.5, 0.2, 100), (11, 3.75, 0.2, 92),
    (0, 4.0, 0.45, 118), (0, 4.75, 0.2, 84), (3, 5.5, 0.22, 100), (5, 5.75, 0.22, 104),
    (6, 6.25, 0.2, 96), (7, 6.5, 0.45, 112), (10, 7.25, 0.2, 98), (7, 7.5, 0.3, 100),
]
RIFF_TURN = [  # alternate 2nd bar used every 4th repeat: climbs to the octave
    (0, 4.0, 0.45, 118), (0, 4.75, 0.2, 84), (12, 5.0, 0.2, 108), (10, 5.5, 0.2, 100),
    (7, 5.75, 0.2, 98), (5, 6.25, 0.2, 96), (3, 6.5, 0.2, 100), (0, 6.75, 0.3, 112),
    (12, 7.25, 0.2, 110), (13, 7.5, 0.2, 100), (14, 7.75, 0.2, 104),
]
PRE_RIFF = [  # 1 bar driving 8ths for the pre-chorus, root-relative
    (0, 0.0, 0.4, 118), (0, 0.75, 0.2, 90), (12, 1.0, 0.2, 108), (0, 1.5, 0.3, 100),
    (0, 2.25, 0.2, 96), (12, 2.5, 0.2, 110), (0, 3.0, 0.3, 104), (7, 3.5, 0.2, 100), (10, 3.75, 0.2, 100),
]
ANSWER = [(60, 2.5, 0.3, 110), (63, 2.75, 0.3, 100), (65, 3.0, 0.5, 116),
          (68, 6.75, 0.25, 104), (67, 7.0, 0.25, 100), (65, 7.25, 0.6, 116)]
TIMPANI_SOLO = [  # breakdown: the quirky timpani tune, 4 bars (beat offsets)
    (53, 0.0, 0.5, 120), (48, 0.75, 0.25, 100), (53, 1.0, 0.5, 112), (56, 1.75, 0.25, 104),
    (55, 2.5, 0.5, 110), (53, 3.0, 0.5, 116), (51, 3.75, 0.25, 100),
    (48, 4.0, 0.5, 116), (51, 4.75, 0.25, 104), (53, 5.0, 0.75, 118), (60, 6.0, 0.5, 120),
    (58, 6.5, 0.25, 104), (56, 6.75, 0.25, 104), (55, 7.0, 0.5, 110), (53, 7.5, 0.5, 116),
    (53, 8.0, 0.5, 120), (48, 8.75, 0.25, 100), (53, 9.0, 0.5, 112), (56, 9.75, 0.25, 104),
    (60, 10.5, 0.5, 114), (63, 11.0, 0.5, 118), (60, 11.75, 0.25, 104),
    (65, 12.0, 0.75, 122), (63, 13.0, 0.25, 108), (60, 13.25, 0.25, 104), (58, 13.5, 0.25, 104),
    (56, 13.75, 0.25, 104), (55, 14.0, 0.5, 112), (53, 15.0, 1.0, 124),
]
STAB_RHYTHM = [(1.75, 0.2, 116), (2.5, 0.35, 104), (5.75, 0.2, 116), (6.5, 0.15, 100), (7.0, 0.35, 110)]
CHORD = {  # stab voicings over the static F
    "Fm7": [56, 60, 63, 65], "Db/F": [56, 61, 65], "Eb/F": [55, 58, 63], "C7#9": [52, 58, 63],
    "Db": [56, 61, 65, 68], "Eb": [55, 58, 63, 67],
}


class Arranger:
    def __init__(self):
        s = self.s = Song("Mirage", bpm=BPM, key="Fm")
        self.kick, self.snare, self.hats, self.perc, self.toms, self.cym = (
            s.track(n, "drums.linn86") for n in ("kick", "snare", "hats", "perc", "toms", "cymbals"))
        self.bass_body = s.track("bass body", "mirage.bass_brass")
        self.bass_crunch = s.track("bass crunch", "mirage.bass_fm")
        self.timp = s.track("timpani", "mirage.timpani")
        self.bell = s.track("bell", surge("Rozzer/Keys/DX Tonez"))
        self.stab = s.track("stab", surge("Brass/Toto Brass"))
        self.stab2 = s.track("stab hi", surge("Brass/JX-10 Double Brass"))
        self.orch = s.track("orch", "fairlight.orchhit_m")
        self.bar = 0

    # -- building blocks -------------------------------------------------------------
    def b(self, bar, beat=0.0):
        return self.s.bar(bar) + beat

    def bass(self, bar, pattern, root=29, vel_scale=1.0, skip_after=None):
        for st, p, d, v in pattern:
            if skip_after is not None and p >= skip_after:
                continue
            for t in (self.bass_body, self.bass_crunch):
                t.note(root + st, self.b(bar, p), d, int(v * vel_scale))

    def riff(self, bar, reps, turn_every=4, root=29):
        for r in range(reps):
            pat = RIFF if (r + 1) % turn_every else RIFF[:8] + RIFF_TURN
            self.bass(bar + 2 * r, pat, root)

    def answers(self, bar, reps, timp=True, bell=False, skip_last=False):
        for r in range(reps):
            for n, p, d, v in ANSWER:
                if skip_last and r == reps - 1 and p > 6:
                    continue
                if timp:
                    self.timp.note(n - 12, self.b(bar + 2 * r, p), d, v)
                if bell:
                    self.bell.note(n + 12, self.b(bar + 2 * r, p), d, v - 10)

    def stabs(self, bar, chords, hi=False, skip_last=False):
        for r, ch in enumerate(chords):
            for p, d, v in STAB_RHYTHM:
                if skip_last and r == len(chords) - 1 and p > 6:
                    continue
                self.stab.notes_at(CHORD[ch], self.b(bar + 2 * r, p), d, v)
                if hi:
                    self.stab2.notes_at([n + 12 for n in CHORD[ch][-2:]], self.b(bar + 2 * r, p), d, v - 12)

    def drums(self, bar, bars, kick=True, snare=True, clap=True, hats="16", metal=False, tamb=False,
              cowbell=True, open_hat=True, fill_last=False, crash_first=False, kick_pattern=None):
        for i in range(bars):
            b0 = self.b(bar + i)
            last = fill_last and i == bars - 1
            if crash_first and i == 0:
                self.cym.hit("crash", b0, 110)
            if kick:
                pat = kick_pattern or ((0, 0.75, 2.5, 2.75) if i % 2 == 0 else (0, 0.75, 2.5, 3.5))
                for pos in pat:
                    if not (last and pos > 2):
                        self.kick.hit("kick", b0 + pos, 120 if pos == 0 else 104)
            for pos in (1, 3):
                if last and pos == 3:
                    continue
                if snare:
                    self.snare.hit("snare", b0 + pos, 120)
                if clap:
                    self.snare.hit("clap", b0 + pos, 112)
                if metal:
                    self.snare.hit("metal3", b0 + pos, 100)
            if hats:
                step = 0.25 if hats == "16" else 0.5
                for k in range(int(4 / step)):
                    pos = k * step
                    if last and pos >= 2:
                        break
                    if open_hat and i % 2 == 1 and pos == 3.5:
                        self.hats.hit("hh_open", b0 + pos, 96)
                    elif step == 0.25:
                        self.hats.hit("hh_closed", b0 + pos, (110, 70, 92, 66)[k % 4])
                    else:
                        self.hats.hit("hh_closed", b0 + pos, 100 if k % 2 else 84)
            if cowbell:
                self.perc.hit("cowbell", b0 + 1.5, 72)
            if tamb:
                for k in range(8):
                    self.perc.hit("tambourine", b0 + k * 0.5, 84 if k % 2 else 64)
            if last:
                self.fill(bar + i)

    def fill(self, bar, start=2.0):
        seq = [("tom_high", 112), ("tom_high", 100), ("tom_mid", 112), ("tom_mid", 104),
               ("tom_low", 118), ("tom_low", 110), ("snare", 120), ("snare", 124)]
        for k, (d, v) in enumerate(seq):
            (self.toms if d.startswith("tom") else self.snare).hit(d, self.b(bar, start + k * 0.25), v)

    def snare_build(self, bar, bars):
        """Pre-chorus roll: 8ths, then 16ths, rising."""
        n = 0
        total = bars * 4 * 4
        for i in range(bars):
            step = 0.5 if i < bars - 1 else 0.25
            for k in range(int(4 / step)):
                n += 1
                self.snare.hit("snare", self.b(bar + i, k * step), 70 + int(50 * (i * 16 + k * step * 4) / total))

    # -- sections ---------------------------------------------------------------------------
    def intro(self, bar):
        s = self.s
        s.marker(self.b(bar), "intro")
        # orchestra hit + timpani call, then the machine starts
        self.orch.note(65, self.b(bar), 0.6, 122)
        self.timp.note(41, self.b(bar), 1.5, 124)
        self.answers(bar, 2, timp=True)
        self.drums(bar, 4, kick=False, snare=False, clap=True, hats="16", cowbell=False, open_hat=False)
        self.kick.hit("kick", self.b(bar + 2), 120).hit("kick", self.b(bar + 3), 120)
        self.orch.note(65, self.b(bar + 3, 3.5), 0.3, 116)
        self.drums(bar + 4, 4, fill_last=True, crash_first=True)
        self.riff(bar + 4, 2)
        self.answers(bar + 4, 2, skip_last=True)
        return bar + 8

    def verse(self, bar, n=1):
        self.s.marker(self.b(bar), f"verse {n}")
        self.drums(bar, 16, crash_first=True, fill_last=True, metal=(n == 2))
        self.riff(bar, 8)
        self.answers(bar, 8, skip_last=True)
        # sparse stab punctuation in the second half, more in verse 2
        for r in range(4, 8):
            if n == 2 or r % 2 == 1:
                self.stab.notes_at(CHORD["Fm7"], self.b(bar + 2 * r, 5.75), 0.2, 112)
                self.stab.notes_at(CHORD["Fm7"], self.b(bar + 2 * r, 6.5), 0.15, 100)
        if n == 2:
            for r in range(0, 8, 2):
                self.perc.hit("metal1", self.b(bar + 2 * r, 3.75), 90)
            self.answers(bar + 8, 4, timp=False, bell=True, skip_last=True)
        return bar + 16

    def pre(self, bar):
        self.s.marker(self.b(bar), "pre")
        self.drums(bar, 4, snare=False, clap=True, hats="8", cowbell=False, open_hat=False)
        self.snare_build(bar, 4)
        for i, (root, ch) in enumerate([(25, "Db"), (25, "Db"), (27, "Eb"), (27, "Eb")]):
            self.bass(bar + i, PRE_RIFF, root=root, skip_after=(3.0 if i == 3 else None))
            for p, d, v in ((0.0, 0.6, 118), (1.75, 0.2, 108), (2.5, 0.4, 110)):
                self.stab.notes_at(CHORD[ch], self.b(bar + i, p), d, v)
        self.orch.note(61, self.b(bar), 0.5, 116)
        self.orch.note(63, self.b(bar + 2), 0.5, 118)
        for k, n in enumerate((63, 63, 64, 64)):  # 16th push into the hook
            self.orch.note(n, self.b(bar + 3, 3.0 + k * 0.25), 0.2, 110 + 3 * k)
        return bar + 4

    def hook(self, bar, final=False, label="hook"):
        self.s.marker(self.b(bar), label)
        self.drums(bar, 8, metal=True, tamb=True, crash_first=True, fill_last=True)
        self.riff(bar, 4)
        self.answers(bar, 4, timp=True, bell=True, skip_last=True)
        chords = ["Fm7", "Db/F", "Fm7", "Eb/F"]
        self.stabs(bar, chords, hi=final, skip_last=True)
        self.orch.note(65, self.b(bar), 0.5, 122)
        self.orch.note(65, self.b(bar + 7, 1.0), 0.3, 112)
        self.orch.note(61, self.b(bar + 7, 1.5), 0.3, 116)
        return bar + 8

    def breakdown(self, bar):
        self.s.marker(self.b(bar), "breakdown")
        # drum machine breakdown: kick + claps + toms + metal, the timpani sings
        for i in range(8):
            b0 = self.b(bar + i)
            self.kick.hit("kick", b0, 120).hit("kick", b0 + 2.5, 108)
            self.snare.hit("clap", b0 + 1, 116).hit("clap", b0 + 3, 116)
            self.perc.hit("metal2", b0 + 1.75, 92)
            if i >= 4:
                self.snare.hit("snare", b0 + 1, 118).hit("snare", b0 + 3, 118)
                for k in range(8):
                    self.hats.hit("hh_closed", b0 + k * 0.5, 96 if k % 2 else 80)
            for pos, d in ((0.75, "tom_low"), (3.25, "tom_mid")):
                self.toms.hit(d, b0 + pos, 100)
        for n, p, d, v in TIMPANI_SOLO:
            self.timp.note(n, self.b(bar, p), d, v)
            self.timp.note(n, self.b(bar + 4, p), d, v)
            if p >= 0:
                self.bell.note(n + 24, self.b(bar + 4, p), d, v - 18)
        self.riff(bar + 4, 2)  # bass back in for the second half
        self.orch.note(65, self.b(bar + 4), 0.5, 120)
        self.fill(bar + 7)
        self.orch.note(64, self.b(bar + 7, 3.5), 0.3, 120)
        return bar + 8

    def outro(self, bar):
        self.s.marker(self.b(bar), "outro")
        self.drums(bar, 3, crash_first=True, tamb=True, metal=True)
        self.riff(bar, 1)
        self.bass(bar + 2, RIFF[:8])
        # final cadence: C7#9 stab -> F hit with timpani, then let it ring
        self.stab.notes_at(CHORD["C7#9"], self.b(bar + 2, 3.0), 0.4, 120)
        self.bass(bar + 2, [(0, 3.0, 0.4, 118)], root=24)
        for t in (self.orch,):
            t.note(65, self.b(bar + 3), 1.2, 124)
        self.timp.note(41, self.b(bar + 3), 2.0, 127)
        self.bass(bar + 3, [(0, 0.0, 1.5, 124)])
        self.kick.hit("kick", self.b(bar + 3), 124)
        self.snare.hit("clap", self.b(bar + 3), 120).hit("snare", self.b(bar + 3), 124)
        self.cym.hit("crash", self.b(bar + 3), 118)
        return bar + 4


def compose() -> Song:
    a = Arranger()
    bar = a.intro(0)
    bar = a.verse(bar, 1)
    bar = a.pre(bar)
    bar = a.hook(bar)
    bar = a.verse(bar, 2)
    bar = a.pre(bar)
    bar = a.hook(bar)
    bar = a.breakdown(bar)
    bar = a.hook(bar, final=True, label="hook x2")
    bar = a.hook(bar, final=True, label="hook x2 (b)")
    bar = a.outro(bar)
    s = a.s
    for t in s.tracks.values():
        t.swing(SWING, grid=0.25)
    s.length_beats = s.bar(bar) + 2

    s.mix = {
        "tracks": {
            "kick": {"gain": -1, "eq": [("hpf", 30), ("bell", 80, -4, 2.5), ("bell", 55, 1.5, 1.0), ("bell", 3000, 3, 1.0)],
                     "comp": {"threshold": -16, "ratio": 4, "attack": 12, "release": 70}, "tape": {"drive_db": 7}},
            "snare": {"gain": -1, "eq": [("hpf", 120), ("bell", 220, 2, 1.0), ("bell", 5000, 2.5, 1.0)],
                      "tape": {"drive_db": 7}, "sends": {"gate": -3}},
            "hats": {"gain": -12, "eq": [("hpf", 500), ("hshelf", 8000, 2)], "pan": 0.3, "tape": {"drive_db": 5}},
            "perc": {"gain": -13, "eq": [("hpf", 400)], "pan": -0.35, "sends": {"plate": -16}},
            "toms": {"gain": -5, "eq": [("hpf", 60)], "width": 1.3, "sends": {"gate": -6}},
            "cymbals": {"gain": -12, "eq": [("hpf", 500)], "width": 1.2},
            "bass body": {"gain": -7.5, "eq": [("hpf", 32), ("bell", 120, 1.5, 1.0)],
                          "comp": {"threshold": -20, "ratio": 4, "attack": 8, "release": 90},
                          "tape": {"drive_db": 8}, "mono": True},
            "bass crunch": {"gain": -10.5, "eq": [("hpf", 40)],
                            "comp": {"threshold": -20, "ratio": 4, "attack": 8, "release": 90},
                            "tape": {"drive_db": 8}, "mono": True},
            "timpani": {"gain": -4.5, "eq": [("hpf", 60), ("bell", 3000, 2, 1.0)], "pan": -0.15,
                        "sends": {"hall": -8}},
            "bell": {"gain": -8.5, "eq": [("hpf", 400)], "width": 0.6, "pan": 0.3,
                     "sends": {"plate": -8, "dly": -14}},
            "stab": {"gain": -3.5, "eq": [("hpf", 180), ("bell", 350, -2, 1.0), ("bell", 2500, 2, 1.0)],
                     "comp": {"threshold": -20, "ratio": 3, "attack": 5, "release": 80},
                     "chorus": {"rate_hz": 0.5, "depth_ms": 2.0, "mix": 0.45}, "sends": {"plate": -10}},
            "stab hi": {"gain": -11, "eq": [("hpf", 400)], "chorus": {"mix": 0.25}, "width": 0.8,
                        "sends": {"plate": -8}},
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
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  bar {beat / 4:5.0f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
