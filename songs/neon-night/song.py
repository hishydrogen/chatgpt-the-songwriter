"""Neon Night (working title) - a vocaloid-style dance-pop song in the spirit of Tokyo
Manaka's "Doomer" (2025): 132 BPM, straight 16ths, F major with borrowed chords (Db, Bbm6),
house piano + supersaw stabs, FM slap bass, a self-made electronic kit and a sung
Japanese/English vocal (筆墨クミ UTAU voicebank through songwriter.voice).

Material (chords, riff, hook) lives here; `Arranger` turns a FORM into tracks.
The groove sketch (songs/neon-groove) reuses this module.
"""
from __future__ import annotations

import random

from songwriter.instruments import surge
from songwriter.song import Song, chord_notes, note_number

BPM = 132
PIANO = "piano.salamander"            # palette keys A: house piano
SAW = surge("Polysynths/Uni Saw FB")   # palette keys D: supersaw stab
BASS = surge("Basses/FM Slap")         # palette bass B
KIT = "drums.club"                     # self-made kit, grooves A + C
VOX = "voice.kumi"                     # palette voice A
VOX_OPTS = {"vibrato_cents": 28, "port_pre": 0.03, "port_post": 0.045, "consonant": 0.9}

# -- harmony ------------------------------------------------------------------
LOOP = ["Bbmaj7", "C", "Am7", "Dm7"]
CHORUS = ["Bbmaj7", "C", "Am7", "Dm7", "Gm7", "C/E", ("Fmaj7", "Dbmaj7"), ("Gm7", "C7sus4")]

# Riff: one rhythm, a top voice chosen per chord (index = hit), voiced downward from it.
RIFF_RHYTHM = [(0.0, 0.5), (0.75, 0.25), (1.5, 0.5), (2.5, 0.25), (3.0, 0.5)]
TOPS = {
    "Bbmaj7": ["D5", "C5", "D5", "F5", "C5"],
    "C": ["E5", "D5", "E5", "G5", "D5"],
    "C/E": ["E5", "D5", "E5", "G5", "E5"],
    "Am7": ["E5", "D5", "C5", "A4", "C5"],
    "Dm7": ["F5", "E5", "D5", "C5", "A4"],
    "Gm7": ["D5", "A4", "D5", "F5", "D5"],
    "Fmaj7": ["C5", "A4", "C5", "E5", "C5"],
    "F": ["C5", "A4", "C5", "F5", "C5"],
    "Dbmaj7": ["F5", "Eb5", "F5", "F5", "Eb5"],
    "C7sus4": ["F5", "C5", "F5", "C5", "Bb4"],
    "Bbm6": ["Db5", "C5", "Db5", "F5", "Db5"],
    "Ebmaj7": ["D5", "Bb4", "D5", "G5", "D5"],
}

# -- melody -------------------------------------------------------------------
# (pitch or "r", lyric, beats); one mora per note.
#   ロンリーナイト ネオンがにじむ / ひとりで踊る 終電のあと
#   大丈夫なんて 嘘ばっか / ねえ 誰か 気づいてよ
HOOK = [
    ("A4", "ろ", .5), ("A4", "ん", .25), ("C5", "り", .75), ("D5", "な", .5), ("C5", "い", .25),
    ("A4", "と", .75), ("r", "", .5), ("G4", "ね", .5),
    ("A4", "お", .5), ("G4", "ん", .25), ("G4", "が", .5), ("G4", "に", .5), ("A4", "じ", .5),
    ("G4", "む", 1.5), ("r", "", .25),
    ("C5", "ひ", .5), ("C5", "と", .25), ("D5", "り", .5), ("C5", "で", .5), ("A4", "お", .5),
    ("G4", "ど", .25), ("A4", "る", 1.0), ("r", "", .5),
    ("A4", "しゅ", .5), ("A4", "う", .25), ("C5", "で", .5), ("C5", "ん", .25), ("D5", "の", .5),
    ("E5", "あ", .5), ("D5", "と", 1.0), ("r", "", .5),
    ("D5", "だ", .5), ("C5", "い", .25), ("A4", "じょ", .5), ("A4", "う", .25), ("G4", "ぶ", .5),
    ("F4", "な", .5), ("G4", "ん", .25), ("A4", "て", 1.0), ("r", "", .25),
    ("G4", "う", .5), ("A4", "そ", .5), ("C5", "ば", .5), ("r", "", .25), ("C5", "か", .75),
    ("r", "", .5), ("D5", "ね", .5), ("C5", "え", .5),
    ("A4", "だ", .5), ("A4", "れ", .25), ("G4", "か", .5), ("F4", "き", .75),
    ("F4", "づ", .5), ("Ab4", "い", .5), ("F4", "て", 1.0),
    ("G4", "よ", 2.0), ("r", "", 2.0),
]

