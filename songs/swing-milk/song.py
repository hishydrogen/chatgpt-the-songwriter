"""Swing, Milk! -- the approved final original scat-jazz arrangement.

The user chose A for verses and B for choruses, Milk, Splendid Steinway,
upright bass and DRSKit, and a definite ensemble ending. The audition's
performances supply the groove vocabulary; melodies, orchestration, fills,
two-bar trading, the modulation and the ending develop it into a song.
"""
from __future__ import annotations

import bisect
import copy
import importlib.util
from pathlib import Path

import mido

from songwriter.song import note_number as N

_spec = importlib.util.spec_from_file_location(
    "chosen_grooves", Path(__file__).resolve().parents[1] / "scat-jazz-groove/song.py")
groove = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(groove)
BPM, SWING = groove.BPM, groove.SWING
HOOK = groove.HOOK
performed, velocity = groove.performed, groove.velocity
VOICE_LABEL = "scat - Milk"
SELECTED = groove.SELECTED
TITLE = "Swing, Milk!"

# Symbol, low root, rootless voicing and allowed melodic tones. The minor-IV
# colour and altered dominants belong to the original audition's harmony.
CHORDS = {
    "Fmaj9": ("F1", ["A3", "C4", "E4", "G4"], {0, 4, 5, 7, 9}),
    "D7b9": ("D2", ["F#3", "C4", "Eb4", "A4"], {0, 2, 3, 6, 9}),
    "Gm9": ("G1", ["Bb3", "D4", "F4", "A4"], {2, 5, 7, 9, 10}),
    "C13": ("C2", ["Bb3", "D4", "E4", "A4"], {0, 2, 4, 7, 9, 10}),
    "Am7": ("A1", ["G3", "C4", "E4", "A4"], {0, 4, 7, 9}),
    "Bbm6": ("Bb1", ["Db4", "F4", "G4", "Bb4"], {1, 5, 7, 10}),
    "F6/9": ("F1", ["A3", "D4", "G4", "C5"], {0, 2, 5, 7, 9}),
    "Dm9": ("D2", ["F3", "C4", "E4", "A4"], {0, 2, 4, 5, 9}),
    "Bbmaj9": ("Bb1", ["D4", "F4", "A4", "C5"], {0, 2, 5, 9, 10}),
    "D13": ("D2", ["F#3", "C4", "E4", "B4"], {0, 2, 4, 6, 9, 11}),
}
MODULATED = {"Fmaj9": "Gmaj9", "D7b9": "E7b9", "Gm9": "Am9", "C13": "D13",
             "Am7": "Bm7", "Bbm6": "Cm6", "F6/9": "G6/9"}
SPECIAL = {
    "turn": ["Gm9", "C13"],
    "lift": ["Am7", "D7b9", "Gm9", "C13"],
    "bridge": ["Dm9", "Dm9", "Gm9", "C13", "Bbmaj9", "Bbm6", "Am7", "D13"],
    "tag": ["Gm9", "C13", "Fmaj9", "Bbm6"],
    "ending": ["Gm9", "C13", "F6/9", "F6/9"],
}

# name, bars, section kind, chosen groove, transpose, performance energy.
FORM = [
    ("intro", 4, "intro", "A", 0, .76),
    ("verse 1", 16, "verse", "A", 0, .85),
    ("lift 1", 4, "lift", "A", 0, .94),
    ("chorus 1", 8, "chorus", "B", 0, 1.00),
    ("turnaround", 2, "turn", "A", 0, .78),
    ("verse 2", 16, "verse", "A", 0, .94),
    ("lift 2", 4, "lift", "A", 0, 1.00),
    ("chorus 2", 8, "chorus", "B", 0, 1.03),
    ("bridge", 8, "bridge", "A", 0, .79),
    ("scat and tenor trading", 8, "trading", "A", 2, .96),
    ("final chorus", 16, "chorus", "B", 2, 1.06),
    ("scat tag", 4, "tag", "B", 2, .99),
    ("ensemble ending", 4, "ending", "B", 2, .92),
]

