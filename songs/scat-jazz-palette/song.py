"""Checkpoint 1: identical performances, three singers and a live jazz band palette.

124 BPM, F major, lightly swung eighths. No random pattern generation: harmony,
walking-bass connections, comping, scat phrasing and answers are written by hand.
Deterministic small performance offsets are shared by every audition candidate.
"""
from __future__ import annotations

import random

import mido

from songwriter.song import Song, note_number as N

BPM = 124
SWING = 0.60
SCAT = {"ど": "do", "び": "bi", "だ": "da", "ば": "ba", "ぶ": "bu", "ー": "-"}

# beat within the eight-bar phrase, symbol, root, rootless/colour voicing.
HARMONY = [
    (0, "Fmaj9", "F1", ["A3", "C4", "E4", "G4"]),
    (4, "D7b9", "D2", ["F#3", "C4", "Eb4", "A4"]),
    (8, "Gm9", "G1", ["Bb3", "D4", "F4", "A4"]),
    (12, "C13", "C2", ["Bb3", "D4", "E4", "A4"]),
    (16, "Am7", "A1", ["G3", "C4", "E4", "A4"]),
    (18, "D7b9", "D2", ["F#3", "C4", "Eb4", "A4"]),
    (20, "Gm9", "G1", ["Bb3", "D4", "F4", "A4"]),
    (22, "C13", "C2", ["Bb3", "D4", "E4", "A4"]),
    (24, "Fmaj9", "F1", ["A3", "C4", "E4", "G4"]),
    (26, "Bbm6", "Bb1", ["Db4", "F4", "G4", "Bb4"]),
    (28, "Gm9", "G1", ["Bb3", "D4", "F4", "A4"]),
    (30, "C13", "C2", ["Bb3", "D4", "E4", "A4"]),
    (31.5, "F6/9", "F1", ["A3", "D4", "G4", "C5"]),
]

# Written on the straight grid; the performance function swings offbeats before
# applying a small phrase-specific push or lag. (offset, pitch, length, syllable)
HOOK = [
    [(0.5, "C4", .37, "ど"), (1, "E4", .40, "び"), (1.5, "G4", .34, "だ"),
     (2, "A4", .63, "ば"), (2.5, "G4", .32, "だ"), (3, "E4", .34, "ど")],
    [(0, "F#4", .40, "ど"), (.5, "A4", .34, "ば"), (1, "F#4", .68, "だ"),
     (2, "Eb4", .72, "ぶ"), (3, "D4", .34, "だ"), (3.5, "F#4", .26, "ば")],
    [(0, "G4", .85, "ど"), (1, "A4", .38, "び"), (1.5, "Bb4", .49, "だ"),
     (2, "A4", .45, "ば"), (2.5, "G4", .61, "ー"), (3.5, "F4", .30, "だ")],
    [(0, "E4", .40, "ど"), (.5, "G4", .33, "び"), (1, "A4", .58, "ば"),
     (1.5, "G4", .30, "だ"), (2, "E4", .90, "ー"), (3, "D4", .30, "ど"),
     (3.5, "G4", .28, "ば")],
    [(.5, "E4", .36, "ど"), (1, "G4", .35, "び"), (1.5, "A4", .34, "だ"),
     (2, "F#4", .66, "ば"), (2.5, "Eb4", .31, "だ"), (3, "D4", .30, "ど"),
     (3.5, "F#4", .27, "び")],
    [(0, "G4", .81, "ば"), (1, "A4", .36, "だ"), (1.5, "Bb4", .34, "び"),
     (2, "A4", .48, "ど"), (2.5, "G4", .33, "ば"), (3, "E4", .67, "ー")],
    [(0, "A4", .82, "だ"), (1, "G4", .61, "ば"), (2, "G4", .45, "ど"),
     (2.5, "F4", .33, "び"), (3, "Db4", .76, "だ")],
    [(0, "F4", .67, "ぶ"), (1, "G4", .35, "だ"), (1.5, "A4", .31, "び"),
     (2, "G4", .46, "ば"), (2.5, "E4", .33, "ど"), (3.5, "F4", .66, "だ")],
]