BASS_ROOT_OCT = 1   # roots in octave 1-2 (E1-D#2)


def root_of(name: str, tr: int = 0) -> int:
    """Bass root (slash bass if any) between E1 and D#2."""
    sym = name.split("/")[1] if "/" in name else name
    letter = sym[:2] if len(sym) > 1 and sym[1] in "#b" else sym[:1]
    n = note_number(f"{letter}1") + tr
    while n < note_number("E1"):
        n += 12
    while n > note_number("D#2"):
        n -= 12
    return n


def voicing(name: str, top: int, n: int = 3, tr: int = 0) -> list[int]:
    """Top note plus the n nearest chord tones below it (closed position, no semitone
    rubs between neighbours)."""
    base = name.split("/")[0]
    pcs = {(p + tr) % 12 for p in chord_notes(base, 4)}
    out, p = [top], top - 1
    while len(out) < n + 1 and p > top - 14:
        if p % 12 in pcs and p % 12 != top % 12 and out[-1] - p != 1:
            out.append(p)
        p -= 1
    return sorted(out)


class Arranger:
    def __init__(self, form, title="Neon Night"):
        """form: [(section name, progression (one entry per bar; tuple = two half-bar
        chords), transpose)]"""
        s = self.s = Song(title, bpm=BPM, key="F")
        self.rng = random.Random(2025)
        self.kick = s.track("kick", KIT)
        self.clap = s.track("clap", KIT)
        self.hats = s.track("hats", KIT)
        self.perc = s.track("perc", KIT)
        self.cym = s.track("cymbals", KIT)
        self.piano = s.track("piano", PIANO)
        self.saw = s.track("saw", SAW)
        self.bass = s.track("bass", BASS)
        self.vox = s.track("vocal", VOX)
        self.vox.opts.update(VOX_OPTS)
        self.sec, self.timeline, bar = {}, [], 0
        for name, prog, tr in form:
            self.sec[name] = (bar, len(prog), tr)
            for i, entry in enumerate(prog):
                b0 = s.bar(bar + i)
                if isinstance(entry, tuple):
                    self.timeline += [(b0, b0 + 2, entry[0], tr), (b0 + 2, b0 + 4, entry[1], tr)]
                else:
                    self.timeline.append((b0, b0 + 4, entry, tr))
            s.marker(s.bar(bar), name)
            bar += len(prog)
        self.total_bars = bar

    # -- lookup ------------------------------------------------------------------
    def chord_at(self, beat):
        for st, en, name, tr in self.timeline:
            if st <= beat + 1e-6 < en:
                return st, en, name, tr
        return self.timeline[-1]

    def span(self, name):
        b0, n, tr = self.sec[name]
        return self.s.bar(b0), n, tr

    def T(self, beat, sd=3.0):
        return max(0.0, beat + self.rng.gauss(0, sd) / 1000 * BPM / 60)

    def V(self, vel, spread=4):
        return int(max(1, min(127, vel + self.rng.randint(-spread, spread))))

    # -- drums ---------------------------------------------------------------------
    def drums_house(self, b0, bars, fill=True, crash=True, vel=1.0):
        """Groove A: four on the floor, clap+snare on 2 and 4, 16th hats, open hat on the &."""
        for bar in range(bars):
            b = b0 + bar * 4
            last = fill and bar == bars - 1
            for k in range(4):
                self.kick.hit("kick", b + k, self.V(118 * vel, 2))
            for k in (1, 3):
                self.clap.hit("clap", b + k, self.V(112 * vel, 3))
                self.clap.hit("snare", b + k, self.V(86 * vel, 3))
            for i in range(16):
                p = i * 0.25
                if last and p >= 3:
                    break
                if i % 4 == 2:
                    self.hats.hit("hh_open", b + p, self.V(90 * vel))
                else:
                    self.hats.hit("hh_closed", b + p, self.V((96, 58, 0, 66)[i % 4] * vel))
            self.perc.hit("shaker", b + 1.75, self.V(64 * vel))
            self.perc.hit("shaker", b + 3.75, self.V(64 * vel))
            if last:
                self.fill(b + 3)
        if crash:
            self.cym.hit("crash", b0, 104)

    def drums_dance(self, b0, bars, fill=True, crash=True, vel=1.0):
        """Groove C: syncopated punch kick, clap+snare backbeat, 16th hats with accents."""
        for bar in range(bars):
            b = b0 + bar * 4
            last = fill and bar == bars - 1
            kicks = (0, 1.5, 2, 3.5) if bar % 2 == 0 else (0, 1.5, 2.25, 3)
            for k in kicks:
                if last and k >= 3:
                    continue
                self.kick.hit("kick_punch", b + k, self.V((120 if k in (0, 2) else 106) * vel, 2))
            for k in (1, 3):
                if last and k == 3:
                    continue
                self.clap.hit("clap", b + k, self.V(114 * vel, 3))
                self.clap.hit("snare", b + k, self.V(92 * vel, 3))
            if bar % 2 == 1:
                self.clap.hit("snare", b + 3.75, self.V(54 * vel))   # ghost
            for i in range(16):
                p = i * 0.25
                if last and p >= 3:
                    break
                if i in (6, 14) and bar % 2 == 1:
                    self.hats.hit("hh_open", b + p, self.V(84 * vel))
                else:
                    self.hats.hit("hh_closed", b + p, self.V((100, 62, 84, 70)[i % 4] * vel))
            self.perc.hit("rim", b + 2.75, self.V(70 * vel))
            if last:
                self.fill(b + 3, toms=True)
        if crash:
            self.cym.hit("crash", b0, 104)

    def fill(self, b, toms=False):
        """One-beat fill into the next section (different each call)."""
        k = self.rng.randint(0, 2)
        if toms:
            for i, (t, d) in enumerate([("tom_high", 0), ("tom_high", .25), ("tom_mid", .5), ("tom_low", .75)]):
                self.perc.hit(t, b + d, self.V(100 + 4 * i))
        elif k == 0:
            for i in range(4):
                self.clap.hit("snare", b + i * 0.25, self.V(70 + 12 * i))
        elif k == 1:
            for i in range(8):
                self.clap.hit("snare", b + i * 0.125, self.V(56 + 8 * i))
        else:
            for d, v in ((0, 100), (0.5, 96), (0.75, 110)):
                self.clap.hit("clap", b + d, self.V(v))
        self.kick.hit("kick", b, 112)

    # -- bass ------------------------------------------------------------------------
    def _bass_note(self, beat, dur, vel, octave=0, look=False):
        st, en, name, tr = self.chord_at(beat + (0.25 if look else 0))
        self.bass.note(root_of(name, tr) + 12 * octave, self.T(beat, 2), dur, self.V(vel))

    def bass_house(self, b0, bars):
        """Off-beat house bass with octave hops."""
        for bar in range(bars):
            b = b0 + bar * 4
            for k in range(4):
                self._bass_note(b + k, 0.2, 96)
                self._bass_note(b + k + 0.5, 0.3, 110, octave=1 if k % 2 else 0)

    def bass_sync(self, b0, bars):
        """3-3-2 syncopation, octave pops, a 16th push into each bar."""
        pat = [(0, .5, 112, 0), (.75, .5, 100, 0), (1.5, .25, 104, 1), (2.0, .25, 90, 0),
               (2.5, .5, 108, 0), (3.25, .25, 96, 1), (3.75, .25, 100, 0)]
        for bar in range(bars):
            b = b0 + bar * 4
            for p, d, v, o in pat:
                self._bass_note(b + p, d, v, o, look=(p == 3.75))

    def bass_funk(self, b0, bars):
        """16th slap: thumb roots, popped octaves, dead-note ghosts."""
        pat = [(0, .4, 116, 0), (.5, .2, 104, 1), (.75, .2, 70, 0), (1.25, .2, 96, 0),
               (1.5, .25, 108, 1), (2.0, .3, 110, 0), (2.5, .2, 102, 1), (2.75, .15, 64, 0),
               (3.0, .3, 106, 0), (3.5, .2, 100, 1), (3.75, .2, 92, 0)]
        for bar in range(bars):
            b = b0 + bar * 4
            for p, d, v, o in pat:
                self._bass_note(b + p, d, v, o, look=(p == 3.75))

    # -- keys -------------------------------------------------------------------------
    def riff(self, b0, bars, piano=True, saw=True, pickups=True, vel=1.0, saw_vel=0.85):
        """The face of the song: tresillo house-piano riff, top voice from TOPS per chord."""
        for bar in range(bars):
            b = b0 + bar * 4
            hits = list(RIFF_RHYTHM)
            if pickups and bar % 2 == 1:
                hits.append((3.75, 0.25))
            for idx, (p, d) in enumerate(hits):
                look = p == 3.75
                st, en, name, tr = self.chord_at(b + p + (0.25 if look else 0))
                tops = TOPS[name.split("/")[0] if name not in TOPS else name]
                top = note_number(tops[0 if look else idx]) + tr
                notes = voicing(name, top, 3, tr)
                v = (104, 86, 98, 90, 96, 92)[idx]
                t = self.T(b + p, 3)
                if piano:
                    self.piano.notes_at(notes, t, d * 0.95, self.V(v * vel))
                if saw:
                    self.saw.notes_at(notes, t, d * 0.8, self.V(v * vel * saw_vel))

    def saw_pump(self, b0, bars, vel=1.0):
        """Supersaw chords on every 8th (sidechained in the mix), held across changes."""
        for bar in range(bars):
            b = b0 + bar * 4
            for k in range(8):
                p = b + k * 0.5
                st, en, name, tr = self.chord_at(p)
                tops = TOPS.get(name, TOPS[name.split("/")[0]])
                notes = voicing(name, note_number(tops[0]) + tr, 3, tr)
                self.saw.notes_at(notes, p, 0.42, self.V((100, 84)[k % 2] * vel))

    def piano_funk(self, b0, bars, vel=1.0):
        """16th comping: short chords on syncopations, ghost hits, top voice from TOPS."""
        pat = [(0, .2, 100, 0), (.5, .15, 70, 0), (.75, .2, 96, 1), (1.25, .15, 66, 1),
               (1.5, .3, 98, 2), (2.25, .2, 92, 3), (2.75, .15, 68, 3), (3.0, .3, 100, 4),
               (3.5, .15, 72, 4)]
        for bar in range(bars):
            b = b0 + bar * 4
            for p, d, v, i in pat:
                st, en, name, tr = self.chord_at(b + p)
                tops = TOPS.get(name, TOPS[name.split("/")[0]])
                notes = voicing(name, note_number(tops[i]) + tr, 3, tr)
                self.piano.notes_at(notes, self.T(b + p, 3), d, self.V(v * vel))

    def saw_stabs(self, b0, bars, vel=1.0):
        """Accent stabs on the & of 2 and the e of 4 (answers the kick pattern)."""
        for bar in range(bars):
            b = b0 + bar * 4
            for p, d in ((1.5, .3), (3.25, .2), (3.5, .4)):
                st, en, name, tr = self.chord_at(b + p)
                tops = TOPS.get(name, TOPS[name.split("/")[0]])
                notes = voicing(name, note_number(tops[3]) + tr, 3, tr)
                self.saw.notes_at(notes, b + p, d, self.V(104 * vel))

    # -- vocal ------------------------------------------------------------------------
    def sing(self, b0, melody, tr=0, x=None):
        b = b0
        for p, lyr, d in melody:
            if p != "r":
                self.vox.note(note_number(p) + tr, b, d, 100, lyric=lyr, x=dict(x) if x else None)
            b += d
        return b

    # -- mix --------------------------------------------------------------------------
    def mix(self):
        self.s.mix = {
            "tracks": {
                "kick": {"gain": -6.5, "eq": [("hpf", 30), ("bell", 3500, 2, 1.0)]},
                "clap": {"gain": -9, "eq": [("hpf", 160), ("bell", 1200, 1.5, 1.0)], "sends": {"room": -10}},
                "hats": {"gain": -15, "eq": [("hpf", 450)], "pan": 0.18},
                "perc": {"gain": -20, "eq": [("hpf", 120)], "pan": -0.25, "sends": {"room": -12}},
                "cymbals": {"gain": -16, "eq": [("hpf", 600)], "width": 1.2},
                "piano": {"gain": -5.5, "eq": [("hpf", 160), ("bell", 320, -3, 1.0), ("hshelf", 6000, 2)],
                          "comp": {"threshold": -20, "ratio": 3, "attack": 8, "release": 90},
                          "width": 0.6, "mono_below": 200, "sends": {"plate": -16}},
                "saw": {"gain": -8.5, "eq": [("hpf", 220), ("bell", 450, -2, 1.0)], "width": 1.0,
                        "duck": {"by": "kick", "depth": 5, "release_ms": 140}, "sends": {"plate": -18}},
                "bass": {"gain": -5.5, "eq": [("hpf", 32), ("bell", 90, 1.5, 1.0)],
                         "comp": {"threshold": -20, "ratio": 4, "attack": 6, "release": 80},
                         "duck": {"by": "kick", "depth": 3}, "mono": True},
                "vocal": {"gain": 0.5, "eq": [("hpf", 140), ("bell", 280, -2.5, 1.0), ("bell", 3200, 2, 1.0),
                                             ("hshelf", 9000, 1.5)],
                          "comp": {"threshold": -22, "ratio": 3.5, "attack": 4, "release": 70},
                          "sends": {"plate": -11, "dly": -18}},
            },
            "fx": {
                "plate": {"type": "reverb", "kind": "plate", "decay": 1.7, "predelay": 25, "hpf": 300, "lpf": 9000},
                "room": {"type": "reverb", "kind": "room", "decay": 0.7, "predelay": 5, "hpf": 250, "lpf": 8000},
                "dly": {"type": "delay", "beats": 0.75, "feedback": 0.32, "hpf": 600, "lpf": 5000},
            },
            "master": {"glue": {"threshold": -16, "ratio": 2, "attack": 20, "release": 200}, "target_lufs": -14},
        }


def compose() -> Song:
    raise NotImplementedError("full arrangement comes after the groove sketch (songs/neon-groove)")