# Each entry is a written bar: offset, pitch, duration, scat syllable. These
# lighter verse sentences differ from the audition's busier chorus hook.
VERSE_A = [
    [(.5,"C4",.36,"ど"),(1,"E4",.40,"び"),(1.5,"G4",.55,"だ"),(2.5,"E4",.60,"ぶ")],
    [(0,"D4",.70,"ど"),(1,"F#4",.55,"び"),(2,"A4",.80,"ば"),(3,"F#4",.40,"だ")],
    [(.5,"D4",.40,"ど"),(1,"F4",.45,"び"),(1.5,"A4",.70,"だ"),(2.5,"G4",.65,"ぶ")],
    [(.5,"E4",.60,"ど"),(1.5,"G4",.45,"び"),(2,"A4",.70,"ば"),(3,"E4",.40,"だ")],
    [(.5,"C4",.40,"ど"),(1,"E4",.40,"び"),(1.5,"G4",.35,"だ"),(2,"F#4",.70,"ば"),(3,"D4",.45,"ど")],
    [(.5,"Bb4",.40,"び"),(1,"A4",.60,"ば"),(2,"G4",.50,"ど"),(3,"E4",.45,"だ")],
    [(.5,"E4",.65,"ど"),(1.5,"G4",.38,"び"),(2,"F4",.75,"ば"),(3,"Db4",.40,"だ")],
    [(.5,"D4",.40,"ど"),(1,"F4",.35,"び"),(2,"E4",.70,"ば"),(3,"G4",.40,"ど"),(3.5,"F4",.36,"だ")],
]
VERSE_B = [
    [(.5,"E4",.36,"ど"),(1,"G4",.40,"び"),(1.5,"A4",.64,"だ"),(2.5,"G4",.33,"ば"),(3,"E4",.38,"ど")],
    [(0,"F#4",.48,"ど"),(.5,"A4",.32,"び"),(1.5,"F#4",.64,"だ"),(2.5,"Eb4",.65,"ぶ")],
    [(.5,"F4",.33,"ど"),(1,"G4",.34,"び"),(1.5,"A4",.65,"だ"),(2.5,"Bb4",.34,"ば"),(3,"A4",.38,"ど")],
    [(0,"G4",.52,"ど"),(1,"A4",.66,"ば"),(2,"G4",.38,"だ"),(2.5,"E4",.66,"ー")],
    [(.5,"E4",.40,"ど"),(1,"G4",.35,"び"),(1.5,"A4",.35,"だ"),(2,"F#4",.65,"ば"),(3,"Eb4",.40,"ぶ")],
    [(0,"G4",.55,"ど"),(1,"Bb4",.55,"ば"),(2,"A4",.35,"だ"),(2.5,"G4",.34,"び"),(3,"E4",.40,"ど")],
    [(0,"A4",.68,"ば"),(1,"G4",.65,"ー"),(2,"Bb4",.35,"ど"),(2.5,"G4",.35,"び"),(3,"F4",.38,"だ")],
    [(0,"G4",.65,"ど"),(1,"A4",.35,"び"),(1.5,"F4",.34,"だ"),(2,"E4",.45,"ば"),(3.5,"F4",.38,"だ")],
]
LIFT = [
    [(.5,"E4",.40,"ど"),(1,"G4",.40,"び"),(1.5,"A4",.85,"ば"),(3,"G4",.50,"だ")],
    [(.5,"D4",.30,"ど"),(1,"F#4",.40,"び"),(1.5,"A4",.65,"だ"),(2.5,"F#4",.40,"ば"),(3,"A4",.70,"だ")],
    [(0,"Bb4",.70,"ば"),(1,"A4",.40,"び"),(1.5,"G4",.65,"ど"),(2.5,"F4",.65,"ぶ")],
    [(0,"E4",.40,"ど"),(.5,"G4",.35,"び"),(1,"A4",.80,"ば"),(2,"G4",.40,"だ"),(2.5,"E4",.35,"ど"),(3,"D4",.30,"び"),(3.5,"G4",.30,"ば")],
]
BRIDGE = [
    [(0,"F4",1.25,"ば"),(1.5,"E4",.50,"び"),(2.5,"D4",.85,"ど")],
    [(.5,"A4",1.50,"ば"),(2.5,"F4",.55,"だ"),(3.5,"E4",.30,"ぶ")],
    [(0,"G4",1.30,"ど"),(1.5,"A4",.40,"び"),(2.5,"Bb4",.80,"ば")],
    [(.5,"A4",.85,"ば"),(1.5,"G4",.45,"だ"),(2.5,"E4",.85,"ぶ")],
    [(0,"F4",.80,"ど"),(1,"A4",.60,"び"),(2,"C5",.80,"ば"),(3,"A4",.55,"だ")],
    [(.5,"Bb4",.65,"ば"),(1.5,"G4",.55,"だ"),(2.5,"F4",.80,"ぶ")],
    [(0,"E4",.60,"ど"),(1,"G4",.45,"び"),(1.5,"A4",.80,"ば"),(3,"G4",.50,"だ")],
    [(0,"F#4",.50,"ど"),(1,"A4",.40,"び"),(1.5,"B4",.70,"ば"),(2.5,"A4",.35,"だ"),(3,"F#4",.40,"ど"),(3.5,"A4",.30,"ば")],
]
TAG = [
    [(0,"G4",.65,"ど"),(1,"A4",.35,"び"),(1.5,"Bb4",.80,"ば"),(3,"A4",.45,"だ")],
    [(0,"G4",.40,"ど"),(.5,"A4",.35,"び"),(1,"E4",.65,"だ"),(2,"G4",.80,"ば"),(3,"E4",.45,"ど")],
    [(.5,"C4",.35,"ど"),(1,"E4",.40,"び"),(1.5,"G4",.40,"だ"),(2,"A4",.90,"ば")],
    [(0,"Bb4",.70,"ば"),(1,"G4",.45,"だ"),(2,"F4",.60,"ぶ"),(3,"Db4",.55,"ど")],
]
TENOR_TRADING = {
    2: [(0,"D4",.40),(.5,"F4",.35),(1,"G4",.70),(2,"Bb4",.40),(2.5,"A4",.38),(3,"G4",.35),(3.5,"F4",.40)],
    3: [(.5,"E4",.30),(1,"G4",.50),(2,"A4",.60),(3,"G4",.35),(3.5,"E4",.40)],
    6: [(0,"A4",.60),(1,"G4",.55),(2,"Bb4",.35),(2.5,"G4",.40),(3,"F4",.30),(3.5,"Db4",.30)],
    7: [(0,"D4",.40),(.5,"F4",.35),(1,"A4",.40),(1.5,"G4",.30),(2,"E4",.30),(2.5,"G4",.35),(3,"A4",.30),(3.5,"C5",.45)],
}


