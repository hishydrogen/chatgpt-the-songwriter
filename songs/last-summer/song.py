"""Last Summer (working title) - an early-2010s vocaloid rock song in the spirit of
siinamota's "少女A" (2013): style, harmony vocabulary, groove and sound only; all material
is original. D major, 170 BPM, straight 8ths and 16ths, a wall of double-tracked
distorted guitars, an upright piano, strings and glockenspiel, and a sung Japanese vocal
(Hikari One UTAU voicebank through songwriter.voice). Theme: the summer you can't go back
to - a marble sealed in a ramune bottle: you can see it, you can't take it out.

Material (chords, riff, melodies, lyrics) lives here; `Arranger` turns a FORM into tracks.
The palette (songs/summer-palette) and groove sketch (songs/summer-groove) import it.
"""
from __future__ import annotations

import random

from songwriter.song import Song, chord_notes, note_number

BPM = 170
KEY = "D"

# -- sounds (checkpoint 1 picks) ------------------------------------------------------------
KIT = "drums.drskit"
TOMS = {"tom1": "tom_high", "tom2": "tom_mid", "tom3": "tom_low"}
GTR = "guitar.emily_di"          # DI guitar into guitarix amp models (strip "amp")
BASS = "bass.darkblack_bright"
PIANO = "piano.upright"
GLOCK = "perc.glockenspiel"
VOX = "voice.hikari"
# Hikari One terms: no pitch/formant edits of the bank's audio -> formant stays 0
VOX_OPTS = {"vibrato_cents": 28, "port_pre": 0.03, "port_post": 0.045, "consonant": 0.85,
            "breath_gap": 0.3, "tail_gap": 0.15}

TS9 = {"type": "ts9", "fslider2_": 0.12, "fslider1_": 750, "fslider0_": 2}
RIG_RHYTHM = [TS9, {"type": "amp", "PreGain": 10, "Distortion": 75, "Drive": 0.5,       # palette B
                    "model": 0, "t_model": 9, "c_model": 13, "Presence": 5}]
RIG_LEAD = [{**TS9, "fslider2_": 0.25, "fslider1_": 850}, {"type": "amp", "PreGain": 10,
            "Distortion": 70, "Drive": 0.55, "Middle": 0.7, "model": 0, "t_model": 9, "c_model": 13,
            "Presence": 6}]
RIG_EDGE = [{"type": "amp", "PreGain": 0, "Distortion": 18, "Drive": 0.25, "model": 0, "t_model": 8,
             "c_model": 9, "Presence": 5}]                                               # palette C
RIG_BASS = {"chain": [{"type": "amp", "PreGain": 0, "Distortion": 30, "Drive": 0.35, "model": 0,
                       "t_model": 16, "c_model": 3, "Presence": 4}], "dry": 0.5}         # palette C

# -- harmony ---------------------------------------------------------------------------------
# Riff/intro: IV-V-iii-vi twice, landing on vi. Verse: a canon descent (D C# B A G F# E A).
RIFF_PROG = ["Gmaj7", "A", "F#m7", "Bm7", "Gmaj7", "A", "Bm7", "Bm7"]
VERSE = ["D", "A/C#", "Bm7", "F#m7/A", "Gmaj7", "D/F#", "Em7", "A",
         "D", "A/C#", "Bm7", "F#m7/A", "Gmaj7", "D/F#", "Em7", ("Asus4", "A")]
PRE = ["Bm7", "F#m7", "Gmaj7", "D/F#", "Em7", "F#m7", "Gmaj7", "A"]
# Chorus: IV-V-iii-vi ("王道進行"), a rising ii-iii-IV-V, again, and an unresolved end on vi.
CHORUS = ["Gmaj7", "A", "F#m7", "Bm7", "Em7", "F#m7", "Gmaj7", "A",
          "Gmaj7", "A", "F#m7", "Bm7", "Em7", "A", "Bm7", "Bm7"]
# Bridge: the minor iv (Gm6) for the bittersweet turn.
BRIDGE = ["Gmaj7", "Gm6", "F#m7", "Bm7", "Em7", "F#m7", "Gmaj7", "A"]
SOLO = VERSE[:8] + CHORUS[:8]
# Quiet chorus; its last bar climbs A -> B, the IV-V of E: the last chorus is a step up.
OCHI = ["Gmaj7", "A", "F#m7", "Bm7", "Em7", "F#m7", "Gmaj7", ("A", "B")]
LAST = CHORUS[:14] + ["D", "D"] + ["Gmaj7", "A", "F#m7", "Bm7", "Em7", "A", "D", "D"]
OUTRO = ["Gmaj7", "A", "F#m7", "Bm7", "Gmaj7", "A", "D", "D"]

FORM = [  # (name, progression, transpose)
    ("intro", RIFF_PROG[:4], 0),
    ("riff", RIFF_PROG, 0),
    ("verse 1", VERSE, 0),
    ("pre 1", PRE, 0),
    ("chorus 1", CHORUS, 0),
    ("interlude", RIFF_PROG, 0),
    ("verse 2", VERSE, 0),
    ("pre 2", PRE, 0),
    ("chorus 2", CHORUS, 0),
    ("solo", SOLO, 0),
    ("bridge", BRIDGE, 0),
    ("ochi", OCHI, 0),
    ("last chorus", LAST, 2),
    ("outro", OUTRO, 2),
]

# -- the face of the song: lead riff over RIFF_PROG, (pitch, beats), 3+3+2 cells ---------------
RIFF = [
    ("F#5", .75), ("D5", .75), ("B4", .5), ("D5", .5), ("E5", .5), ("F#5", .5), ("A5", .5),
    ("E5", .75), ("C#5", .75), ("A4", .5), ("C#5", .5), ("D5", .5), ("E5", 1.0),
    ("E5", .75), ("C#5", .75), ("A4", .5), ("C#5", .5), ("E5", .5), ("F#5", .5), ("A5", .5),
    ("F#5", .75), ("D5", .75), ("B4", .5), ("D5", .5), ("C#5", .5), ("B4", 1.0),
    ("F#5", .75), ("D5", .75), ("B4", .5), ("D5", .5), ("E5", .5), ("F#5", .5), ("B5", .5),
    ("A5", .75), ("E5", .75), ("C#5", .5), ("E5", .5), ("F#5", .5), ("E5", 1.0),
    ("D5", .75), ("F#5", .75), ("B5", .5), ("A5", .5), ("F#5", .5), ("E5", .5), ("D5", .5),
    ("E5", .75), ("D5", .75), ("C#5", .5), ("B4", 2.0),
]
assert sum(d for _, d in RIFF) == 8 * 4

# Guitar solo over SOLO (canon, then the chorus chords): (pitch, beats[, bend up from N
# semitones below]). Bars 9-16 paraphrase the hook an octave up and climb to a held E6.
SOLO_LINE = [
    ("F#5", 1.5, 2), ("A5", .5), ("F#5", .5), ("E5", .5), ("D5", 1.0),
    ("C#5", .5), ("E5", .5), ("A5", 1.0), ("E5", .5), ("C#5", .5), ("A4", 1.0),
    ("B4", .5), ("D5", .5), ("F#5", 1.0, 2), ("E5", .5), ("D5", .5), ("B4", 1.0),
    ("C#5", .5), ("E5", .5), ("F#5", .5), ("A5", .5), ("C#6", 2.0),
    ("D6", .25), ("C#6", .25), ("B5", .25), ("A5", .25), ("B5", .25), ("A5", .25), ("F#5", .25), ("E5", .25),
    ("D5", .25), ("E5", .25), ("F#5", .25), ("A5", .25), ("B5", 1.0),
    ("A5", .25), ("F#5", .25), ("E5", .25), ("D5", .25), ("E5", .25), ("D5", .25), ("B4", .25), ("A4", .25), ("D5", 2.0),
    ("G5", .25), ("F#5", .25), ("E5", .25), ("D5", .25), ("B4", .25), ("D5", .25), ("E5", .25), ("G5", .25),
    ("B5", 1.0, 2), ("A5", .5), ("G5", .5),
    ("A5", .5), ("E5", .25), ("C#5", .25), ("A4", .25), ("C#5", .25), ("E5", .25), ("A5", .25), ("C#6", .25), ("E6", .25),
    ("C#6", .5), ("E6", 1.0),
    ("A5", .5), ("B5", .5), ("D6", .5), ("E6", 1.5), ("D6", .5), ("r", .5),
    ("A5", .5), ("B5", .5), ("C#6", .5), ("E6", 1.0), ("D6", .5), ("C#6", 1.0),
    ("C#6", .75, 2), ("B5", .25), ("A5", .5), ("F#5", .5), ("A5", .5), ("C#6", .5), ("E6", .5), ("C#6", .5),
    ("D6", 1.5), ("B5", .5), ("A5", .5), ("F#5", .5), ("D5", 1.0),
    ("E5", .25), ("G5", .25), ("B5", .25), ("D6", .25), ("E6", .25), ("D6", .25), ("B5", .25), ("G5", .25),
    ("E5", .25), ("G5", .25), ("B5", .25), ("D6", .25), ("E6", 1.0),
    ("C#6", .25), ("B5", .25), ("A5", .25), ("F#5", .25), ("A5", .25), ("C#6", .25), ("E6", .25), ("C#6", .25), ("E6", 2.0),
    ("D6", .5), ("E6", .5), ("D6", .5), ("B5", .5), ("A5", .5), ("B5", .5), ("D6", 1.0, 1),
    ("E6", 3.0, 2), ("r", 1.0),
]
assert sum(n[1] for n in SOLO_LINE) == 16 * 4

