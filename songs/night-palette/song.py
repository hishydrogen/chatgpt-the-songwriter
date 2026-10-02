"""Sound-palette audition for the Doomer-inspired track (132 BPM, straight 16ths, F major).

Part 1 - voices: every UTAU voicebank sings the same 8-bar chorus over the same groove.
Part 2 - keys, bass, drums: each candidate plays the same 4 bars (Bbmaj7 C Am7 Dm7).
Section list with timestamps: `python songs/night-palette/song.py`.
"""
from songwriter.instruments import surge
from songwriter.song import Song, chord_notes, note_number

BPM = 132

# Chorus hook, 8 bars: (pitch or "r", lyric, beats). One mora per note.
#   ロンリーナイト ネオンがにじむ / ひとりでおどる 終電のあと
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
HOOK_CHORDS = [("Bbmaj7", 4), ("C", 4), ("Am7", 4), ("Dm7", 4), ("Gm7", 4), ("C/E", 4),
               ("Fmaj7", 2), ("Dbmaj7", 2), ("Gm7", 2), ("C7sus4", 2)]
LOOP_CHORDS = [("Bbmaj7", 4), ("C", 4), ("Am7", 4), ("Dm7", 4)]

VOICES = [
    ("voice A: Hitsuboku Kumi", "voice.kumi", {}),
    ("voice B: Kumi strong", "voice.kumi", {"style": "S"}),
    ("voice C: Milk", "voice.milk", {}),
    ("voice D: Hikari One", "voice.hikari", {}),
    ("voice E: Viki Hopper", "voice.viki", {}),
    ("voice F: Adachi Rei (robot)", "voice.adachi", {}),
]
KEYS = [
    ("keys A: house piano (Salamander)", "piano.salamander", "stabs"),
    ("keys B: Rhodes", "epiano.rhodes", "stabs"),
    ("keys C: pluck synth", surge("Plucks/Clean"), "stabs"),
    ("keys D: supersaw stab", surge("Polysynths/Uni Saw FB"), "stabs"),
    ("keys E: DX EP", surge("Keys/DX EP"), "stabs"),
]
BASSES = [
    ("bass A: rubber synth bass", surge("Basses/Rubber Bass"), "bass"),
    ("bass B: FM slap", surge("Basses/FM Slap"), "bass"),
    ("bass C: saw bass", surge("Basses/Lord Sawtooth"), "bass"),
    ("bass D: deep sub", surge("Basses/Plain"), "bass"),
    ("bass E: finger bass (sampled)", "bass.darkblack", "bass"),
]
DRUMS = ["drums A: house kick, 4 on the floor", "drums B: 808 kick, broken beat",
         "drums C: punch kick, J-pop dance"]

ROOTS = {"Bbmaj7": "Bb1", "C": "C2", "Am7": "A1", "Dm7": "D2", "Gm7": "G1", "C/E": "E1",
         "Fmaj7": "F1", "Dbmaj7": "Db2", "C7sus4": "C2"}


class Palette:
    def __init__(self):
        s = self.s = Song("Night palette", bpm=BPM, key="F")
        self.kick = s.track("kick", "drums.club")
        self.clap = s.track("clap", "drums.club")
        self.hats = s.track("hats", "drums.club")
        self.bed_bass = s.track("bed bass", surge("Basses/Rubber Bass"))
        self.bed_keys = s.track("bed keys", "piano.salamander")
        self.beat = 0.0

    def chords_at(self, chords, b0):
        out, b = [], b0
        for c, d in chords:
            out.append((c, b, d))
            b += d
        return out

    def drums(self, b0, bars, style="A"):
        s = self.s
        for bar in range(bars):
            b = b0 + s.bar(bar)
            if style == "A":
                kicks = (0, 1, 2, 3)
            elif style == "B":
                kicks = (0, 0.75, 2.5) if bar % 2 == 0 else (0, 1.5, 2.25, 3.5)
            else:
                kicks = (0, 1.5, 2, 3.5) if bar % 2 == 0 else (0, 1.5, 2.25, 3)
            kname = {"A": "kick", "B": "kick_808", "C": "kick_punch"}[style]
            for k in kicks:
                self.kick.hit(kname, b + k, 118 if k in (0, 2) else 104)
            for k in (1, 3):
                self.clap.hit("clap", b + k, 116)
                if style != "B":
                    self.clap.hit("snare", b + k, 90)
            for i in range(16):
                p = i * 0.25
                if style == "A" and i % 4 == 2:
                    self.hats.hit("hh_open", b + p, 92)
                elif style == "B" and i in (6, 14):
                    self.hats.hit("hh_open", b + p, 84)
                else:
                    self.hats.hit("hh_closed", b + p, (100, 64, 86, 70)[i % 4])
            if style != "A":
                self.hats.hit("shaker", b + 0.5, 70)
                self.hats.hit("shaker", b + 2.5, 70)

    def bassline(self, t, chords, b0, vel=104):
        for c, b, d in self.chords_at(chords, b0):
            n = note_number(ROOTS[c])
            for k in range(int(d * 2)):
                p = b + k * 0.5
                oct_up = k % 4 == 3
                t.note(n + (12 if oct_up else 0), p, 0.35 if k % 2 else 0.45, vel if k % 2 == 0 else vel - 14)

    def stabs(self, t, chords, b0, vel=92):
        """Offbeat chord stabs with a 16th push into every other bar."""
        for c, b, d in self.chords_at(chords, b0):
            notes = sorted(chord_notes(c, 4))
            notes = [n - 12 if n > 74 else n for n in notes]
            for k in range(int(d)):
                t.notes_at(notes, b + k + 0.5, 0.3, vel)
            t.notes_at(notes, b + d - 0.25, 0.2, vel - 10)

    def sing(self, label, inst, x):
        t = self.s.track(label, inst)
        b = self.beat
        for p, l, d in HOOK:
            if p != "r":
                t.note(p, b, d, 100, lyric=l, x=dict(x) if x else None)
            b += d

    def section(self, label, bars):
        self.s.marker(self.beat, label)
        b0 = self.beat
        self.beat += self.s.bar(bars)
        return b0