class SwingSong(groove.palette.PaletteSong):
    def full_midi(self):
        mf=super().full_midi()
        conductor=mf.tracks[0]
        events=[]
        tick=0
        for msg in conductor:
            tick+=msg.time
            if msg.type!="end_of_track":
                events.append((tick,msg.copy(time=0)))
        events.extend([(0,mido.MetaMessage("key_signature",key="F",time=0)),
                       (280*self.TPB,mido.MetaMessage("key_signature",key="G",time=0)),
                       (0,mido.MetaMessage("text",text="Swing eighths 60:40. Verse=A; chorus=B.",time=0))])
        conductor.clear()
        prev=0
        for tick,msg in sorted(events,key=lambda e:e[0]):
            conductor.append(msg.copy(time=tick-prev))
            prev=tick
        return mf


class Arrangement(groove.Sketch):
    def __init__(self):
        super().__init__()
        # Preserve the chosen strips/tracks while adding a DAW conductor with
        # the section markers and the actual F-to-G key change.
        old=self.s
        self.s=SwingSong(TITLE,bpm=BPM,key="F")
        self.s.tracks=old.tracks
        for t in self.s.tracks.values():
            t.song=self.s
        self.score_events = []
        self.timeline = []
        self.templates = {}
        for style in ("A", "B"):
            k = groove.Sketch()
            k.arrange(0, style)
            self.templates[style] = k.s
        self.lead = self.voice_track(VOICE_LABEL, 10, -3.5, 0)
        self.harmonies = [self.voice_track("Milk harmony left", 11, -17, -.34),
                          self.voice_track("Milk harmony right", 12, -17, .34)]
        for t in self.harmonies:
            t.opts.update(breath_db=None, breathy=.025, vibrato_cents=12, jitter=.20)

    def voice_track(self, name, channel, gain, pan):
        t = self.track(name, SELECTED["voice"], channel, gain,
                       eq=[("hpf", 125), ("bell", 280, -2.5, .9), ("bell", 750, -2, .9),
                           ("bell", 3200, 2, .7), ("hshelf", 9000, 1.5, .7)],
                       comp={"threshold": -20, "ratio": 2.5, "attack": 10, "release": 90},
                       pan=pan, sends={"plate": -15 if channel == 10 else -12,
                                       "slap": -23 if channel == 10 else -30})
        t.opts.update(groove.palette.VOICE_OPTS, formant=0)
        return t

    def prepare_form(self):
        for name, bars, kind, style, tr, energy in FORM:
            start = self.section(name, bars, kind)
            sec = self.sections[-1]
            sec.update(name=name, kind=kind, groove=style, transpose=tr, energy=energy)
            if kind in SPECIAL:
                changes = [(4 * i, c) for i, c in enumerate(SPECIAL[kind])]
            else:
                changes = [(chunk + b, c) for chunk in range(0, bars * 4, 32)
                           for b, c, _, _ in groove.HARMONY if chunk + b < bars * 4]
            for local, symbol in changes:
                self.timeline.append((start + local, symbol, tr))
        self.timeline.sort()
        self.chord_beats = [b for b, _, _ in self.timeline]

    def chord(self, beat):
        _, symbol, tr = self.timeline[max(0, bisect.bisect_right(self.chord_beats, beat + 1e-7) - 1)]
        root, voicing, pcs = CHORDS[symbol]
        return {"symbol": MODULATED.get(symbol, symbol) if tr == 2 else symbol,
                "source": symbol, "transpose": tr, "root": N(root) + tr,
                "voicing": [N(p) + tr for p in voicing], "pcs": {(p + tr) % 12 for p in pcs}}

    def record(self, track, pitch, nominal, dur, vel=80, lyric=None, x=None):
        role = "voice" if track.instrument.startswith("voice.") else "sax" if track is self.sax else "piano"
        self.score_events.append({"track": track.name, "beat": nominal, "pitch": N(pitch),
                                  "duration": dur, "chord": self.chord(nominal)["symbol"]})
        track.note(pitch, performed(nominal, role), dur, velocity(vel, nominal), lyric=lyric, x=x)

    def copy_band(self, sec):
        template = self.templates[sec["groove"]]
        start, total, tr = sec["beat"], sec["bars"] * 4, sec["transpose"]
        for chunk in range(0, total, 32):
            available = min(32, total - chunk)
            energy = sec["energy"] * (1.035 if chunk and sec["kind"] == "verse" else 1)
            for name, src in template.tracks.items():
                t = self.s.tracks[name]
                if sec["kind"] in ("intro", "turn") and (t in self.horns or t is self.sax or t is self.riff):
                    continue
                if sec["name"] == "verse 1" and chunk == 0 and (t in self.horns or t is self.sax):
                    continue
                if sec["kind"] == "trading" and t is self.sax:
                    continue
                for n in src.notes:
                    if n.start >= available-.03:
                        continue
                    if sec["name"] == "verse 1" and chunk == 0 and t is self.kit["toms"] and n.start < 16:
                        continue
                    nn = copy.deepcopy(n)
                    nn.start += start + chunk
                    if not t.instrument.startswith("drums."):
                        nn.pitch += tr
                    nn.vel = max(1, min(127, round(nn.vel * energy)))
                    # Tiny deterministic variations belong to a performance,
                    # while written syncopations and beat accents stay intact.
                    drift = ((round(n.start * 1000) + round(start) * 7) % 7 - 3) * BPM / 60000
                    nn.start = max(start + chunk, nn.start + drift)
                    t.notes.append(nn)
                t.ccs.extend((start + chunk + b, cc, v) for b, cc, v in src.ccs if b < available)
                t.bends.extend((start + chunk + b, v) for b, v in src.bends if b < available)
        # End each section's pedal explicitly, including a clipped intro.
        self.piano.cc(64, 0, start + total - .02)

    def special_band(self, sec):
        start, bars, tr, kind = sec["beat"], sec["bars"], sec["transpose"], sec["kind"]
        # The selected A/B drum vocabulary continues underneath new harmony.
        template = self.templates[sec["groove"]]
        for name, src in template.tracks.items():
            if not src.instrument.startswith("drums."):
                continue
            t = self.s.tracks[name]
            for n in src.notes:
                if n.start >= bars * 4-.03:
                    continue
                if kind == "ending" and n.start >= 8-.03:
                    continue
                nn = copy.deepcopy(n)
                nn.start += start
                nn.vel = max(1, round(nn.vel * sec["energy"]))
                t.notes.append(nn)
        lines = {
            "turn": [["G1","Bb1","D2","Db2"],["C2","E2","G1","E1"]],
            "lift": [["A1","C2","E2","G1"],["D2","F#2","A1","F#1"],
                     ["G1","Bb1","D2","Db2"],["C2","E2","G1","E1"]],
            "bridge": [["D2","F2","A1","C2"],["D2","A1","C2","F#1"],
                       ["G1","Bb1","D2","Db2"],["C2","E2","G1","A1"],
                       ["Bb1","D2","F2","A1"],["Bb1","Db2","F2","Ab1"],
                       ["A1","C2","E2","C#2"],["D2","F#2","A1","F#1"]],
            "tag": [["G1","Bb1","D2","Db2"],["C2","E2","G1","E1"],
                    ["F1","A1","C2","A1"],["Bb1","Db2","F2","F#1"]],
            "ending": [["G1","Bb1","D2","Db2"],["C2","E2","G1","E1"]],
        }
        for bar in range(bars):
            if kind == "ending" and bar >= 2:
                break
            b = start + bar * 4
            chord = self.chord(b)
            for j, p in enumerate(lines[kind][bar]):
                pos = j if sec["groove"] == "A" else (0, 1.5, 2, 3.25)[j]
                self.bass.note(N(p) + tr, b + performed(pos, "bass"), .72 if j % 2 == 0 else .55,
                               velocity(round((92 if j % 2 == 0 else 77) * sec["energy"]), b + pos))
            pattern = [(0,.28),(1.5,.24),(2.5,.28)] if sec["groove"] == "A" else [(0,.24),(.75,.16),(1.5,.23),(2.5,.25),(3.25,.16)]
            for pos, dur in pattern:
                for j, pitch in enumerate(chord["voicing"]):
                    onset = b + performed(pos, "piano") + j * .007
                    self.piano.note(pitch, onset, dur - j * .007,
                                    velocity(round((70 if pos != .75 else 53) * sec["energy"]), b + pos, j))
                self.piano.sustain(b + pos + .04, b + pos + dur)
            for pos in (1, 3) if sec["groove"] == "A" else (.5,1.5,2.5,3.5):
                self.guitar.notes_at(chord["voicing"][:2], b + performed(pos,"guitar"), .13,
                                     velocity(round(59 * sec["energy"]), b+pos), strum=.014)
            if kind != "turn" and (bar % 2 or kind in ("lift", "tag")):
                self.horn_chord(b + 3.36, .25, 70 if kind == "bridge" else 80)
        self.bass.cc(11, 108, start)
        self.piano.cc(64, 0, start + bars * 4 - .02)

    def horn_chord(self, beat, dur, vel):
        chord = self.chord(beat)
        v = chord["voicing"]
        for j, (t, pitch) in enumerate(zip(self.horns, (v[0]-12, v[1]-12, v[-1]-12))):
            self.record(t, pitch, beat + j*.006, dur, vel+j*2)
            t.cc_ramp(11, beat, beat + min(.25, dur), 79, 109, step=.06)

    def sing_lines(self, sec, lines, bar_offset=0, backing=False, gain=0):
        # WORLD uses per-note gain; MIDI singers get the corresponding section
        # expression on the independent vocal channel as well.
        self.lead.cc(11,round(90*10**(gain/20)),sec["beat"]+bar_offset*4)
        for bar, line in enumerate(lines):
            for j, (pos, pitch, dur, syllable) in enumerate(line):
                nominal = sec["beat"] + (bar + bar_offset) * 4 + pos
                pitch = N(pitch) + sec["transpose"]
                x = {"vib": .70 if dur > .65 else 0, "scoop": .55 if j == 0 else 0,
                     "fall": .45 if j == len(line)-1 else 0, "gain_db": gain}
                self.record(self.lead, pitch, nominal, dur, 99 if dur > .5 else 92, syllable, x)
                if dur > .65:
                    self.lead.vibrato(performed(nominal,"voice")+.38,
                                      performed(nominal,"voice")+dur-.04, rate_hz=5.2, cents=12)
                if backing and (dur >= .6 or j == 0):
                    pcs = self.chord(nominal)["pcs"]
                    candidates = [p for p in range(max(55, pitch-7), pitch-2) if p%12 in pcs]
                    hp = max(candidates) if candidates else pitch-12
                    for k, t in enumerate(self.harmonies):
                        self.record(t, hp, nominal + (0.018 if k else .005) * BPM / 60,
                                    max(.14, dur-.04), 89, syllable,
                                    {"vib": .5 if dur > .65 else 0, "scoop": .25 if j == 0 else 0,
                                     "fall": .25 if j == len(line)-1 else 0})

    def melodic_answers(self, sec):
        # Verse breath spaces get longer replies than the hook audition did.
        if sec["kind"] == "verse":
            for bar in (1, 3, 9, 11):
                b = sec["beat"] + bar * 4
                chord = self.chord(b+3.45)
                tones = sorted(p for p in range(62, 73) if p%12 in chord["pcs"])
                for j, p in enumerate(tones[-3:]):
                    self.record(self.riff, p, b + 3.42 + j*.17, .12, 75+j*3)
        if sec["kind"] in ("intro", "turn"):
            for bar in range(sec["bars"]):
                b = sec["beat"] + bar*4
                chord = self.chord(b)
                tones = chord["voicing"][-3:]
                for j, p in enumerate(tones):
                    self.record(self.riff, p, b + .5 + j*.5, .32 if j<2 else .58, 81+j*2)
                self.horn_chord(b + 3.37, .22, 70)
        if sec["kind"] == "chorus" and sec["name"] != "chorus 1":
            for off in range(0, sec["bars"]*4, 32):
                for pos in (10.98, 25.73):
                    self.horn_chord(sec["beat"] + off + pos, .17, 81 if sec["transpose"] == 0 else 87)

    def add_transition(self, sec, index):
        if sec["kind"] not in ("verse", "lift", "bridge"):
            return
        end = sec["beat"] + sec["bars"]*4
        # Replace, rather than stack on, the last beat's existing fill.
        for part in ("snare", "toms"):
            self.kit[part].notes = [n for n in self.kit[part].notes if not end-1 <= n.start < end]
        fills = [
            [(-.90,"snare",59),(-.65,"tom_high",66),(-.40,"tom_mid",72),(-.16,"tom_low",80)],
            [(-.90,"snare",65),(-.67,"snare",39),(-.40,"tom_high",74),(-.14,"tom_low",84)],
            [(-.88,"tom_high",65),(-.62,"tom_mid",72),(-.35,"tom_low",80),(-.12,"snare",76)],
        ][index%3]
        for rel, name, v in fills:
            part = "snare" if name == "snare" else "toms"
            self.hit(part, name, 0, end+rel, v)
        self.kit["cymbals"].hit("crash_tip", end + .006, 69 if sec["kind"] == "verse" else 79, .20)

    def trading(self, sec):
        calls = [HOOK[0], HOOK[1], [], [], HOOK[4], HOOK[5], [], []]
        self.sing_lines(sec, calls)
        for bar, line in TENOR_TRADING.items():
            b = sec["beat"] + bar*4
            self.sax.cc(64, 127, b)
            self.sax.cc(80, 13, b)
            self.sax.bend(-650, b)
            self.sax.bend(0, b+.15)
            for j, (pos,pitch,dur) in enumerate(line):
                self.record(self.sax, N(pitch)+sec["transpose"], b+pos, dur, 91 if j%3 else 99)
            self.sax.cc_ramp(11,b,b+3.78,80,111,step=.14)
            self.sax.cc(64,0,b+3.97)

    def ending(self, sec):
        # ii-V, a short drum pickup, then a single G6/9 ensemble arrival.
        lines = [[(0,"G4",.7,"ど"),(1,"A4",.4,"び"),(2,"Bb4",.7,"ば")],
                 [(0,"G4",.45,"ど"),(1,"E4",.55,"び"),(2,"A4",.65,"ば")],
                 [(0,"F4",6.8,"だ")], []]
        self.sing_lines(sec,lines,backing=True,gain=-1.2)
        hit = sec["beat"] + 8
        chord = self.chord(hit)
        for j,p in enumerate(chord["voicing"]):
            self.record(self.piano,p,hit+j*.009,5.8-j*.009,88+j)
        self.piano.sustain(hit+.02,hit+6.2)
        self.bass.note(chord["root"],hit,.95,94)
        self.guitar.notes_at(chord["voicing"][:2],hit+.012,.34,75,strum=.012)
        self.horn_chord(hit,.70,86)
        self.record(self.sax,N("G4"),hit+.014,1.45,94)
        self.sax.cc(64,0,hit)
        for part,name,v in (("kick","kick",88),("snare","snare",92),("cymbals","crash_tip",75)):
            self.kit[part].hit(name,hit+.008,v,.2)
        self.piano.cc(64,0,hit+6.3)

    def finish(self):
        # Release a preceding note before a same-key MIDI retrigger. The voice
        # is monophonic, so apply the same rule across all its pitches too.
        for t in self.s.tracks.values():
            groups = {}
            for n in sorted(t.notes,key=lambda n:n.start):
                key = 0 if t.instrument.startswith("voice.") else n.pitch
                if key in groups:
                    prev = groups[key]
                    if prev.start+prev.dur > n.start-.018:
                        prev.dur=max(.04,n.start-prev.start-.018)
                groups[key]=n
        self.s.length_beats=self.beat
        self.s.mix={"tracks":self.mix,"fx":{
            "room":{"type":"reverb","kind":"room","decay":.70,"predelay":8,"hpf":300,"lpf":7800},
            "plate":{"type":"reverb","kind":"plate","decay":1.05,"predelay":22,"hpf":350,"lpf":8500},
            "slap":{"type":"delay","beats":.22,"feedback":.12,"hpf":650,"lpf":5500}},
            "master":{"target_lufs":-14,"ceiling":-1,"mono_below":100,
                      "glue":{"threshold":-16,"ratio":1.5,"attack":30,"release":170}}}
        self.s.form_sections=self.sections
        self.s.chord_timeline=[{"beat":b,**self.chord(b)} for b,_,_ in self.timeline]
        self.s.written_events=self.score_events
        return self.s