# -- melodies: (pitch or "r", lyric, beats), one mora per note ---------------------------------
R = ("r", "", .5)

# 蝉の声が 遠くなって / アスファルトに 揺れる陽炎 / 自転車で 下った坂 / あの日の風が 頬をなでた
# ラムネの瓶 傾けたら / カランと鳴った ビー玉ひとつ / 「取り出せないね」って 笑った君 / その横顔が 焼きついてる
VERSE_1 = [
    ("r", "", 1.0), ("F#4", "せ", .5), ("F#4", "み", .5), ("E4", "の", .5), ("D4", "こ", .5), ("F#4", "え", .5), ("A4", "が", .5),
    ("A4", "と", .5), ("B4", "お", .5), ("A4", "く", .5), ("E4", "な", .5), ("r", "", .25), ("E4", "て", .75), ("r", "", 1.0),
    R, ("F#4", "あ", .5), ("F#4", "す", .5), ("F#4", "ふぁ", .5), ("A4", "る", .5), ("B4", "と", .5), ("A4", "に", .5), R,
    ("A4", "ゆ", .5), ("C#5", "れ", .5), ("B4", "る", .5), ("A4", "か", .5), ("F#4", "げ", .5), ("E4", "ろ", .5), ("F#4", "ー", 1.0),
    R, ("G4", "じ", .5), ("G4", "て", .5), ("F#4", "ん", .5), ("G4", "しゃ", .5), ("B4", "で", 1.0), R,
    ("A4", "く", .5), ("A4", "だ", .5), ("r", "", .25), ("F#4", "た", .75), ("E4", "さ", .5), ("D4", "か", 1.0), R,
    ("E4", "あ", .5), ("G4", "の", .5), ("B4", "ひ", .5), ("A4", "の", .5), ("G4", "か", .5), ("A4", "ぜ", .5), ("B4", "が", .5), R,
    ("C#5", "ほ", .5), ("B4", "お", .5), ("A4", "を", .5), ("A4", "な", .5), ("B4", "で", .5), ("A4", "た", 1.0), R,
    ("r", "", 1.0), ("F#4", "ら", .5), ("F#4", "む", .5), ("E4", "ね", .5), ("D4", "の", .5), ("F#4", "び", .5), ("A4", "ん", .5),
    ("A4", "か", .5), ("B4", "た", .5), ("A4", "む", .5), ("E4", "け", .5), ("E4", "た", .5), ("E4", "ら", 1.0), R,
    ("F#4", "か", .5), ("F#4", "ら", .5), ("A4", "ん", .5), ("B4", "と", .5), ("D5", "な", .5), ("r", "", .25), ("B4", "た", .75), R,
    ("C#5", "び", 1.0), ("B4", "だ", .5), ("A4", "ま", .5), ("F#4", "ひ", .5), ("A4", "と", .5), ("A4", "つ", .5), R,
    ("B4", "と", .5), ("B4", "り", .5), ("A4", "だ", .5), ("B4", "せ", .5), ("D5", "な", .5), ("D5", "い", .5), ("B4", "ね", .5),
    ("r", "", .25), ("A4", "て", .25),
    ("F#4", "わ", .5), ("A4", "ら", .5), ("r", "", .25), ("A4", "た", .75), ("B4", "き", .5), ("A4", "み", 1.0), R,
    ("G4", "そ", .5), ("A4", "の", .5), ("B4", "よ", .5), ("B4", "こ", .5), ("D5", "が", .5), ("B4", "お", .5), ("A4", "が", .5), R,
    ("A4", "や", .5), ("B4", "き", .5), ("D5", "つ", .5), ("C#5", "い", .5), ("B4", "て", .5), ("A4", "る", 1.0), R,
]
# 制服を 脱いだ春に / 君は遠い 町へ行った / 「元気でね」って 手を振った / 改札の向こう 消えた背中
# 知らない駅の 知らない夏 / 同じ空の 下にいるのに / スマホの中の 君はずっと / あの日のまま 笑ってる
VERSE_2 = [
    ("r", "", 1.0), ("F#4", "せ", .5), ("F#4", "い", .5), ("E4", "ふ", .5), ("D4", "く", .5), ("F#4", "お", 1.0),
    ("A4", "ぬ", .5), ("B4", "い", .5), ("A4", "だ", .5), ("E4", "は", .5), ("E4", "る", .5), ("E4", "に", 1.0), R,
    R, ("F#4", "き", .5), ("F#4", "み", .5), ("F#4", "わ", .5), ("A4", "と", .5), ("B4", "お", .5), ("A4", "い", 1.0),
    ("A4", "ま", .5), ("C#5", "ち", .5), ("B4", "え", .5), ("A4", "い", .5), ("r", "", .25), ("F#4", "た", .75), ("r", "", 1.0),
    R, ("G4", "げ", .5), ("G4", "ん", .5), ("F#4", "き", .5), ("G4", "で", .5), ("B4", "ね", .5), ("r", "", .25), ("A4", "て", .75),
    ("A4", "て", .5), ("A4", "お", .5), ("F#4", "ふ", .5), ("r", "", .25), ("E4", "た", 1.25), ("r", "", 1.0),
    ("E4", "か", .5), ("G4", "い", .5), ("B4", "さ", .5), ("A4", "つ", .5), ("G4", "の", .5), ("A4", "む", .5), ("B4", "こ", .5), ("B4", "う", .5),
    ("C#5", "き", .5), ("B4", "え", .5), ("A4", "た", .5), ("A4", "せ", .5), ("B4", "な", .5), ("A4", "か", 1.0), R,
    R, ("F#4", "し", .5), ("F#4", "ら", .5), ("E4", "な", .5), ("D4", "い", .5), ("F#4", "え", .5), ("A4", "き", .5), ("A4", "の", .5),
    ("A4", "し", .5), ("B4", "ら", .5), ("A4", "な", .5), ("E4", "い", .5), ("E4", "な", .5), ("E4", "つ", 1.0), R,
    ("F#4", "お", .5), ("F#4", "な", .5), ("A4", "じ", .5), ("B4", "そ", .5), ("D5", "ら", .5), ("B4", "の", 1.0), R,
    ("C#5", "し", .5), ("B4", "た", .5), ("A4", "に", .5), ("A4", "い", .5), ("F#4", "る", .5), ("A4", "の", .5), ("A4", "に", .5), R,
    ("B4", "す", .5), ("B4", "ま", .5), ("A4", "ほ", .5), ("B4", "の", .5), ("D5", "な", .5), ("D5", "か", .5), ("B4", "の", 1.0),
    ("F#4", "き", .5), ("A4", "み", .5), ("A4", "わ", .5), ("B4", "ず", .5), ("r", "", .25), ("A4", "と", 1.25), R,
    ("G4", "あ", .5), ("A4", "の", .5), ("B4", "ひ", .5), ("B4", "の", .5), ("D5", "ま", .5), ("B4", "ま", 1.0), R,
    ("A4", "わ", .5), ("B4", "ら", .5), ("r", "", .25), ("D5", "て", .75), ("C#5", "る", 1.5), R,
]
# 「来年もまた ここで会おう」 / 指切りした 小指が痛い / 夕立が 全部 流してく / ねえ
PRE_1 = [
    R, ("B4", "ら", .5), ("B4", "い", .5), ("A4", "ね", .5), ("B4", "ん", .5), ("D5", "も", .5), ("D5", "ま", .5), ("B4", "た", .5),
    ("A4", "こ", .5), ("A4", "こ", .5), ("C#5", "で", .5), ("C#5", "あ", .5), ("B4", "お", .5), ("A4", "う", 1.0), R,
    R, ("B4", "ゆ", .5), ("B4", "び", .5), ("A4", "き", .5), ("B4", "り", .5), ("D5", "し", .5), ("D5", "た", 1.0),
    ("F#4", "こ", .5), ("A4", "ゆ", .5), ("A4", "び", .5), ("B4", "が", .5), ("A4", "い", .5), ("F#4", "た", .5), ("F#4", "い", .5), R,
    ("G4", "ゆ", .5), ("G4", "う", .5), ("B4", "だ", .5), ("B4", "ち", .5), ("D5", "が", 1.0), R, ("D5", "ぜ", .5),
    ("C#5", "ん", .5), ("A4", "ぶ", 1.0), R, ("A4", "な", .5), ("B4", "が", .5), ("C#5", "し", .5), ("C#5", "て", .5),
    ("D5", "く", 1.5), ("r", "", 2.5),
    ("r", "", 2.0), ("F#4", "ね", .5), ("A4", "え", 1.0), R,
]
# 花火の音 遠く響いて / 誰かの 笑い声がして / 振り向いても 君はいない / ねえ
PRE_2 = [
    R, ("B4", "は", .5), ("B4", "な", .5), ("A4", "び", .5), ("B4", "の", .5), ("D5", "お", .5), ("D5", "と", 1.0),
    ("A4", "と", .5), ("A4", "お", .5), ("C#5", "く", .5), ("C#5", "ひ", .5), ("B4", "び", .5), ("A4", "い", .5), ("A4", "て", .5), R,
    R, ("B4", "だ", .5), ("B4", "れ", .5), ("A4", "か", .5), ("B4", "の", .5), R, ("D5", "わ", .5), ("D5", "ら", .5),
    ("F#4", "い", .5), ("A4", "ご", .5), ("A4", "え", .5), ("B4", "が", .5), ("A4", "し", .5), ("F#4", "て", 1.0), R,
    ("G4", "ふ", .5), ("G4", "り", .5), ("B4", "む", .5), ("B4", "い", .5), ("D5", "て", 1.0), ("D5", "も", .5), R,
    ("C#5", "き", .5), ("A4", "み", 1.0), R, ("A4", "わ", .5), ("B4", "い", .5), ("C#5", "な", 1.0),
    ("D5", "い", 1.5), ("r", "", 2.5),
    ("r", "", 2.0), ("F#4", "ね", .5), ("A4", "え", 1.0), R,
]
# かえりたい かえりたいよ / ビー玉に とじこめた夏 / 君の声も 青い空も / まだ ここで 光ってる
HOOK = [
    ("A4", "か", .5), ("B4", "え", .5), ("D5", "り", .5), ("E5", "た", 1.5), ("D5", "い", .5), ("r", "", .5),
    ("A4", "か", .5), ("B4", "え", .5), ("C#5", "り", .5), ("E5", "た", 1.0), ("D5", "い", .5),
    ("C#5", "よ", .75), ("r", "", .25),
    ("C#5", "び", 1.0), ("B4", "だ", .5), ("A4", "ま", .5), ("A4", "に", .5), ("r", "", .5),
    ("F#4", "と", .5), ("A4", "じ", .5),
    ("B4", "こ", .5), ("D5", "め", .5), ("D5", "た", .5), ("B4", "な", 1.0), ("A4", "つ", .5), ("r", "", 1.0),
    ("B4", "き", .5), ("B4", "み", .5), ("A4", "の", .5), ("B4", "こ", .5), ("D5", "え", 1.0), ("B4", "も", .5),
    ("r", "", .5),
    ("C#5", "あ", .5), ("C#5", "お", .5), ("B4", "い", .5), ("C#5", "そ", .5), ("E5", "ら", 1.0),
    ("C#5", "も", .5), ("r", "", .5),
    ("D5", "ま", .5), ("D5", "だ", 1.0), ("r", "", .5), ("B4", "こ", .5), ("D5", "こ", .5), ("E5", "で", 1.0),
    ("C#5", "ひ", .5), ("E5", "か", .5), ("r", "", .25), ("E5", "て", .75), ("E5", "る", 1.0), ("r", "", 1.0),
]
# もどれない もどれないよ / わかってる わかってるのに / 八月の 終わりの空に / 手を伸ばしたまま
CHORUS_B = [
    ("A4", "も", .5), ("B4", "ど", .5), ("D5", "れ", .5), ("E5", "な", 1.5), ("D5", "い", .5), ("r", "", .5),
    ("A4", "も", .5), ("B4", "ど", .5), ("C#5", "れ", .5), ("E5", "な", 1.0), ("D5", "い", .5), ("C#5", "よ", .75), ("r", "", .25),
    ("C#5", "わ", .5), ("C#5", "か", .5), ("r", "", .25), ("B4", "て", .25), ("A4", "る", 1.0), R, ("A4", "わ", .5), ("B4", "か", .5),
    ("r", "", .25), ("D5", "て", .25), ("C#5", "る", .5), ("B4", "の", .5), ("B4", "に", 1.5), ("r", "", 1.0),
    ("B4", "は", .5), ("B4", "ち", .5), ("A4", "が", .5), ("B4", "つ", .5), ("D5", "の", 1.0), R, ("D5", "お", .5),
    ("E5", "わ", .5), ("E5", "り", .5), ("C#5", "の", .5), ("D5", "そ", .5), ("E5", "ら", 1.5), ("D5", "に", .5),
    ("D5", "て", .5), ("C#5", "を", .5), ("B4", "の", .5), ("A4", "ば", .5), ("B4", "し", .5), ("D5", "た", .5), ("D5", "ま", 1.0),
    ("B4", "ま", 2.0), ("r", "", 2.0),
]
CHORUS_1 = HOOK + CHORUS_B
# chorus 2: あの笑顔も 青い空も / ... / 八月の 終わりの駅で / 立ち止まったまま
CHORUS_2 = HOOK[:26] + [
    ("B4", "あ", .5), ("B4", "の", .5), ("A4", "え", .5), ("B4", "が", .5), ("D5", "お", 1.0), ("B4", "も", .5), R,
] + HOOK[33:] + CHORUS_B[:34] + [
    ("E5", "わ", .5), ("E5", "り", .5), ("C#5", "の", .5), ("D5", "え", .5), ("E5", "き", 1.5), ("D5", "で", .5),
    ("D5", "た", .5), ("C#5", "ち", .5), ("B4", "ど", .5), ("A4", "ま", .5), ("r", "", .25), ("B4", "た", .75), ("D5", "ま", 1.0),
    ("B4", "ま", 2.0), ("r", "", 2.0),
]
# 大人になれば 忘れるって / 誰かが言ってた だけど / 忘れたくない 忘れたくないよ / 君がいた夏を
BRIDGE_MEL = [
    ("D4", "お", .5), ("G4", "と", .5), ("A4", "な", .5), ("B4", "に", .5), ("B4", "な", .5), ("A4", "れ", .5), ("B4", "ば", 1.0),
    R, ("D5", "わ", .5), ("D5", "す", .5), ("Bb4", "れ", .5), ("G4", "る", 1.0), ("r", "", .25), ("E4", "て", .75),
    ("F#4", "だ", .5), ("A4", "れ", .5), ("C#5", "か", .5), ("B4", "が", .5), ("A4", "い", .5), ("r", "", .25), ("A4", "て", .25),
    ("F#4", "た", 1.0),
    ("r", "", 1.0), ("B4", "だ", .5), ("D5", "け", .5), ("D5", "ど", 2.0),
    ("E5", "わ", .5), ("D5", "す", .5), ("B4", "れ", .5), ("D5", "た", .5), ("E5", "く", .5), ("D5", "な", .5), ("B4", "い", 1.0),
    ("E5", "わ", .5), ("C#5", "す", .5), ("A4", "れ", .5), ("C#5", "た", .5), ("E5", "く", .5), ("F#5", "な", .5), ("E5", "い", .5),
    ("C#5", "よ", .5),
    ("D5", "き", .5), ("D5", "み", .5), ("B4", "が", .5), ("D5", "い", .5), ("E5", "た", 1.0), ("D5", "な", .5), ("B4", "つ", .5),
    ("A4", "お", 2.0), ("r", "", 2.0),
]
# かえりたい かえりたいよ / ビー玉の 中の夏へ / 君もきっと 同じ空を / どこかで 見上げてる / ねえ
OCHI_MEL = HOOK[:13] + [
    ("C#5", "び", 1.0), ("B4", "だ", .5), ("A4", "ま", .5), ("A4", "の", .5), R, ("F#4", "な", .5), ("A4", "か", .5),
    ("B4", "の", .5), ("D5", "な", .5), ("D5", "つ", .5), ("B4", "え", 1.5), ("r", "", 1.0),
    ("B4", "き", .5), ("B4", "み", .5), ("A4", "も", .5), ("B4", "き", .5), ("r", "", .25), ("D5", "と", 1.25), R,
    ("C#5", "お", .5), ("C#5", "な", .5), ("B4", "じ", .5), ("C#5", "そ", .5), ("E5", "ら", 1.0), ("C#5", "お", .5), R,
    ("D5", "ど", .5), ("D5", "こ", .5), ("B4", "か", .5), ("D5", "で", 1.0), R, ("B4", "み", .5), ("D5", "あ", .5),
    ("E5", "げ", .5), ("D5", "て", .5), ("E5", "る", 1.0), R, ("F#4", "ね", .5), ("B4", "え", 1.0),
]
# (a step up) ありがとう ありがとうね / ビー玉に とじこめた夏 / いつまでも 色褪せないで / この胸で 光ってる
# もどれない もどれなくても / 大丈夫 歩いてゆくよ / 八月の 終わりの空に / 手を振って 笑うよ
# もどれない もどれなくても / 忘れない 忘れないから / 八月の 終わりの空に / さよならを 言うよ
_NAKUTEMO = CHORUS_B[:6] + [
    ("A4", "も", .5), ("B4", "ど", .5), ("C#5", "れ", .5), ("E5", "な", 1.0), ("D5", "く", .5), ("C#5", "て", .5), ("B4", "も", .5)]