def compose() -> Song:
    a = Palette()
    s = a.s
    # part 1: voices over the full groove (drums A, rubber bass, piano stabs)
    for label, inst, x in VOICES:
        b0 = a.section(label, 8)
        a.drums(b0, 8, "A")
        a.bassline(a.bed_bass, HOOK_CHORDS, b0)
        a.stabs(a.bed_keys, HOOK_CHORDS, b0, 80)
        a.beat = b0
        a.sing(label, inst, x)
        a.beat = b0 + s.bar(8)
    a.beat += s.bar(1)
    # part 2: keys over drums only
    for label, inst, _ in KEYS:
        b0 = a.section(label, 4)
        a.drums(b0, 4, "A")
        a.stabs(s.track(label, inst), LOOP_CHORDS, b0)
    for label, inst, _ in BASSES:
        b0 = a.section(label, 4)
        a.drums(b0, 4, "A")
        a.bassline(s.track(label, inst), LOOP_CHORDS, b0)
    for label, style in zip(DRUMS, "ABC"):
        b0 = a.section(label, 4)
        a.drums(b0, 4, style)
        a.bassline(a.bed_bass, LOOP_CHORDS, b0, 96)
    s.length_beats = a.beat + 2

    mixer = {
        "kick": {"gain": -4, "eq": [("hpf", 28)]},
        "clap": {"gain": -9, "eq": [("hpf", 150)], "sends": {"room": -12}},
        "hats": {"gain": -14, "eq": [("hpf", 400)], "pan": 0.2},
        "bed bass": {"gain": -8, "eq": [("hpf", 30)], "mono": True, "duck": {"by": "kick", "depth": 4}},
        "bed keys": {"gain": -14, "eq": [("hpf", 150), ("bell", 350, -3, 1.0)], "width": 0.6},
    }
    for label, *_ in VOICES:
        mixer[label] = {"gain": -3, "eq": [("hpf", 120), ("bell", 300, -2, 1.0)],
                        "comp": {"threshold": -20, "ratio": 3, "attack": 5, "release": 80},
                        "sends": {"plate": -12, "dly": -20}}
    for label, *_ in KEYS:
        mixer[label] = {"gain": -8, "eq": [("hpf", 150), ("bell", 350, -2, 1.0)], "width": 0.7,
                        "sends": {"plate": -16}}
    for label, *_ in BASSES:
        mixer[label] = {"gain": -6, "eq": [("hpf", 30)], "mono": True, "duck": {"by": "kick", "depth": 4}}
    s.mix = {
        "tracks": mixer,
        "fx": {
            "plate": {"type": "reverb", "kind": "plate", "decay": 1.6, "predelay": 20, "hpf": 300, "lpf": 9000},
            "room": {"type": "reverb", "kind": "room", "decay": 0.8, "predelay": 5, "hpf": 250, "lpf": 8000},
            "dly": {"type": "delay", "beats": 0.75, "feedback": 0.3, "hpf": 500, "lpf": 5000},
        },
        "master": {"glue": {"threshold": -16, "ratio": 2, "attack": 20, "release": 200}, "target_lufs": -14},
    }
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