VOICE_OPTS = dict(vibrato_cents=18, vibrato_rate=5.2, vibrato_after=.26,
                  vibrato_fade=.15, port_pre=.016, port_post=.025, overshoot=7,
                  scoop=-38, scoop_time=.055, fall=-22, fall_time=.075,
                  jitter=.28, consonant=.82, breathy=.015, breath_db=-17,
                  breath_gap=.55, release=.060)
VOICES = [("voice A - Kumi", "voice.kumi"),
          ("voice B - Hikari", "voice.hikari"),
          ("voice C - Milk", "voice.milk")]
KEYS = [("keys A - Yamaha grand", "piano.salamander"),
        ("keys B - Steinway grand", "piano.splendid"),
        ("keys C - Rhodes", "epiano.rhodes")]
BASSES = [("bass A - upright", "bass.upright_pizz"),
          ("bass B - finger electric", "bass.darkblack")]
DRUMS = [("drums A - Virtuosity", "drums.virtuosity"),
         ("drums B - DRSKit", "drums.drskit")]


def chord_at(beat):
    local = min(31.999, max(0, beat))
    return next(c for c in reversed(HARMONY) if c[0] <= local + 1e-9)


def performed(beat, role, index=0):
    """One reproducible performed time for each role and phrase position."""
    if abs(beat * 2 - round(beat * 2)) < 1e-7 and round(beat * 2) % 2:
        beat += SWING - .5
    bias = {"voice": 10, "piano": -2, "bass": -3, "snare": 9,
            "ride": -1, "kick": -2, "guitar": 3, "horn": 4, "sax": 7}.get(role, 2)
    seed = 9127 + round(beat * 960) * 17 + sum(map(ord, role)) * 13 + index
    rng = random.Random(seed)
    offset_ms = bias + rng.uniform(-3.5, 3.5)
    return max(0, beat + offset_ms * BPM / 60000)


def velocity(base, beat, voice=0):
    rng = random.Random(2071 + round(beat * 960) * 7 + voice * 131)
    return max(1, min(127, base + rng.randint(-3, 3)))


class PaletteSong(Song):
    """Keep MIDI channels consistent across sequential candidate tracks and export scat."""
    @staticmethod
    def decorate(mf, tracks):
        for mt, track in tracks:
            absolute, tick = [], 0
            for msg in mt:
                tick += msg.time
                if msg.type != "end_of_track":
                    if hasattr(msg, "channel"):
                        msg = msg.copy(channel=track.channel)
                    absolute.append((tick, 1, msg.copy(time=0)))
            # The audio engine receives kana; DAW-readable MIDI gets ASCII syllables.
            for note in track.notes:
                if note.lyric:
                    absolute.append((round(note.start * mf.ticks_per_beat), 0,
                                     mido.MetaMessage("lyrics", text=SCAT[note.lyric], time=0)))
            absolute.append((0, -1, mido.MetaMessage("text", text=track.instrument, time=0)))
            mt.clear()
            prev = 0
            for tick, _, msg in sorted(absolute, key=lambda e: (e[0], e[1])):
                mt.append(msg.copy(time=tick - prev))
                prev = tick
        return mf

    def track_midi(self, track):
        mf = super().track_midi(track)
        return self.decorate(mf, [(mf.tracks[0], track)])

    def full_midi(self):
        mf = super().full_midi()
        return self.decorate(mf, zip(mf.tracks[1:], self.tracks.values()))