LAST_MEL = [
    ("A4", "あ", .5), ("B4", "り", .5), ("D5", "が", .5), ("E5", "と", 1.5), ("D5", "ー", .5), ("r", "", .5),
    ("A4", "あ", .5), ("B4", "り", .5), ("C#5", "が", .5), ("E5", "と", 1.0), ("D5", "ー", .5), ("C#5", "ね", .75), ("r", "", .25),
] + HOOK[13:26] + [
    ("B4", "い", .5), ("B4", "つ", .5), ("A4", "ま", .5), ("B4", "で", .5), ("D5", "も", 1.5), R,
    ("C#5", "い", .5), ("C#5", "ろ", .5), ("B4", "あ", .5), ("C#5", "せ", .5), ("E5", "な", 1.0), ("C#5", "い", .5), ("B4", "で", .5),
    R, ("D5", "こ", .5), ("D5", "の", .5), ("B4", "む", .5), ("D5", "ね", 1.0), ("E5", "で", 1.0),
] + HOOK[-6:] + _NAKUTEMO + [
    ("C#5", "だ", .5), ("C#5", "い", .5), ("B4", "じょ", .5), ("A4", "ー", .5), ("A4", "ぶ", .5), R, ("A4", "あ", .5), ("B4", "る", .5),
    ("D5", "い", .5), ("C#5", "て", .5), ("B4", "ゆ", .5), ("B4", "く", .5), ("B4", "よ", 1.0), ("r", "", 1.0),
] + CHORUS_B[27:40] + [
    ("D5", "て", .5), ("C#5", "を", .5), ("D5", "ふ", .5), ("r", "", .25), ("E5", "て", .75), R, ("D5", "わ", .5), ("E5", "ら", .5),
    ("D5", "う", 1.0), ("D5", "よ", 2.0), ("r", "", 1.0),
] + _NAKUTEMO + [
    ("C#5", "わ", .5), ("C#5", "す", .5), ("B4", "れ", .5), ("A4", "な", .5), ("A4", "い", .5), R, ("A4", "わ", .5), ("B4", "す", .5),
    ("D5", "れ", .5), ("C#5", "な", .5), ("B4", "い", .5), ("B4", "か", .5), ("B4", "ら", 1.0), ("r", "", 1.0),
] + CHORUS_B[27:40] + [
    ("D5", "さ", .5), ("C#5", "よ", .5), ("D5", "な", .5), ("E5", "ら", 1.0), ("D5", "お", 1.0), R,
    ("B4", "い", .5), ("C#5", "う", .5), ("D5", "よ", 3.0),
]