def compose():
    a=Arrangement()
    a.prepare_form()
    for index,sec in enumerate(a.sections):
        kind=sec["kind"]
        if kind in SPECIAL:
            a.special_band(sec)
        else:
            a.copy_band(sec)
        if kind=="verse":
            first,second=(VERSE_A,VERSE_B) if sec["name"]=="verse 1" else (VERSE_B,VERSE_A)
            vocal_gain=1.6 if sec["name"]=="verse 2" else 0
            a.sing_lines(sec,first,gain=vocal_gain)
            a.sing_lines(sec,second,bar_offset=8,gain=vocal_gain+.3)
        elif kind=="lift":
            a.sing_lines(sec,LIFT,gain=.4)
        elif kind=="chorus":
            a.sing_lines(sec,HOOK,backing=sec["name"]!="chorus 1",gain=.5)
            if sec["bars"]==16:
                variation=copy.deepcopy(HOOK)
                variation[2]=[(0,"G4",.55,"ど"),(1,"A4",.35,"び"),(1.5,"Bb4",.95,"ば"),(2.5,"A4",.34,"だ"),(3,"G4",.44,"ど")]
                variation[6]=[(0,"A4",.70,"ば"),(1,"G4",.65,"ー"),(2,"Bb4",.35,"ど"),(2.5,"G4",.34,"び"),(3,"F4",.60,"だ")]
                a.sing_lines(sec,variation,bar_offset=8,backing=True,gain=.8)
        elif kind=="bridge":
            a.sing_lines(sec,BRIDGE,gain=-3.0)
        elif kind=="trading":
            a.trading(sec)
        elif kind=="tag":
            a.sing_lines(sec,TAG,backing=True,gain=-1.1)
        elif kind=="ending":
            a.ending(sec)
        a.melodic_answers(sec)
        a.add_transition(sec,index)
    return a.finish()


if __name__=="__main__":
    s=compose()
    for sec in s.form_sections:
        print(f"{s.seconds(sec['beat']):6.2f}-{s.seconds(sec['beat']+sec['bars']*4):6.2f}  {sec['name']} ({sec['groove']}, +{sec['transpose']})")
    print(len(s.tracks),"tracks;",sum(len(t.notes) for t in s.tracks.values()),"notes")