class Palette:
    def __init__(self):
        self.s = PaletteSong("Floating scat - sound palette", bpm=BPM, key="F")
        self.beat = 0
        self.sections = []
        self.mix = {}
        self.piano = self.track("band piano", "piano.salamander", 0, -8,
                                eq=[("hpf", 130), ("bell", 340, -2.5, .8)], width=.55,
                                sends={"room": -16})
        self.bass = self.track("band upright bass", "bass.upright_pizz", 1, -9,
                               eq=[("hpf", 35), ("bell", 220, -2, .8)], mono=True,
                               comp={"threshold": -19, "ratio": 2, "attack": 24, "release": 130})
        self.guitar = self.track("band muted guitar", "guitar.green_stac", 2, -17,
                                 eq=[("hpf", 220), ("lpf", 7000)], pan=-.30,
                                 sends={"room": -18})
        self.horns = [
            self.track("band trombone", "brass.trombone_stac", 3, -18, pan=-.22),
            self.track("band french horn", "brass.horn_stac", 4, -19, pan=.06),
            self.track("band muted trumpet", "brass.trumpet_harmon", 5, -18, pan=.26),
        ]
        for t in self.horns:
            self.mix[t.name].update(eq=[("hpf", 180), ("bell", 700, -1.5, .8)],
                                    sends={"room": -13})
        self.sax = self.track("band tenor replies", "sax.tenor", 6, -15,
                              eq=[("hpf", 170), ("bell", 650, -2, .8)], pan=.16,
                              sends={"plate": -17})
        self.drum_bed = self.drum_tracks("band", "drums.virtuosity")
        self.perc = self.track("band bongo and shaker", "drums.virtuosity", 9, -21,
                               eq=[("hpf", 330)], pan=-.27, sends={"room": -20})

    def track(self, name, inst, channel, gain, **cfg):
        t = self.s.track(name, inst, channel=channel)
        self.mix[name] = {"gain": gain, **cfg}
        return t

    def drum_tracks(self, label, inst):
        cfg = {
            "kick": (-12, 0, [("hpf", 35), ("bell", 70, -2, 1)]),
            "snare": (-11, -.06, [("hpf", 155)]),
            "ride": (-12, .25, [("hpf", 500), ("hshelf", 8000, -1, .7)]),
            "hat pedal": (-17, -.22, [("hpf", 650)]),
            "toms": (-15, -.14, [("hpf", 90)]),
        }
        return {part: self.track(f"{label} | {part}", inst, 9, gain, pan=pan, eq=eq,
                                width=.5 if part == "ride" else 1.0,
                                sends={"room": -17 if part != "kick" else -24})
                for part, (gain, pan, eq) in cfg.items()}

    def section(self, label, bars, role):
        start = self.beat
        self.s.marker(start, label)
        self.sections.append({"label": label, "beat": start, "bars": bars, "role": role})
        self.beat += bars * 4
        return start

    def drums(self, tracks, start, bars):
        for bar in range(bars):
            b = bar * 4
            for j, v in enumerate((53, 36, 58, 39)):
                tracks["kick"].hit("kick", start + performed(b + j, "kick"), velocity(v, b+j), .12)
            for j in (1, 3):
                tracks["snare"].hit("snare", start + performed(b+j, "snare"),
                                    velocity(79 if j == 1 else 84, b+j), .16)
            if bar in (1, 3, 5, 7):
                for j in (.5, 2.5):
                    tracks["snare"].hit("snare", start + performed(b+j, "snare"),
                                        velocity(27, b+j), .10)
            for j, v in ((0, 71), (1, 55), (1.5, 63), (2, 75), (3, 57), (3.5, 68)):
                tracks["ride"].hit("ride", start + performed(b+j, "ride"), velocity(v, b+j), .25)
            for j in (1, 3):
                tracks["hat pedal"].hit("hh_pedal", start + performed(b+j, "hat"), velocity(57, b+j), .12)
            if bar in (3, 7):
                for j, name, v in ((3.08, "tom_high", 63), (3.32, "tom_mid", 71),
                                   (3.65, "tom_low", 80)):
                    # Virtuosity labels its two main toms low/high.
                    drum = "tom_low" if name == "tom_mid" and tracks["toms"].instrument == "drums.virtuosity" else name
                    tracks["toms"].hit(drum, start + performed(b+j, "tom"), velocity(v,b+j), .17)

    def bassline(self, t, start, bars):
        lines = [["F1", "A1", "C2", "E2"], ["D2", "F#2", "A1", "F#1"],
                 ["G1", "Bb1", "D2", "Db2"], ["C2", "E2", "G1", "Ab1"],
                 ["A1", "C2", "D2", "F#1"], ["G1", "Bb1", "C2", "E2"],
                 ["F1", "A1", "Bb1", "Db2"], ["G1", "D2", "C2", "E2"]]
        for bar in range(bars):
            for j, pitch in enumerate(lines[bar % 8]):
                beat = bar*4+j
                length = (.78, .68, .81, .64)[j]
                if bar == 7 and j == 3:
                    length = .35
                t.note(pitch, start + performed(beat, "bass"), length,
                       velocity((91, 80, 88, 77)[j], beat))
            if bar == 7:
                t.note("F1", start + performed(31.5, "bass"), .66, 90)
        t.cc(11, 108, start)

    def comp(self, t, start, bars, feature=False):
        patterns = [((0,.32,73),(1.5,.22,64),(2.5,.28,74)),
                    ((.5,.30,68),(2.5,.24,75)),
                    ((0,.36,70),(1.5,.24,65),(3.5,.23,77)),
                    ((.5,.29,70),(2.5,.25,74)),
                    ((0,.26,72),(1.5,.23,64),(2.5,.25,75),(3.5,.24,70)),
                    ((.5,.27,70),(2,.23,74),(3,.27,65)),
                    ((0,.30,73),(1.5,.23,64),(2,.32,69),(3.5,.23,75)),
                    ((0,.25,71),(1.5,.23,66),(2,.25,72),(3.5,.65,81))]
        for bar in range(bars):
            for pos, dur, vel in patterns[bar % 8]:
                beat = bar*4+pos
                # A written anticipation uses the next chord; its note-off is explicit.
                look = beat+.5 if pos == 3.5 and bar not in (6,7) else beat
                chord = chord_at(look)
                pitches = [N(p) for p in chord[3]]
                onset = start + performed(beat,"piano")
                for i, p in enumerate(pitches):
                    roll = (0, .011, .020, .015)[i]
                    t.note(p,onset+roll,max(.10,dur-roll),velocity(vel+(3 if i==3 else -2),beat,i))
                t.sustain(onset+.025,onset+min(.30,dur+.05))
            # A recognisable top-line answer in the singer's first breathing gap.
            if bar in (0,4) or feature and bar in (1,3):
                phrase = [(3.38,"E4"),(3.62,"G4"),(3.83,"C5")] if bar in (0,4) else [(3.12,"F#4"),(3.38,"A4")]
                if bar == 3:
                    phrase = [(3.12,"E4"),(3.38,"G4"),(3.68,"A4")]
                for pos,pitch in phrase:
                    t.note(pitch,start+performed(bar*4+pos,"piano"),.14,velocity(80,bar*4+pos))
        t.cc(64,0,start+bars*4-.02)

    def band_colour(self,start,bars):
        for bar in range(bars):
            for pos in (1,3):
                beat=bar*4+pos
                chord=chord_at(beat)
                guide=[N(p) for p in chord[3][:2]]
                self.guitar.notes_at(guide,start+performed(beat,"guitar"),.16,
                                     velocity(63,beat),strum=.017)
            if bar%2:
                for k in range(8):
                    beat=bar*4+k*.5
                    self.perc.hit("shaker",start+performed(beat,"shaker"),
                                  velocity(43 if k%2 else 49,beat),.12)
                for pos,name in ((.5,"bongo_lo"),(2.5,"bongo_hi")):
                    self.perc.hit(name,start+performed(bar*4+pos,"bongo"),velocity(49,bar*4+pos),.13)
        # Horns and tenor take different gaps, with register and expression specified.
        for beat,pitches in ((13.32,["C3","E3","Bb3"]),
                            (23.78,["C3","E3","A3"]),
                            (31.52,["F3","A3","D4"])):
            if beat >= bars*4:
                continue
            for i,(t,pitch) in enumerate(zip(self.horns,pitches)):
                onset=start+performed(beat,"horn",i)+i*.008
                t.note(pitch,onset,.22 if beat<31 else .58,velocity(80,beat,i))
                t.cc_ramp(11,onset,onset+.18,74,104,step=.06)
        for bar in (0,4):
            if bar>=bars:
                continue
            startb=start+bar*4
            self.sax.cc(64,127,startb+3.30)
            self.sax.cc(80,12,startb+3.30)
            for pos,pitch,dur in ((3.39,"E4",.18),(3.64,"G4",.26)):
                onset=startb+performed(pos,"sax")
                self.sax.note(pitch,onset,dur,velocity(88,bar*4+pos))
            self.sax.bend(-700,startb+3.36)
            self.sax.bend(0,startb+3.46)
            self.sax.cc_ramp(11,startb+3.32,startb+3.92,74,101,step=.1)
            self.sax.cc(64,0,startb+3.96)

    def sing(self,label,inst,start):
        t=self.track(label,inst,10,-2,eq=[("hpf",125),("bell",280,-2.5,.9),
                       ("bell",750,-2,.9),("bell",3200,2,.7),("hshelf",9000,1.5,.7)],
                     comp={"threshold":-20,"ratio":2.5,"attack":10,"release":90},
                     sends={"plate":-15,"slap":-23})
        t.opts.update(VOICE_OPTS)
        for bar,line in enumerate(HOOK):
            for j,(pos,pitch,dur,syllable) in enumerate(line):
                beat=bar*4+pos
                onset=start+performed(beat,"voice")
                # Deliberate vowel connection; don't cut a note after a swung next onset.
                if j+1<len(line):
                    next_on=start+performed(bar*4+line[j+1][0],"voice")
                    dur=min(dur,max(.10,next_on-onset-.025))
                x={"vib":.70 if dur>.60 else 0,"scoop":.55 if j==0 else 0,
                   "fall":.5 if j==len(line)-1 else 0,
                   "gain_db":1.0 if syllable=="ば" and dur>.45 else 0.0}
                t.note(pitch,onset,dur,velocity(100 if dur>.45 else 93,beat),lyric=syllable,x=x)
                if dur>.60:
                    t.vibrato(onset+.38,onset+dur-.03,rate_hz=5.2,cents=12,fade=.45)
        return t

    def gap(self):
        # One quiet turnaround bar lets release/reverb tails clear before the next voice.
        self.s.marker(self.beat,"turnaround")
        self.drums(self.drum_bed,self.beat,1)
        self.bass.note("F1",self.beat,.70,65)
        self.piano.notes_at([N(p) for p in ("A3","D4","G4")],self.beat+.5,.25,56)
        self.beat+=4