for _name, _mel, _bars in (("verse 1", VERSE_1, 16), ("verse 2", VERSE_2, 16), ("pre 1", PRE_1, 8),
                           ("pre 2", PRE_2, 8), ("hook", HOOK, 8), ("chorus 1", CHORUS_1, 16),
                           ("chorus 2", CHORUS_2, 16), ("bridge", BRIDGE_MEL, 8), ("ochi", OCHI_MEL, 8),
                           ("last", LAST_MEL, 24)):
    assert abs(sum(d for *_, d in _mel) - _bars * 4) < 1e-9, (_name, sum(d for *_, d in _mel))

# -- voicing helpers ---------------------------------------------------------------------------


def pcs(name: str, tr: int = 0) -> set[int]:
    """Pitch classes of a chord symbol (slash bass excluded)."""
    return {(p + tr) % 12 for p in chord_notes(name.split("/")[0], 4)}


def root_of(name: str, lo: str = "E1", hi: str = "D#2", tr: int = 0, slash: bool = True) -> int:
    """Root (or slash bass) between lo and hi."""
    sym = name.split("/")[1] if "/" in name and slash else name.split("/")[0]
    letter = sym[:2] if len(sym) > 1 and sym[1] in "#b" else sym[:1]
    n = note_number(f"{letter}1") + tr
    while n < note_number(lo):
        n += 12
    while n > note_number(hi):
        n -= 12
    return n


def power(name: str, tr: int = 0, octave: bool = True) -> list[int]:
    """Guitar power chord on the chord root (low E or A string, E2-D#3): root, fifth, octave."""
    r = root_of(name, "E2", "D#3", tr, slash=False)
    return [r, r + 7, r + 12] if octave else [r, r + 7]


def voicing(name: str, top: int, n: int = 3, tr: int = 0) -> list[int]:
    """Top note plus the n nearest chord tones below it, no semitone between neighbours
    (the top's pitch class is doubled only when the chord has too few notes)."""
    ps = pcs(name, tr)
    out, p = [top], top - 1
    while len(out) < n + 1 and p > top - 20:
        if p % 12 in ps and out[-1] - p != 1 and (p % 12 != top % 12 or len(ps) < n + 1):
            out.append(p)
        p -= 1
    return sorted(out)


def top_for(name: str, tr: int = 0, ceiling: str = "F#5") -> int:
    """Highest chord tone at or below the ceiling (keeps keyboard tops in one band)."""
    c = note_number(ceiling) + tr
    ps = pcs(name, tr)
    while c % 12 not in ps:
        c -= 1
    return c


D_MAJOR = [2, 4, 6, 7, 9, 11, 1]   # pitch classes D E F# G A B C#


def harmony_note(pitch: int, chord: str, tr: int, below: bool = False) -> int:
    """A diatonic third above (or below) if it is a chord tone, else the nearest chord tone
    3-5 semitones away."""
    ps = pcs(chord, tr)
    scale = [(p + tr) % 12 for p in D_MAJOR]
    sign = -1 if below else 1
    if pitch % 12 in scale:
        k = scale.index(pitch % 12)
        step = (sign * (scale[(k + 2 * sign) % 7] - pitch)) % 12
        if (pitch + sign * step) % 12 in ps:
            return pitch + sign * step
    for d in (3, 4, 5):
        if (pitch + sign * d) % 12 in ps:
            return pitch + sign * d
    return pitch + sign * 3