def compose():
    a=Palette()
    for label,inst in VOICES:
        b=a.section(label,8,"voice")
        a.drums(a.drum_bed,b,8); a.bassline(a.bass,b,8); a.comp(a.piano,b,8)
        a.band_colour(b,8); a.sing(label,inst,b); a.gap()
    for label,inst in KEYS:
        b=a.section(label,4,"keys")
        a.drums(a.drum_bed,b,4); a.bassline(a.bass,b,4)
        t=a.track(label,inst,0,-5,eq=[("hpf",130),("bell",340,-2.5,.8)],
                  width=.55,sends={"room":-16})
        a.comp(t,b,4,feature=True); a.gap()
    for label,inst in BASSES:
        b=a.section(label,4,"bass")
        a.drums(a.drum_bed,b,4); a.comp(a.piano,b,4)
        t=a.track(label,inst,1,-6,eq=[("hpf",35),("bell",220,-2,.8)],mono=True,
                  comp={"threshold":-19,"ratio":2,"attack":24,"release":130})
        a.bassline(t,b,4); a.gap()
    for label,inst in DRUMS:
        b=a.section(label,4,"drums")
        a.comp(a.piano,b,4); a.bassline(a.bass,b,4)
        tracks=a.drum_tracks(label,inst)
        a.drums(tracks,b,4); a.gap()
    a.s.length_beats=a.beat
    a.s.mix={"tracks":a.mix,"fx":{
        "room":{"type":"reverb","kind":"room","decay":.65,"predelay":8,
                "hpf":300,"lpf":7800},
        "plate":{"type":"reverb","kind":"plate","decay":.90,"predelay":22,
                 "hpf":350,"lpf":8500},
        "slap":{"type":"delay","beats":.22,"feedback":.12,"hpf":650,"lpf":5500}},
        "master":{"target_lufs":-14,"ceiling":-1,"mono_below":100,
                  "glue":{"threshold":-16,"ratio":1.5,"attack":30,"release":170}}}
    a.s.palette_sections=a.sections
    return a.s


if __name__=="__main__":
    song=compose()
    for sec in song.palette_sections:
        print(f"{song.seconds(sec['beat']):6.2f}-{song.seconds(sec['beat']+sec['bars']*4):6.2f}  {sec['label']}")
    print(len(song.tracks),"tracks;",round(song.seconds(song.end_beat),2),"seconds plus release")