class Arranger:
    def __init__(self, form, title="Last Summer"):
        """form: [(section, progression (one entry per bar; a tuple = two half-bar chords),
        transpose)]"""
        s = self.s = Song(title, bpm=BPM, key=KEY)
        self.rng = random.Random(2013)
        self.kick, self.snare, self.hats = s.track("kick", KIT), s.track("snare", KIT), s.track("hats", KIT)
        self.cym, self.toms = s.track("cymbals", KIT), s.track("toms", KIT)
        self.bass = s.track("bass", BASS)
        self.gtr = [s.track("guitar L", GTR), s.track("guitar R", GTR)]
        self.lead = s.track("lead guitar", GTR)
        self.edge = s.track("arpeggio guitar", GTR)
        self.piano = s.track("piano", PIANO)
        self.glock = s.track("glockenspiel", GLOCK)
        self.vln = s.track("violins", "strings.violins_sus")
        self.vla = s.track("violas", "strings.violas_sus")
        self.vc = s.track("celli", "strings.celli_sus")
        self.vox = s.track("vocal", VOX)
        self.vox.opts.update(VOX_OPTS)
        self.harm = [s.track("harmony L", VOX), s.track("harmony R", VOX)]
        self.harm[0].opts.update({**VOX_OPTS, "vibrato_cents": 18, "breathy": 0.15, "breath_db": None})
        self.harm[1].opts.update({**VOX_OPTS, "vibrato_cents": 22, "breathy": 0.25, "breath_db": None,
                                  "port_pre": 0.04})
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

    # -- lookup / feel ---------------------------------------------------------------------------
    def chord_at(self, beat):
        for st, en, name, tr in self.timeline:
            if st <= beat + 1e-6 < en:
                return st, en, name, tr
        return self.timeline[-1]

    def span(self, name):
        b0, n, tr = self.sec[name]
        return self.s.bar(b0), n, tr

    def T(self, beat, ms=4.0):
        return max(0.0, beat + self.rng.gauss(0, ms) / 1000 * BPM / 60)

    def V(self, vel, spread=4):
        return int(max(1, min(127, vel + self.rng.randint(-spread, spread))))

    def hit(self, track, drum, beat, vel, ms=4.0):
        track.hit(drum, self.T(beat, ms), self.V(vel))

    # -- drums -----------------------------------------------------------------------------------
    def drums_8beat(self, b0, bars, vel=1.0, fill="toms", crash=True, ride=False, push=True):
        """Groove A: kick 1, &2, 3 (+&4 every other bar), snare 2 and 4, 8th hats (or ride on
        quarters + hats, ride=True)."""
        for bar in range(bars):
            b = b0 + 4 * bar
            last = fill and bar == bars - 1
            kicks = (0, 1.5, 2) if bar % 2 == 0 or not push else (0, 1.5, 2, 3.5)
            for k in kicks:
                if not (last and k >= 2):
                    self.hit(self.kick, "kick", b + k, (118 if k in (0, 2) else 104) * vel)
            for k in (1, 3):
                if not (last and k == 3):
                    self.hit(self.snare, "snare", b + k, 116 * vel)
            for i in range(8):
                if last and i >= 4:
                    break
                if ride and i % 2 == 0:
                    self.hit(self.cym, "ride", b + i * .5, (104 if i % 4 == 0 else 92) * vel)
                elif not ride:
                    self.hit(self.hats, "hh_closed" if i % 2 == 0 or bar % 4 != 3 or i != 7 else "hh_open",
                             b + i * .5, (100, 76)[i % 2] * vel)
            if last:
                self.fill(b + 2, fill, vel)
        if crash:
            self.hit(self.cym, "crash", b0, 112 * vel)

    def drums_four(self, b0, bars, vel=1.0, fill="snare", crash=True):
        """Groove B (dance rock, 四つ打ち): kick on every beat, snare 2 and 4, open hat on
        every &, quiet 16th closed hats."""
        for bar in range(bars):
            b = b0 + 4 * bar
            last = fill and bar == bars - 1
            for k in range(4):
                if not (last and k >= 2):
                    self.hit(self.kick, "kick", b + k, (118 if k % 2 == 0 else 110) * vel)
            for k in (1, 3):
                if not (last and k == 3):
                    self.hit(self.snare, "snare", b + k, 114 * vel)
            for i in range(16):
                p = i * .25
                if last and p >= 2:
                    break
                if i % 4 == 2:
                    self.hit(self.hats, "hh_open", b + p, 96 * vel)
                elif i % 4 != 0:
                    self.hit(self.hats, "hh_closed", b + p, (0, 62, 0, 70)[i % 4] * vel)
            if last:
                self.fill(b + 2, fill, vel)
        if crash:
            self.hit(self.cym, "crash", b0, 112 * vel)

    def drums_sprint(self, b0, bars, vel=1.0, fill="toms", crash=True):
        """Groove C (16-beat sprint): syncopated kick, snare 2 and 4 with ghost notes, 16th
        hats accented on the 8ths."""
        for bar in range(bars):
            b = b0 + 4 * bar
            last = fill and bar == bars - 1
            kicks = (0, .75, 1.5, 2, 2.75) if bar % 2 == 0 else (0, .75, 1.5, 2, 3.25, 3.5)
            for k in kicks:
                if not (last and k >= 2):
                    self.hit(self.kick, "kick", b + k, (118 if k in (0, 2) else 102) * vel)
            for k in (1, 3):
                if not (last and k == 3):
                    self.hit(self.snare, "snare", b + k, 116 * vel)
            for g in (1.75, 3.75) if bar % 2 else (2.25,):
                if not (last and g >= 2):
                    self.hit(self.snare, "snare", b + g, 52 * vel, ms=3)
            for i in range(16):
                p = i * .25
                if last and p >= 2:
                    break
                self.hit(self.hats, "hh_closed", b + p, (100, 64, 84, 66)[i % 4] * vel, ms=3)
            if last:
                self.fill(b + 2, fill, vel)
        if crash:
            self.hit(self.cym, "crash", b0, 112 * vel)

    def drums_half(self, b0, bars, vel=1.0, fill="snare", crash=True):
        """Half time: kick 1 and &3, snare on 3, 8th hats (bridge, quiet chorus pick-up)."""
        for bar in range(bars):
            b = b0 + 4 * bar
            last = fill and bar == bars - 1
            for k in (0, 2.5):
                self.hit(self.kick, "kick", b + k, 110 * vel)
            self.hit(self.snare, "snare", b + 2, 112 * vel)
            for i in range(8):
                if last and i >= 6:
                    break
                self.hit(self.hats, "hh_closed", b + i * .5, (88, 64)[i % 2] * vel)
            if last:
                self.fill(b + 3, fill, vel, beats=1)
        if crash:
            self.hit(self.cym, "crash", b0, 104 * vel)

    def fill(self, at, kind, vel=1.0, beats=2):
        """Fill over the last `beats` beats before the next section; a different one each time."""
        n = int(beats / .25)
        if kind == "toms":
            seq = ["snare"] * (n // 4) + [TOMS["tom1"]] * (n // 4) + [TOMS["tom2"]] * (n // 4) + [TOMS["tom3"]] * (n - 3 * (n // 4))
            for i, d in enumerate(seq):
                self.hit(self.snare if d == "snare" else self.toms, d, at + i * .25, (96 + 24 * i / n) * vel)
            self.hit(self.kick, "kick", at, 110 * vel)
        elif kind == "snare":
            for i in range(n):
                self.hit(self.snare, "snare", at + i * .25, (70 + 50 * i / n) * vel, ms=3)
        elif kind == "flams":
            for i, d in enumerate(["snare", TOMS["tom1"], "snare", TOMS["tom2"], "snare", TOMS["tom3"],
                                   TOMS["tom3"], "snare"][:int(beats / .25)]):
                self.hit(self.snare if d == "snare" else self.toms, d, at + i * .25, (100 + 3 * i) * vel)
                if i % 2 == 1:
                    self.hit(self.kick, "kick", at + i * .25, 104 * vel)
        elif kind == "kime":        # unison hits with the band: & of 3, 4 (crash choke)
            for p in (beats - 1.5, beats - 1.0):
                self.hit(self.kick, "kick", at + p, 120 * vel)
                self.hit(self.snare, "snare", at + p, 118 * vel)
                self.hit(self.cym, "crash", at + p, 110 * vel)

    def crash(self, beat, vel=112):
        self.hit(self.cym, "crash", beat, vel)
        self.hit(self.kick, "kick", beat, 118)

    # -- bass ------------------------------------------------------------------------------------
    def bass_8ths(self, b0, bars, vel=1.0, oct_pop=True, lead_in=True):
        """Root 8ths (ルート弾き), an octave pop on the & of 4, a lead-in to the next root."""
        for k in range(bars * 8):
            p = b0 + k * .5
            st, en, name, tr = self.chord_at(p)
            r = root_of(name, tr=tr)
            n = r
            if k % 8 == 7:
                nst, _, nname, ntr = self.chord_at(p + .5)
                nr = root_of(nname, tr=ntr)
                if lead_in and nr != r and k == bars * 8 - 1:
                    n = nr - 1 if (nr - 1) >= note_number("E1") else nr + 2
                elif oct_pop:
                    n = r + 12
            self.bass.note(n, self.T(p, 5), .42, self.V((110 if k % 2 == 0 else 96) * vel))

    def bass_octaves(self, b0, bars, vel=1.0):
        """Dance-rock octaves: root on the beat, octave on the &."""
        for k in range(bars * 8):
            p = b0 + k * .5
            st, en, name, tr = self.chord_at(p)
            r = root_of(name, tr=tr)
            self.bass.note(r + (12 if k % 2 else 0), self.T(p, 5), .4, self.V((112 if k % 2 == 0 else 100) * vel))

    def bass_drive16(self, b0, bars, vel=1.0):
        """8ths with a 16th double on the & of 2 and 4 (the sprint groove)."""
        for bar in range(bars):
            b = b0 + 4 * bar
            for p, d, v in ((0, .45, 112), (.5, .45, 98), (1, .45, 108), (1.5, .2, 100), (1.75, .2, 92),
                            (2, .45, 110), (2.5, .45, 98), (3, .45, 106), (3.5, .2, 100), (3.75, .2, 96)):
                st, en, name, tr = self.chord_at(b + p)
                r = root_of(name, tr=tr)
                self.bass.note(r + (12 if p == 3.75 else 0), self.T(b + p, 5), d, self.V(v * vel))

    def bass_long(self, b0, bars, vel=1.0):
        """Whole notes on each chord (quiet sections)."""
        for st, en, name, tr in self.timeline:
            if b0 - 1e-6 <= st < b0 + bars * 4 - 1e-6:
                self.bass.note(root_of(name, tr=tr), st, (en - st) * .95, self.V(96 * vel))

    # -- guitars ---------------------------------------------------------------------------------
    def _strum(self, t, notes, beat, dur, vel, mute, seed_rng):
        t.cc(70, 127 if mute else 0, max(0.0, beat - .03))
        when = beat + seed_rng.gauss(0, 6) / 1000 * BPM / 60
        for j, n in enumerate(notes):
            t.note(n, max(0.0, when + j * .004), dur, int(max(1, min(127, vel + seed_rng.randint(-4, 4)))))

    def gtr_chug(self, b0, bars, vel=1.0, accents=(0, 1.5, 3)):
        """Palm-muted 8ths with open accents (verses)."""
        for side, t in enumerate(self.gtr):
            rng = random.Random(int(b0 * 7) + side)
            for k in range(bars * 8):
                p = b0 + k * .5
                st, en, name, tr = self.chord_at(p)
                acc = (k % 8) * .5 in accents
                self._strum(t, power(name, tr), p, .46 if acc else .22, (122 if acc else 104) * vel, not acc, rng)

    def gtr_wall(self, b0, bars, vel=1.0):
        """Open power-chord 8ths, accents on the beats (choruses)."""
        for side, t in enumerate(self.gtr):
            rng = random.Random(int(b0 * 11) + side)
            for k in range(bars * 8):
                p = b0 + k * .5
                st, en, name, tr = self.chord_at(p)
                self._strum(t, power(name, tr), p, .48, (122 if k % 2 == 0 else 112) * vel, False, rng)

    def gtr_cut(self, b0, bars, vel=1.0):
        """16th cutting: muted strums with open accents on 1, the a of 1, & of 2, 4 (dance rock)."""
        acc = {0, .75, 1.5, 3, 3.75}
        for side, t in enumerate(self.gtr):
            rng = random.Random(int(b0 * 13) + side)
            for k in range(bars * 16):
                p = b0 + k * .25
                st, en, name, tr = self.chord_at(p)
                a = (k % 16) * .25 in acc
                self._strum(t, power(name, tr), p, .3 if a else .12, (120 if a else 84) * vel, not a, rng)

    def gtr_trem(self, b0, bars, vel=1.0):
        """16th tremolo picking on the power chord, palm-muted lightly, open on the beats."""
        for side, t in enumerate(self.gtr):
            rng = random.Random(int(b0 * 17) + side)
            for k in range(bars * 16):
                p = b0 + k * .25
                st, en, name, tr = self.chord_at(p)
                on = k % 4 == 0
                self._strum(t, power(name, tr, octave=False), p, .24, (116 if on else 98) * vel, not on, rng)

    def gtr_hold(self, b0, bars, vel=1.0):
        """Let-ring power chords on every chord change (breaks, the pre-chorus lift)."""
        for side, t in enumerate(self.gtr):
            rng = random.Random(int(b0 * 19) + side)
            for st, en, name, tr in self.timeline:
                if b0 - 1e-6 <= st < b0 + bars * 4 - 1e-6:
                    self._strum(t, power(name, tr), st, (en - st) * .96, 118 * vel, False, rng)

    def gtr_hits(self, beats, dur=.4, vel=1.0):
        """Unison kime hits."""
        for side, t in enumerate(self.gtr):
            rng = random.Random(int(beats[0] * 23) + side)
            for p in beats:
                st, en, name, tr = self.chord_at(p)
                self._strum(t, power(name, tr), p, dur, 124 * vel, False, rng)

    def lead_line(self, b0, line, tr=0, vel=1.0, vib_cents=28, track=None):
        """A monophonic lead (the riff, the solo): notes never overlap; long notes get pitch-bend
        vibrato (the DI sampler bends +/-12 semitones)."""
        t = track or self.lead
        b = b0
        for p, d, *bend in line:
            if p != "r":
                n = note_number(p) + tr
                st = self.T(b, 5)
                t.note(n, st, max(.1, d - .04), self.V(112 * vel))
                v0 = b
                if bend:            # pick a step below and push the string up into the note
                    rise = min(.3, d * .3)
                    for i in range(7):
                        f = i / 6
                        t.bend(int(-bend[0] / 12 * 8191 * (1 - f) ** 2), st + f * rise)
                    v0 = b + rise
                if d >= .75 and vib_cents:
                    t.vibrato(v0 + min(.35, d * .4), b + d - .05, rate_hz=5.6, cents=vib_cents, bend_range=12,
                              fade=.5)
                elif bend:
                    t.bend(0, b + d - .05)
            b += d
        return b

    def arpeggio(self, b0, bars, vel=1.0, step=.5):
        """Let-ring arpeggios on open-sounding voicings (edge-of-breakup guitar)."""
        for k in range(int(bars * 4 / step)):
            p = b0 + k * step
            st, en, name, tr = self.chord_at(p)
            r = root_of(name, "E2", "D#3", tr)
            v = voicing(name, top_for(name, tr, "F#5"), 3, tr)
            shape = [r, v[0], v[1], v[2], v[3], v[2], v[1], v[0]]
            self.edge.note(shape[k % 8], self.T(p, 6), 1.4, self.V((96 if k % 4 == 0 else 82) * vel))

    # -- keys and colour -----------------------------------------------------------------------
    def piano_8ths(self, b0, bars, vel=1.0):
        """Rock piano: left-hand root octaves on quarters, right-hand chords on 8ths."""
        for k in range(bars * 8):
            p = b0 + k * .5
            st, en, name, tr = self.chord_at(p)
            rh = voicing(name, top_for(name, tr, "E5"), 3, tr)
            if k % 2 == 0:
                r = root_of(name, "C2", "B2", tr)
                self.piano.notes_at([r, r + 12], self.T(p, 6), .9, self.V(90 * vel))
            self.piano.notes_at(rh, self.T(p, 6), .4, self.V((88 if k % 2 == 0 else 72) * vel))

    def piano_arp16(self, b0, bars, vel=1.0):
        """16th arpeggios up and down over two octaves, pedalled per chord."""
        for st, en, name, tr in self.timeline:
            if not (b0 - 1e-6 <= st < b0 + bars * 4 - 1e-6):
                continue
            r = root_of(name, "C3", "B3", tr)
            v = voicing(name, top_for(name, tr, "A5"), 4, tr)
            up = [r, r + 7] + v
            seq = up + up[-2:0:-1]
            n = int((en - st) / .25)
            for i in range(n):
                self.piano.note(seq[i % len(seq)], self.T(st + i * .25, 5), .3, self.V((84 if i % 4 == 0 else 68) * vel))
            self.piano.sustain(st + .02, en - .05)

    def piano_riff(self, b0, line, tr=0, octave=0, vel=1.0):
        b = b0
        for p, d in line:
            if p != "r":
                n = note_number(p) + tr + 12 * octave
                self.piano.notes_at([n, n - 12], self.T(b, 5), d * .9, self.V(96 * vel))
            b += d

    def piano_ballad(self, b0, bars, vel=1.0):
        """Quiet chorus: half-note chords with a moving top, pedalled; root octaves below."""
        for st, en, name, tr in self.timeline:
            if not (b0 - 1e-6 <= st < b0 + bars * 4 - 1e-6):
                continue
            r = root_of(name, "C2", "B2", tr)
            v = voicing(name, top_for(name, tr, "D5"), 3, tr)
            for h in range(int((en - st) / 2)):
                p = st + 2 * h
                self.piano.notes_at([r, r + 12] if h == 0 else [r + 12], self.T(p, 8), 1.9, self.V(72 * vel))
                self.piano.notes_at(v, self.T(p + (.5 if h else 0), 8), 1.4, self.V((70 if h == 0 else 60) * vel))
            self.piano.sustain(st + .02, en - .05)

    def strings(self, b0, bars, vel=1.0, tops=("F#5", "E5", "E5", "D5", "D5", "C#5", "D5", "E5")):
        """Sustained chords: violins the upper two voices, violas the lower two, celli the root."""
        i = 0
        for st, en, name, tr in self.timeline:
            if not (b0 - 1e-6 <= st < b0 + bars * 4 - 1e-6):
                continue
            top = top_for(name, tr, tops[i % len(tops)])
            v = voicing(name, top, 3, tr)
            d = en - st - .05
            for n in v[2:]:
                self.vln.note(n, st + .02, d, self.V(82 * vel))
            for n in v[:2]:
                self.vla.note(n, st + .02, d, self.V(80 * vel))
            self.vc.note(root_of(name, "C3", "B3", tr), st + .02, d, self.V(80 * vel))
            i += 1

    def glock_line(self, b0, line, tr=0, octave=1, vel=1.0):
        b = b0
        for p, d in line:
            if p != "r":
                self.glock.note(note_number(p) + tr + 12 * octave, self.T(b, 3), min(d, 1.0), self.V(92 * vel))
            b += d

    # -- vocal -----------------------------------------------------------------------------------
    def sing(self, b0, melody, tr=0, x=None, harmony=False):
        b = b0
        for p, lyr, d in melody:
            if p != "r":
                n = note_number(p) + tr
                self.vox.note(n, b, d, 100, lyric=lyr, x=dict(x) if x else None)
                if harmony:      # a third above, or below where that would leave the bank's range
                    ch = self.chord_at(b)[2]
                    h = harmony_note(n, ch, tr, below=harmony == "below")
                    if h > note_number("D5"):
                        h = harmony_note(n, ch, tr, below=True)
                    for i, t in enumerate(self.harm):
                        t.note(h, b + .012 * i, d, 92, lyric=lyr)
            b += d
        return b

    def prune(self):
        """Drop tracks that never got a note (nothing to render)."""
        for k in [k for k, t in self.s.tracks.items() if not t.notes]:
            del self.s.tracks[k]

    # -- mix -------------------------------------------------------------------------------------
    def mix(self):
        gtr_eq = [("hpf", 90), ("bell", 220, -2.5, 1.0), ("bell", 500, -1.5, 1.0), ("bell", 3000, 1.0, 1.0),
                  ("lpf", 9000)]
        self.s.mix = {
            "tracks": {
                "kick": {"gain": -6, "eq": [("hpf", 30), ("bell", 60, 2, 1.2), ("bell", 350, -3, 1.0),
                                            ("bell", 4000, 2.5, 1.0)],
                         "comp": {"threshold": -18, "ratio": 4, "attack": 10, "release": 80}, "bus": "drums"},
                "snare": {"gain": -7, "eq": [("hpf", 90), ("bell", 200, 1.5, 1.0), ("bell", 5000, 2.5, 1.0)],
                          "comp": {"threshold": -18, "ratio": 4, "attack": 8, "release": 100}, "bus": "drums",
                          "sends": {"room": -9}},
                "hats": {"gain": -13, "eq": [("hpf", 400), ("hshelf", 8000, 2.0)], "pan": 0.25, "bus": "drums"},
                "cymbals": {"gain": -12.5, "eq": [("hpf", 300), ("hshelf", 9000, 1.5)], "width": 0.75,
                            "bus": "drums"},
                "toms": {"gain": -9, "eq": [("hpf", 70), ("bell", 400, -2, 1.0)], "width": 0.8, "bus": "drums",
                         "sends": {"room": -10}},
                "bass": {"amp": RIG_BASS, "gain": -4.5, "eq": [("hpf", 35), ("bell", 250, -1.5, 1.0),
                                                                ("bell", 800, 1.5, 1.0)],
                         "comp": {"threshold": -20, "ratio": 4, "attack": 6, "release": 80}, "mono": True},
                "guitar L": {"amp": RIG_RHYTHM, "gain": -7.5, "pan": -0.95, "eq": gtr_eq, "bus": "guitars"},
                "guitar R": {"amp": RIG_RHYTHM, "gain": -7.5, "pan": 0.95, "eq": gtr_eq, "bus": "guitars"},
                "lead guitar": {"amp": RIG_LEAD, "gain": -4.5, "pan": 0.1,
                                "eq": [("hpf", 150), ("bell", 300, -2, 1.0), ("bell", 1500, 1.5, 1.0), ("lpf", 8500)],
                                "sends": {"plate": -14, "dly": -14}},
                "arpeggio guitar": {"amp": RIG_EDGE, "gain": -10, "pan": -0.4,
                                    "eq": [("hpf", 160), ("bell", 300, -2, 1.0), ("hshelf", 5000, 1.5)],
                                    "sends": {"plate": -14, "dly": -16}},
                "piano": {"gain": -6.5, "eq": [("hpf", 110), ("bell", 320, -2.5, 1.0), ("hshelf", 6000, 2.0)],
                          "comp": {"threshold": -20, "ratio": 3, "attack": 8, "release": 90},
                          "width": 0.5, "pan": 0.15, "mono_below": 200, "sends": {"plate": -16}},
                "glockenspiel": {"gain": -11, "eq": [("hpf", 600)], "pan": 0.3, "sends": {"plate": -10, "dly": -16}},
                "violins": {"gain": -11, "eq": [("hpf", 200), ("bell", 400, -2, 1.0)], "width": 0.7, "pan": -0.15,
                            "bus": "strings"},
                "violas": {"gain": -12, "eq": [("hpf", 150), ("bell", 400, -2, 1.0)], "width": 0.7, "pan": 0.15,
                           "bus": "strings"},
                "celli": {"gain": -12, "eq": [("hpf", 70), ("bell", 300, -1.5, 1.0)], "width": 0.6, "bus": "strings"},
                "vocal": {"gain": 2.5, "eq": [("hpf", 150), ("bell", 280, -2.5, 1.0), ("bell", 750, -2.0, 1.0),
                                              ("bell", 3200, 2.5, 1.0), ("hshelf", 9000, 2.5)],
                          "comp": {"threshold": -22, "ratio": 3.5, "attack": 4, "release": 70},
                          "sends": {"plate": -11, "dly": -19}},
                "harmony L": {"gain": -9, "eq": [("hpf", 250), ("bell", 750, -3, 1.0), ("hshelf", 8000, 2)],
                              "comp": {"threshold": -24, "ratio": 4, "attack": 5, "release": 80},
                              "pan": -0.45, "sends": {"plate": -6}},
                "harmony R": {"gain": -9, "eq": [("hpf", 250), ("bell", 750, -3, 1.0), ("hshelf", 8000, 2)],
                              "comp": {"threshold": -24, "ratio": 4, "attack": 5, "release": 80},
                              "pan": 0.45, "sends": {"plate": -6}},
            },
            "buses": {
                "drums": {"comp": {"threshold": -16, "ratio": 3, "attack": 15, "release": 120},
                          "saturate": {"drive_db": 2, "mix": 0.4}},
                "guitars": {"comp": {"threshold": -18, "ratio": 2.5, "attack": 20, "release": 150}},
                "strings": {"sends": {"hall": -8}},
            },
            "fx": {
                "plate": {"type": "reverb", "kind": "plate", "decay": 1.6, "predelay": 20, "hpf": 300, "lpf": 9000},
                "room": {"type": "reverb", "kind": "room", "decay": 0.7, "predelay": 5, "hpf": 250, "lpf": 8000},
                "hall": {"type": "reverb", "kind": "hall", "decay": 2.2, "predelay": 25, "hpf": 250, "lpf": 8000},
                "dly": {"type": "delay", "beats": 0.75, "feedback": 0.3, "hpf": 500, "lpf": 5000},
            },
            "master": {"eq": [("bell", 2500, -1.0, 0.8), ("hshelf", 5000, 2.5, 0.7), ("hshelf", 10000, 2.0, 0.7)],
                       "glue": {"threshold": -18, "ratio": 2, "attack": 20, "release": 200}, "target_lufs": -14},
        }


# -- arrangement ------------------------------------------------------------------------------
GROOVE = {"riff": "A", "verse": "B", "chorus": "A", "solo": "C", "last": "A"}   # checkpoint 2 picks
OUTRO_RIFF = RIFF[:-11] + [("D5", .75), ("F#5", .75), ("A5", .5), ("B5", .5), ("A5", .5), ("F#5", .5),
                           ("E5", .5), ("D5", 4.0)]
assert sum(d for _, d in OUTRO_RIFF) == 8 * 4


def tail_from(melody, beat):
    """(pitch, beats) of a sung melody from `beat` on (to double it on an instrument)."""
    out, b = [], 0.0
    for p, _, d in melody:
        if b >= beat - 1e-9:
            out.append((p, d))
        b += d
    return out


def band(a: Arranger, b0, n, groove, part, vel=1.0, fill="toms", crash=True):
    """Drums, bass and rhythm guitars of one groove. part: "verse" (lighter, palm-muted),
    "chorus" (open wall) or "riff"."""
    if groove == "A":
        a.drums_8beat(b0, n, vel=vel, fill=fill, crash=crash, ride=part == "chorus")
        a.bass_8ths(b0, n, vel=vel)
        (a.gtr_chug if part == "verse" else a.gtr_wall)(b0, n, vel=vel)
    elif groove == "B":
        a.drums_four(b0, n, vel=vel, fill=fill, crash=crash)
        a.bass_octaves(b0, n, vel=vel)
        a.gtr_cut(b0, n, vel=vel * (.9 if part == "verse" else 1.0))
    else:
        a.drums_sprint(b0, n, vel=vel, fill=fill, crash=crash)
        a.bass_drive16(b0, n, vel=vel)
        (a.gtr_trem if part != "chorus" else a.gtr_wall)(b0, n, vel=vel)


def compose() -> Song:
    a = Arranger(FORM)
    s = a.s
    fills = iter(["snare", "toms", "flams", "toms", "snare", "flams", "toms", "toms", "flams", "snare",
                  "toms", "flams", "toms", "snare", "toms", "flams"])
    for name, prog, tr in FORM:
        b0, n, tr = a.span(name)
        if name == "intro":              # the riff, quietly: upright piano, glock, crunch arpeggios
            a.piano_riff(b0, RIFF[:26], tr, vel=.75)
            a.glock_line(b0, RIFF[:26], tr, vel=.7)
            a.arpeggio(b0, n, vel=.8)
            a.strings(b0, n, vel=.7)
            a.fill(b0 + 4 * n - 2, "snare")
        elif name in ("riff", "interlude"):
            band(a, b0, n, GROOVE["riff"], "riff", fill=next(fills))
            a.lead_line(b0, RIFF, tr)
            a.glock_line(b0, RIFF, tr)
            a.piano_8ths(b0, n, vel=.75)
        elif name.startswith("verse"):       # dance-rock groove (B); the cutting guitars join halfway
            first = name == "verse 1"
            a.drums_four(b0, 8, vel=.8, fill=False)
            a.bass_octaves(b0, 8, vel=.85)
            if first:
                a.arpeggio(b0, 8, vel=.85)
            else:
                a.gtr_cut(b0, 8, vel=.75)
            band(a, b0 + 32, 8, GROOVE["verse"], "verse", vel=.9, fill=next(fills), crash=False)
            a.arpeggio(b0 + 32, 8, vel=.75 if first else .85)
            a.piano_ballad(b0 + 32, 8, vel=.7)
            a.sing(b0, VERSE_1 if first else VERSE_2, tr)
        elif name.startswith("pre"):
            a.drums_half(b0, 4, vel=.9, fill=False)
            a.drums_8beat(b0 + 16, 3, vel=.95, fill=False, crash=False)
            a.bass_long(b0, 4)
            a.bass_8ths(b0 + 16, 3)
            a.gtr_hold(b0, 7, vel=.95)
            a.strings(b0, 8, vel=.9)
            a.piano_8ths(b0, 7, vel=.75)
            last = b0 + 28                     # bar 8: one hit, silence under "ねえ", a roll in
            a.gtr_hits([last], dur=.9)
            a.crash(last)
            a.bass.note(root_of("A", tr=tr), last, .9, 112)
            a.fill(last + 2, "snare", beats=2)
            a.sing(b0, PRE_1 if name == "pre 1" else PRE_2, tr)
        elif name.startswith("chorus"):
            band(a, b0, n, GROOVE["chorus"], "chorus", fill=next(fills))
            a.crash(b0 + 32)
            a.piano_8ths(b0, n, vel=.8)
            a.strings(b0, n)
            a.sing(b0, CHORUS_1 if name == "chorus 1" else CHORUS_2, tr, harmony="below")
        elif name == "solo":
            band(a, b0, n, GROOVE["solo"], "riff", fill=next(fills))
            a.crash(b0 + 32)
            a.lead_line(b0, SOLO_LINE, tr, vib_cents=32)
            a.strings(b0 + 32, 8, vel=.9)
            a.piano_arp16(b0 + 32, 8, vel=.75)
        elif name == "bridge":
            a.drums_half(b0, 4, vel=.85, fill=False)
            a.drums_8beat(b0 + 16, 3, vel=.95, fill="toms", crash=True)
            a.bass_long(b0, 4)
            a.bass_8ths(b0 + 16, 3)
            a.gtr_hold(b0 + 16, 3, vel=.9)
            a.piano_ballad(b0, 7)
            a.strings(b0, 8)
            stop = b0 + 28                     # one hit under "を", then the quiet chorus
            a.gtr_hits([stop], dur=2.5)
            a.crash(stop)
            a.bass.note(root_of("A", tr=tr), stop, 2.5, 110)
            a.sing(b0, BRIDGE_MEL, tr)
        elif name == "ochi":                 # quiet chorus: piano and voice, strings creep in
            a.piano_ballad(b0, n, vel=.85)
            a.strings(b0 + 16, 4, vel=.75)
            a.fill(b0 + 30, "toms", beats=2)
            a.gtr_hits([b0 + 30], dur=1.8, vel=.9)
            a.sing(b0, OCHI_MEL, tr)
        elif name == "last chorus":
            band(a, b0, n, GROOVE["last"], "chorus", fill=next(fills))
            for k in (32, 64):
                a.crash(b0 + k)
            a.piano_8ths(b0, n, vel=.85)
            a.strings(b0, n)
            a.glock_line(b0 + 64, tail_from(LAST_MEL, 64), tr, octave=1, vel=.6)
            a.sing(b0, LAST_MEL, tr, harmony="below")
        elif name == "outro":
            band(a, b0, 7, GROOVE["riff"], "riff", fill="toms")
            a.lead_line(b0, OUTRO_RIFF, tr)
            a.glock_line(b0, OUTRO_RIFF, tr)
            end = b0 + 28                      # final chord rings out
            a.gtr_hits([end], dur=6)
            a.crash(end)
            a.bass.note(root_of("D", tr=tr), end, 5, 116)
            a.piano.notes_at([root_of("D", "C2", "B2", tr), root_of("D", "C2", "B2", tr) + 12]
                             + voicing("D", top_for("D", tr, "F#5"), 3, tr), end, 6, 100)
            a.piano.sustain(end + .02, end + 7)
    a.mix()
    a.prune()
    s.length_beats = s.bar(a.total_bars) + 6
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
