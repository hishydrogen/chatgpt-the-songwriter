"""Catalina Blue (working title) - a 1978 West Coast instrumental in the spirit of
"What a Fool Believes" (style, harmony vocabulary, groove and sound only; all material
is original). Eb major, 119 BPM drifting to 122 like a live band (the reference measured
118.9 -> 122), 8th notes at 52:48.

Intro 8 | Verse 16 | Pre 8 | Chorus 16 | Riff 4 | Verse 8 | Pre 8 | Chorus 8 (pivot) |
Bridge 16 (B major, synth solo) | Final chorus 16 (E major) | Outro 8 | Ending 2

The face of the song is the piano riff: left-hand octaves on a 3+3+2 tresillo, the right
hand rocking between two voicings with a top line climbing Bb-C-D-Eb, doubled by an OB-8
(the reference's opening is a Steinway plus an Oberheim). Verses bounce (groove A),
pre-choruses gather on off-beat pushes with two drummers on the backbeat (B), choruses
open into 16ths (C). The chorus floats on IV (Abmaj9) and only lands on I at the very
end; a minor iv (Abm6) gives it the bittersweet turn. Chorus 2 pivots through Abm7 = G#m7
into B major for the bridge, and the bridge's tonic becomes the dominant of E: the final
chorus arrives a half step above the first one. Tenor sax sings the melody; a soft retro
synth takes the bridge solo and doubles the last chorus an octave up; a brass section
(horns + trombones, trumpets for the peaks, harmon mutes for the quiet parts) stands in
for the backing vocals.
"""
import random

from songwriter.instruments import surge
from songwriter.song import Song, note_number

BPM = 119.0
SWING_OFF = 0.02          # 8th off-beats land at 52% of the beat
KIT = "drums.virtuosity"
KIT_CC = {71: 30, 105: 127, 109: 70, 111: 50}   # palette pick B: open room + vintage mic
PIANO = "piano.splendid"
OB = surge("Brass/OB-8 Jump")
RHODES = "epiano.rhodes"
BASS = "bass.darkblack"
GUITAR = "guitar.green_twang"
SAX = "sax.tenor"
SYNTH = surge("Vospi/Leads/Nice And Elegant Retro", portamento_ms=45, play_mode="mono_st_fp")

# chord -> (RH voicing 1, RH voicing 2, left-hand root G2..F#3, pad voicing, safe upper
#           interval above the bass for the bass player)
CH = {
    # riff / verse
    "Abmaj9":    ([60, 63, 67], [63, 67, 70], 44, [60, 63, 67, 70], 7),
    "Bb/Ab":     ([62, 65, 70], [65, 70, 72], 44, [62, 65, 70, 72], 2),
    "Gm7":       ([62, 65, 70], [65, 70, 74], 43, [62, 65, 70, 72], 7),
    "Cm9":       ([63, 67, 70], [67, 70, 74], 48, [62, 63, 67, 70], 7),
    "Fm7/Bb":    ([63, 68, 72], [68, 72, 75], 46, [63, 65, 68, 72], 7),
    # pre-chorus
    "Bbm9":      ([61, 65, 68], [65, 68, 72], 46, [61, 65, 68, 72], 7),
    "Eb13":      ([61, 65, 67], [65, 67, 72], 51, [61, 65, 67, 72], 7),
    "Abmaj7#11": ([60, 63, 67], [63, 67, 74], 44, [60, 63, 67, 74], 7),
    "C7b9":      ([64, 67, 70], [67, 70, 73], 48, [64, 67, 70, 73], 7),
    "Fm9":       ([60, 63, 68], [63, 67, 72], 53, [63, 67, 68, 72], 7),
    "Ab6":       ([60, 63, 65], [63, 65, 68], 44, [60, 63, 65, 68], 7),
    "Am7b5":     ([60, 63, 67], [63, 67, 72], 45, [60, 63, 67, 72], 6),
    "Ab/Bb":     ([63, 68, 72], [68, 72, 75], 46, [60, 63, 68, 72], 7),
    "Bb7b9":     ([62, 65, 68], [65, 68, 71], 46, [62, 65, 68, 71], 7),
    "Bb13":      ([56, 62, 67], [62, 67, 72], 46, [56, 62, 67, 72], 7),   # Ab D G: the pickup's G is the 13th
    # chorus
    "Eb/G":      ([63, 67, 70], [67, 70, 75], 43, [63, 67, 70, 75], 3),
    "Bbm7":      ([61, 65, 68], [65, 68, 73], 46, [61, 65, 68, 72], 7),
    "Eb7b9":     ([61, 64, 67], [64, 67, 73], 51, [61, 64, 67, 70], 7),
    "Abm6":      ([59, 63, 65], [63, 65, 68], 44, [59, 63, 65, 68], 7),
    "Db9":       ([63, 65, 71], [65, 68, 71], 49, [63, 65, 68, 71], 7),
    "Ebmaj9":    ([62, 65, 67], [65, 67, 70], 51, [62, 65, 67, 70], 7),
    # pivot to B
    "Abm7":      ([59, 63, 66], [63, 66, 71], 44, [59, 63, 66, 70], 7),
    "F#13sus":   ([64, 68, 71], [68, 71, 75], 54, [64, 68, 71, 75], 7),
    "F#13":      ([64, 68, 70], [68, 70, 75], 54, [64, 68, 70, 75], 7),
    # bridge (B major)
    "Bmaj9":     ([63, 66, 70], [66, 70, 73], 47, [63, 66, 70, 73], 7),
    "A/B":       ([61, 64, 69], [64, 69, 73], 47, [61, 64, 69, 73], 7),
    "G#m9":      ([63, 66, 70], [66, 70, 75], 44, [63, 66, 70, 71], 7),
    "C#m9":      ([64, 68, 71], [68, 71, 75], 49, [63, 64, 68, 71], 7),
    "Emaj9":     ([63, 66, 68], [66, 68, 71], 52, [63, 66, 68, 71], 7),
    "D#m7":      ([61, 66, 70], [66, 70, 73], 51, [61, 66, 70, 73], 7),
    "G#7b9":     ([60, 63, 66], [63, 66, 69], 44, [60, 63, 66, 69], 7),
    "Emaj7#11":  ([63, 68, 70], [68, 70, 75], 52, [63, 68, 70, 71], 7),
    "F#/E":      ([61, 66, 70], [66, 70, 73], 52, [61, 66, 70, 73], 2),
    "F#m9":      ([61, 64, 68], [64, 69, 73], 54, [61, 64, 68, 69], 7),
    "B13":       ([57, 63, 68], [63, 68, 73], 47, [57, 63, 68, 73], 7),
    # ending
    "E6/9":      ([66, 68, 73], [68, 73, 78], 52, [61, 66, 68, 71], 7),
}

RIFF = ["Abmaj9", "Bb/Ab", "Gm7", ("Cm9", "Fm7/Bb")]
PRE = ["Cm9", ("Bbm9", "Eb13"), "Abmaj7#11", ("Gm7", "C7b9"), "Fm9", "Gm7", ("Ab6", "Am7b5"), ("Ab/Bb", "Bb13")]
CHORUS_A = ["Abmaj9", "Eb/G", "Fm9", ("Gm7", "C7b9"), "Abmaj9", ("Bbm7", "Eb7b9"), "Abm6", ("Ab/Bb", "Bb13")]
CHORUS_B = CHORUS_A[:6] + [("Abm6", "Db9"), "Ebmaj9"]
CHORUS_PIVOT = CHORUS_A[:6] + [("Abm7", "Db9"), ("F#13sus", "F#13")]
BRIDGE = ["Bmaj9", "A/B", "Bmaj9", "A/B", "G#m9", ("C#m9", "F#13"), "Emaj9", ("D#m7", "G#7b9"),
          "C#m9", "D#m7", "Emaj7#11", "F#/E", "C#m9", "F#m9", "A/B", ("A/B", "B13")]

FORM = [  # (name, groove, progression, transpose)
    ("intro", "A", RIFF * 2, 0),
    ("verse 1", "A", RIFF * 4, 0),
    ("pre 1", "B", PRE, 0),
    ("chorus 1", "C", CHORUS_A + CHORUS_B, 0),
    ("riff", "A", RIFF, 0),
    ("verse 2", "A", RIFF * 2, 0),
    ("pre 2", "B", PRE, 0),
    ("chorus 2", "C", CHORUS_PIVOT, 0),
    ("bridge", "R", BRIDGE, 0),
    ("final chorus", "C", CHORUS_A + CHORUS_B, 1),
    ("outro", "A", RIFF * 2, 1),
    ("ending", "-", ["E6/9", "E6/9"], 0),
]

# -- melodies: (bar, beat, pitch, length[, velocity]) relative to the section --------------
VERSE_A = [
    (0, 1.5, "Eb4", 0.5), (0, 2.0, "F4", 0.5), (0, 2.5, "G4", 0.5), (0, 3.0, "Bb4", 1.5),
    (1, 0.5, "Ab4", 0.5), (1, 1.0, "G4", 0.5), (1, 1.5, "F4", 1.5),
    (2, 3.0, "D4", 0.5), (2, 3.5, "F4", 0.5),
    (3, 0.0, "G4", 1.0), (3, 1.0, "F4", 0.5), (3, 1.5, "Eb4", 1.5),
]
VERSE_A2 = [
    (0, 1.5, "Eb4", 0.5), (0, 2.0, "F4", 0.5), (0, 2.5, "G4", 0.5), (0, 3.0, "C5", 1.5),
    (1, 0.5, "Bb4", 0.5), (1, 1.0, "G4", 0.5), (1, 1.5, "Bb4", 1.0), (1, 2.5, "Ab4", 0.5), (1, 3.0, "G4", 1.0),
    (2, 0.0, "F4", 1.5),
    (3, 2.0, "Bb3", 0.5), (3, 2.5, "C4", 0.5), (3, 3.0, "Eb4", 0.5), (3, 3.5, "F4", 0.5),
]
VERSE_B = [
    (0, 0.0, "G4", 1.0), (0, 1.0, "Bb4", 0.5), (0, 1.5, "C5", 1.0), (0, 2.5, "Bb4", 0.5), (0, 3.0, "G4", 0.5), (0, 3.5, "Eb4", 0.5),
    (1, 0.0, "F4", 2.0), (1, 3.0, "D4", 0.5), (1, 3.5, "Eb4", 0.5),
    (2, 0.0, "F4", 0.5), (2, 0.5, "G4", 0.5), (2, 1.0, "Bb4", 1.0), (2, 2.0, "D5", 1.0), (2, 3.0, "C5", 0.5), (2, 3.5, "Bb4", 0.5),
    (3, 0.0, "G4", 1.5), (3, 1.5, "F4", 0.5), (3, 2.0, "Eb4", 1.5),
]
VERSE_C = [
    (0, 1.5, "C5", 0.5), (0, 2.0, "Bb4", 0.5), (0, 2.5, "G4", 0.5), (0, 3.0, "Ab4", 1.0),
    (1, 0.0, "G4", 1.0), (1, 1.0, "F4", 1.0), (1, 2.0, "D4", 1.5),
    (2, 2.0, "Bb3", 0.5), (2, 2.5, "D4", 0.5), (2, 3.0, "F4", 0.5), (2, 3.5, "G4", 0.5),
    (3, 0.0, "Bb4", 1.5), (3, 1.5, "Ab4", 0.5), (3, 2.0, "F4", 1.0), (3, 3.0, "Eb4", 1.0),
]
PRE_MEL = [
    (0, 0.5, "G4", 1.0), (0, 1.5, "F4", 0.5), (0, 2.0, "Eb4", 1.0), (0, 3.0, "D4", 0.5), (0, 3.5, "Eb4", 0.5),
    (1, 0.0, "F4", 1.0), (1, 1.0, "Ab4", 1.0), (1, 2.0, "G4", 1.5), (1, 3.5, "Ab4", 0.5),
    (2, 0.5, "Bb4", 1.0), (2, 1.5, "C5", 0.5), (2, 2.0, "D5", 1.5), (2, 3.5, "C5", 0.5),
    (3, 0.0, "Bb4", 1.5), (3, 1.5, "G4", 0.5), (3, 2.0, "E4", 1.0), (3, 3.0, "G4", 0.5), (3, 3.5, "Bb4", 0.5),
    (4, 0.0, "Ab4", 1.5), (4, 1.5, "G4", 0.5), (4, 2.0, "F4", 1.0), (4, 3.0, "Ab4", 0.5), (4, 3.5, "C5", 0.5),
    (5, 0.0, "Bb4", 1.5), (5, 1.5, "D5", 1.0), (5, 2.5, "C5", 0.5), (5, 3.0, "Bb4", 1.0),
    (6, 0.0, "C5", 1.0), (6, 1.0, "Eb5", 2.0, 108), (6, 3.0, "D5", 0.5), (6, 3.5, "C5", 0.5),
    (7, 0.0, "Bb4", 2.0), (7, 3.0, "G4", 0.5), (7, 3.5, "Ab4", 0.5),
]
HOOK = [  # chorus bars 1-6; the pickup G4 Ab4 sits in the bar before
    (0, 0.0, "Bb4", 1.0, 104), (0, 1.0, "C5", 0.5), (0, 1.5, "Eb5", 2.0, 112), (0, 3.5, "D5", 0.5),
    (1, 0.0, "C5", 0.5), (1, 0.5, "Bb4", 1.5, 104), (1, 2.0, "G4", 0.5), (1, 2.5, "F4", 0.5), (1, 3.0, "G4", 1.0),
    (2, 0.0, "F4", 0.5), (2, 0.5, "Ab4", 1.0), (2, 1.5, "C5", 1.5, 106), (2, 3.0, "Bb4", 0.5), (2, 3.5, "Ab4", 0.5),
    (3, 0.0, "G4", 1.0), (3, 1.0, "Bb4", 0.5), (3, 1.5, "G4", 0.5), (3, 2.0, "E4", 0.5), (3, 2.5, "F4", 0.5),
    (3, 3.0, "G4", 0.5), (3, 3.5, "Ab4", 0.5),
    (4, 0.0, "Bb4", 1.0, 106), (4, 1.0, "C5", 0.5), (4, 1.5, "Eb5", 2.5, 116),
    (5, 0.0, "Db5", 1.0, 110), (5, 1.0, "C5", 0.5), (5, 1.5, "Bb4", 0.5), (5, 2.0, "G4", 1.0), (5, 3.0, "Bb4", 1.0),
]
HOOK_END_A = [  # Abm6 | Ab/Bb Bb7b9 -> back to the top
    (6, 0.0, "B4", 1.5, 108), (6, 1.5, "Bb4", 0.5), (6, 2.0, "Ab4", 1.0), (6, 3.0, "F4", 0.5), (6, 3.5, "Ab4", 0.5),
    (7, 0.0, "F4", 2.0), (7, 2.0, "D4", 1.0), (7, 3.0, "G4", 0.5), (7, 3.5, "Ab4", 0.5),
]
HOOK_END_B = [  # Abm6 Db9 | Ebmaj9: home at last
    (6, 0.0, "B4", 1.0, 108), (6, 1.0, "Bb4", 0.5), (6, 1.5, "Ab4", 0.5), (6, 2.0, "F4", 1.0), (6, 3.0, "Eb4", 0.5),
    (6, 3.5, "F4", 0.5), (7, 0.0, "G4", 3.5, 104),
]
HOOK_END_PIVOT = [  # Abm7 Db9 | F#13sus F#13 -> hands over to the synth in B
    (6, 0.0, "B4", 1.0, 108), (6, 1.0, "Bb4", 0.5), (6, 1.5, "Ab4", 0.5), (6, 2.0, "F4", 1.0), (6, 3.0, "Eb4", 0.5),
    (6, 3.5, "F4", 0.5), (7, 0.0, "C#5", 1.5, 106), (7, 1.5, "B4", 0.5), (7, 2.0, "A#4", 1.0), (7, 3.0, "C#5", 0.5),
    (7, 3.5, "D#5", 2.0, 112),
]
PICKUP = [(-1, 3.0, "G4", 0.5), (-1, 3.5, "Ab4", 0.5)]
SOLO = [  # synth, B major
    (0, 0.5, "F#5", 0.5), (0, 1.0, "G#5", 0.5), (0, 1.5, "B5", 1.5), (0, 3.0, "A#5", 0.5), (0, 3.5, "G#5", 0.5),
    (1, 0.0, "F#5", 1.0), (1, 1.0, "E5", 0.5), (1, 1.5, "C#5", 1.5), (1, 3.0, "E5", 0.5), (1, 3.5, "F#5", 0.5),
    (2, 0.0, "G#5", 0.5), (2, 0.5, "A#5", 0.5), (2, 1.0, "B5", 0.5), (2, 1.5, "C#6", 1.0), (2, 2.5, "D#6", 1.5),
    (3, 0.0, "C#6", 0.5), (3, 0.5, "B5", 0.5), (3, 1.0, "A5", 1.0), (3, 2.0, "F#5", 0.5), (3, 2.5, "E5", 0.5), (3, 3.0, "C#5", 1.0),
    (4, 0.0, "D#5", 1.5), (4, 1.5, "F#5", 0.5), (4, 2.0, "A#5", 1.0), (4, 3.0, "B5", 0.5), (4, 3.5, "A#5", 0.5),
    (5, 0.0, "G#5", 1.0), (5, 1.0, "E5", 0.5), (5, 1.5, "D#5", 0.5), (5, 2.0, "E5", 0.5), (5, 2.5, "F#5", 0.5), (5, 3.0, "A#5", 1.0),
    (6, 0.0, "B5", 1.5), (6, 1.5, "G#5", 0.5), (6, 2.0, "F#5", 0.5), (6, 2.5, "D#5", 0.5), (6, 3.0, "E5", 1.0),
    (7, 0.0, "F#5", 1.0), (7, 1.0, "A#5", 1.0), (7, 2.0, "C6", 0.5), (7, 2.5, "A5", 0.5), (7, 3.0, "G#5", 0.5), (7, 3.5, "F#5", 0.5),
    (8, 0.0, "E5", 0.25), (8, 0.25, "G#5", 0.25), (8, 0.5, "B5", 0.25), (8, 0.75, "D#6", 0.25), (8, 1.0, "E6", 1.5),
    (8, 2.5, "D#6", 0.5), (8, 3.0, "B5", 1.0),
    (9, 0.0, "C#6", 1.0), (9, 1.0, "A#5", 0.5), (9, 1.5, "F#5", 0.5), (9, 2.0, "G#5", 1.0), (9, 3.0, "A#5", 1.0),
    (10, 0.0, "B5", 0.5), (10, 0.5, "C#6", 0.5), (10, 1.0, "D#6", 0.5), (10, 1.5, "E6", 0.5), (10, 2.0, "A#5", 2.0),
    (11, 0.0, "C#6", 1.5), (11, 1.5, "A#5", 0.5), (11, 2.0, "F#5", 1.0), (11, 3.0, "G#5", 0.5), (11, 3.5, "A#5", 0.5),
    (12, 0.0, "B5", 2.0), (12, 2.0, "G#5", 0.5), (12, 2.5, "E5", 0.5), (12, 3.0, "D#5", 1.0),
    (13, 0.0, "A5", 1.0), (13, 1.0, "G#5", 0.5), (13, 1.5, "E5", 0.5), (13, 2.0, "F#5", 1.5), (13, 3.5, "G#5", 0.5),
    (14, 0.0, "A5", 0.5), (14, 0.5, "B5", 0.5), (14, 1.0, "C#6", 1.0), (14, 2.0, "E6", 3.0, 120),
    (15, 1.0, "C#6", 0.5), (15, 1.5, "B5", 0.5), (15, 2.0, "A5", 0.5), (15, 2.5, "F#5", 0.5), (15, 3.0, "D#5", 1.0),
]
TEASER = [  # intro: the hook's opening, an octave up on the synth
    (-1, 3.0, "F5", 0.5), (-1, 3.5, "Ab5", 0.5),
    (0, 0.0, "Bb5", 1.0), (0, 1.0, "C6", 0.5), (0, 1.5, "Eb6", 2.0), (0, 3.5, "D6", 0.5),
    (1, 0.0, "C6", 0.5), (1, 0.5, "Bb5", 1.5), (1, 2.0, "G5", 0.5), (1, 2.5, "F5", 0.5), (1, 3.0, "G5", 1.0),
    (3, 2.0, "F5", 0.5), (3, 2.5, "G5", 0.5), (3, 3.0, "Bb5", 1.0),
]
OUTRO_SAX = [  # E major, over the riff
    (0, 1.5, "E4", 0.5), (0, 2.0, "F#4", 0.5), (0, 2.5, "G#4", 0.5), (0, 3.0, "C#5", 1.5),
    (1, 0.5, "B4", 0.5), (1, 1.0, "G#4", 0.5), (1, 1.5, "B4", 1.0), (1, 2.5, "A4", 0.5), (1, 3.0, "G#4", 1.0),
    (2, 0.0, "F#4", 0.5), (2, 0.5, "G#4", 0.5), (2, 1.0, "B4", 1.0), (2, 2.0, "D#5", 1.0), (2, 3.0, "C#5", 0.5), (2, 3.5, "B4", 0.5),
    (3, 0.0, "G#4", 1.5), (3, 1.5, "F#4", 0.5), (3, 2.0, "E4", 1.5),
    (4, 1.5, "C#5", 0.5), (4, 2.0, "B4", 0.5), (4, 2.5, "G#4", 0.5), (4, 3.0, "A4", 1.0),
    (5, 0.0, "G#4", 1.0), (5, 1.0, "F#4", 1.0), (5, 2.0, "D#4", 1.5),
    (6, 2.0, "B3", 0.5), (6, 2.5, "D#4", 0.5), (6, 3.0, "F#4", 0.5), (6, 3.5, "G#4", 0.5),
    (7, 0.0, "B4", 1.5), (7, 1.5, "A4", 0.5), (7, 2.0, "F#4", 1.0), (7, 3.0, "E4", 0.5),
    (7, 3.5, "F#4", 0.5), (8, 0.0, "G#4", 7.0, 100),
]
RIFF_LICK = [  # guitar double-stops over the 4-bar riff interlude
    (0, 0.5, [67, 72], 0.5), (0, 1.0, [70, 75], 1.0), (0, 2.5, [68, 72], 0.5), (0, 3.0, [67, 70], 1.0),
    (1, 0.5, [65, 70], 0.5), (1, 1.0, [67, 72], 1.5), (1, 3.0, [65, 70], 0.5), (1, 3.5, [62, 67], 0.5),
    (2, 0.0, [62, 65], 1.0), (2, 1.5, [65, 70], 0.5), (2, 2.0, [67, 72], 0.5), (2, 2.5, [70, 74], 1.5),
    (3, 0.5, [67, 70], 0.5), (3, 1.0, [63, 67], 1.0), (3, 2.5, [63, 68], 0.5), (3, 3.0, [65, 68], 1.0),
]


class Arranger:
    def __init__(self):
        s = self.s = Song("Catalina Blue", bpm=BPM, key="Eb")
        self.rng = random.Random(1978)
        drums = ("kick", "snare", "snare 2", "hats", "toms", "cymbals", "perc")
        self.kick, self.snare, self.snare2, self.hats, self.toms, self.cym, self.perc = (
            s.track(n, KIT) for n in drums)
        for t in (self.kick, self.snare, self.snare2, self.hats, self.toms, self.cym, self.perc):
            for cc, v in KIT_CC.items():
                t.cc(cc, v, 0)
        self.piano = s.track("piano", PIANO)
        self.ob = s.track("OB-8", OB)
        self.rhodes = s.track("rhodes", RHODES)
        self.bass = s.track("bass", BASS)
        self.gtr = s.track("guitar", GUITAR)
        self.tbn = s.track("trombones", "brass.trombone_sus")
        self.hn = s.track("horns", "brass.horn_sus")
        self.tpt = s.track("trumpets", "brass.trumpet_sus")
        self.harmon = s.track("harmon trumpets", "brass.trumpet_harmon")
        self.tbn_st = s.track("trombone stabs", "brass.trombone_stac")
        self.hn_st = s.track("horn stabs", "brass.horn_stac")
        self.tpt_st = s.track("trumpet stabs", "brass.trumpet_stac")
        self.sax = s.track("tenor sax", SAX)
        self.syn = s.track("synth lead", SYNTH)
        self.sec = {}          # name -> (first bar, bars, transpose)
        self.timeline = []     # (start beat, end beat, chord name, transpose)
        bar = 0
        for name, groove, prog, tr in FORM:
            self.sec[name] = (bar, len(prog), tr, groove)
            for i, entry in enumerate(prog):
                b0 = s.bar(bar + i)
                if isinstance(entry, tuple):
                    self.timeline += [(b0, b0 + 2, entry[0], tr), (b0 + 2, b0 + 4, entry[1], tr)]
                else:
                    self.timeline.append((b0, b0 + 4, entry, tr))
            bar += len(prog)
        self.total_bars = bar

    # -- timing and lookup -------------------------------------------------------------
    def T(self, beat, sd=4.0, bias=0.0):
        """Performed time of a written beat: 52% swing on the 8th off-beats plus a human
        timing error (sd and push/lag in milliseconds)."""
        if abs((beat * 2) % 2 - 1) < 1e-6:
            beat += SWING_OFF
        return max(0.0, beat + self.rng.gauss(bias, sd) / 1000 * self.s.bpm_at(beat) / 60)

    def V(self, vel, spread=4):
        return int(max(1, min(127, round(vel + self.rng.randint(-spread, spread)))))

    def chord_at(self, beat):
        for st, en, name, tr in self.timeline:
            if st <= beat + 1e-6 < en:
                return st, en, name, tr
        return self.timeline[-1]

    def ch(self, beat):
        """(v1, v2, root, pad, fifth) of the chord sounding at `beat`, transposed."""
        st, en, name, tr = self.chord_at(beat)
        v1, v2, root, pad, fifth = CH[name]
        return [p + tr for p in v1], [p + tr for p in v2], root + tr, [p + tr for p in pad], fifth

    def bars(self, name):
        b0, n, tr, groove = self.sec[name]
        return self.s.bar(b0), n, tr

    def spans(self, start, end):
        return [c for c in self.timeline if c[0] >= start - 1e-6 and c[0] < end - 1e-6]

    # -- keys ------------------------------------------------------------------------------
    def keys_bounce(self, start, n_bars, vel=1.0, ob=True, last_push=True):
        """Groove A: left-hand octaves on 1, 2&, 4; right hand rocking v1/v2 on the other
        8ths; the next chord pushed on 4&."""
        for bar in range(n_bars):
            o = start + bar * 4
            for pos in (0.0, 1.5, 3.0):
                # the left hand anticipates a chord that changes on the next beat
                look = pos + 0.5 if self.chord_at(o + pos + 0.5)[0] == o + pos + 0.5 else pos
                v1, v2, root, pad, _ = self.ch(o + look)
                d, v = {0.0: (0.75, 100), 1.5: (0.45, 88), 3.0: (0.45, 92)}[pos]
                self.piano.notes_at([root - 12, root], self.T(o + pos, 5), d, self.V(v * vel))
            for pos, which, d, v in ((0.5, 0, 0.3, 84), (1.0, 1, 0.45, 100), (2.0, 0, 0.3, 82), (2.5, 1, 0.3, 90)):
                voicing = self.ch(o + pos)[which]
                t = self.T(o + pos, 5)
                self.piano.notes_at(voicing, t, d, self.V(v * vel))
                if ob:
                    self.ob.notes_at(voicing, t, d, self.V(v * vel - 12))
            if bar < n_bars - 1 or last_push:
                voicing = self.ch(o + 4.0)[0]
                t = self.T(o + 3.5, 5, -3)
                self.piano.notes_at(voicing, t, 0.85, self.V(104 * vel))
                if ob:
                    self.ob.notes_at(voicing, t, 0.85, self.V(104 * vel - 12))
            for st, en, *_ in self.spans(o, o + 4):
                self.piano.sustain(st + 0.02, st + 0.45)

    def keys_pushes(self, start, n_bars, vel=1.0, inst=None, ob=False):
        """Groove B: held chords on the off-beats, the next chord pushed across the bar."""
        inst = inst or self.piano
        for st, en, *_ in self.spans(start, start + n_bars * 4):
            _, _, root, pad, fifth = self.ch(st)
            length = en - st
            hits = [(0.5, 1.0, 90), (1.5, 0.45, 80), (2.5, 0.9, 88)] if length == 4 else \
                   [(0.5, 1.0, 88)] if st % 4 == 0 else [(0.5, 0.45, 84)]
            for pos, d, v in hits:
                t = self.T(st + pos, 6, 3)
                inst.notes_at(pad, t, d, self.V(v * vel))
                if ob:
                    self.ob.notes_at(pad, t, d, self.V(v * vel - 14))
            if inst is self.piano:
                self.piano.notes_at([root - 12, root], self.T(st, 5), 1.4 if length == 4 else 1.0, self.V(98 * vel))
                if length == 4:
                    up = root + fifth if fifth == 7 else root
                    up -= 12 if up > 55 else 0
                    self.piano.notes_at([up - 12, up], self.T(st + 2, 5), 1.0, self.V(86 * vel))
            if en % 4 == 0 and en < start + n_bars * 4:
                t = self.T(en - 0.5, 6, -4)
                inst.notes_at(self.ch(en)[3], t, 1.2, self.V(104 * vel))
            inst.sustain(st + 0.02, en - 0.08)

    def keys_16ths(self, start, n_bars, vel=1.0):
        """Groove C: right hand pulsing x.xx 16ths, left hand octaves on 1 and 3 with 16th pickups."""
        for bar in range(n_bars):
            o = start + bar * 4
            for beat in range(4):
                for frac, which, v in ((0.0, 0, 80), (0.5, 1, 96), (0.75, 0, 70)):
                    pos = beat + frac
                    self.piano.notes_at(self.ch(o + pos)[which], self.T(o + pos, 4), 0.18, self.V(v * vel, 5))
            for pos, d, v in ((0.0, 0.9, 98), (1.75, 0.2, 84), (2.0, 0.9, 98), (3.75, 0.2, 84)):
                look = pos + 0.25 if pos % 1 else pos
                root = self.ch(o + look)[2]
                self.piano.notes_at([root - 12, root], self.T(o + pos, 4), d, self.V(v * vel))

    def rhodes_pad(self, start, n_bars, vel=56):
        for st, en, *_ in self.spans(start, start + n_bars * 4):
            self.rhodes.notes_at(self.ch(st)[3], self.T(st, 8), en - st - 0.1, self.V(vel, 3))
            self.rhodes.sustain(st + 0.05, en - 0.05)

    # -- bass ------------------------------------------------------------------------------
    def approach(self, cur, nxt, k):
        if nxt == cur:
            return cur + 7 if cur + 7 <= 47 else cur - 5
        return nxt - 1 if k % 2 == 0 else nxt + 1

    def bass_part(self, start, n_bars, style, vel=1.0):
        k = 0
        for st, en, *_ in self.spans(start, start + n_bars * 4):
            _, _, root, _, fifth = self.ch(st)
            r = root - 12
            nxt = self.ch(en)[2] - 12
            up = r + fifth
            full = en - st == 4
            if style == "A":
                pat = [(0, r, 0.9, 106), (1.5, r, 0.4, 90), (2.0, up, 0.45, 96), (3.0, r + 12, 0.35, 92),
                       (3.5, self.approach(r, nxt, k), 0.45, 92)] if full else \
                      [(0, r, 0.9, 104), (1.5, r if st % 4 == 0 else up, 0.4, 90)] if st % 4 == 0 else \
                      [(0, r, 0.9, 102), (1.0, r, 0.4, 90), (1.5, self.approach(r, nxt, k), 0.45, 92)]
            elif style == "B":
                pat = [(0, r, 1.4, 106), (1.5, r + 12, 0.2, 84), (1.75, up, 0.2, 80), (2.0, r, 0.9, 98),
                       (3.0, up, 0.4, 90), (3.5, self.approach(r, nxt, k), 0.4, 92)] if full else \
                      [(0, r, 1.4, 104)] if st % 4 == 0 else \
                      [(0, r, 0.9, 100), (1.0, up, 0.4, 88), (1.5, self.approach(r, nxt, k), 0.4, 92)]
            elif style == "C":
                notes = [r, r, r + 12, r, r, r + 12, up, self.approach(r, nxt, k)]
                pat = [(i * 0.5, notes[i if full else (i + (4 if st % 4 else 0)) % 8], 0.42, 104 if i % 2 == 0 else 90)
                       for i in range(int((en - st) * 2))]
                if not full and st % 4 == 0:
                    pat = [(i * 0.5, [r, r, r + 12, r][i], 0.42, 104 if i % 2 == 0 else 90) for i in range(4)]
                elif not full:
                    pat = [(i * 0.5, [r, r + 12, up, self.approach(r, nxt, k)][i], 0.42, 100 if i % 2 == 0 else 88)
                           for i in range(4)]
            else:  # bridge: syncopated, Latin-tinged
                pat = [(0, r, 0.7, 104), (0.75, r, 0.2, 80), (1.5, up, 0.45, 92), (2.5, r, 0.4, 94),
                       (3.0, r + 12, 0.4, 88), (3.5, self.approach(r, nxt, k), 0.45, 90)] if full else \
                      [(0, r, 0.7, 102), (0.75, r, 0.2, 80), (1.5, self.approach(r, nxt, k), 0.45, 90)]
            for pos, n, d, v in pat:
                if st + pos < start + n_bars * 4:
                    self.bass.note(n, self.T(st + pos, 5, 2), d, self.V(v * vel))
            k += 1

    # -- drums -----------------------------------------------------------------------------
    def groove(self, start, n_bars, style, vel=1.0, double=False, tamb=False, congas=False,
               open_every=4, crash=True, skip_last=2.0):
        """One section of drums. The last bar stops at `skip_last` beats for the fill."""
        kicks = {"A": [(0, 1.5, 2.0), (0, 2.0, 3.5), (0, 1.5, 2.0), (0, 2.0, 2.5)],
                 "B": [(0, 2.0, 2.5), (0, 1.75, 2.0)],
                 "C": [(0, 1.5, 2.0, 3.25), (0, 0.75, 2.0, 3.5)],
                 "R": [(0, 1.5, 2.5), (0, 2.0, 3.5)]}[style]
        ghosts = {"A": [(1.75, 3.75), (0.75, 2.5, 3.75)], "B": [(2.75,), (1.75, 3.25)],
                  "C": [(0.75, 1.75, 2.25, 3.75), (1.25, 1.75, 2.75, 3.5)], "R": [(1.75,), (3.75,)]}[style]
        if crash:
            self.cym.hit("crash", self.T(start, 4), self.V(108 * vel))
        for bar in range(n_bars):
            o = start + bar * 4
            last = bar == n_bars - 1
            stop = skip_last if last else 4.0
            for pos in kicks[bar % len(kicks)]:
                if pos < stop:
                    self.kick.hit("kick", self.T(o + pos, 4), self.V((112 if pos == 0 else 94) * vel))
            for pos in (1.0, 3.0):
                if pos < stop:
                    hit = "sidestick" if style == "R" and bar < 8 else "snare"
                    self.snare.hit(hit, self.T(o + pos, 4, 4), self.V(116 * vel))
                    if double:
                        self.snare2.hit("snare", self.T(o + pos, 5, 14), self.V(104 * vel))
            for pos in ghosts[bar % 2]:
                if pos < stop and not (style == "R" and bar < 8):
                    self.snare.hit("snare", self.T(o + pos, 6), self.V(32 * vel, 6))
            step = 0.25 if style == "C" else 0.5
            for k in range(int(4 / step)):
                pos = k * step
                if pos >= stop:
                    break
                if style == "R":
                    hit = "ride_bell" if k % 2 == 0 and k % 4 == 0 else "ride"
                    self.cym.hit(hit, self.T(o + pos, 4, 2 if k % 2 else 0), self.V((92 if k % 2 == 0 else 74) * vel))
                    continue
                if style == "C":
                    v = (100, 58, 84, 56)[k % 4]
                else:
                    v = 98 if k % 2 == 0 else 74
                hit = "hh_half" if (bar % open_every == open_every - 1 and pos == 3.5) else "hh_closed"
                self.hats.hit(hit, self.T(o + pos, 4, 2 if (pos * 2) % 2 else 0), self.V(v * vel, 5))
            if tamb:
                for k in range(8):
                    pos = k * 0.5
                    if pos < stop:
                        self.perc.hit("tambourine", self.T(o + pos, 5, 3), self.V((88 if k in (2, 6) else 62) * vel))
            if congas:
                for pos, hit, v in ((0.75, "conga_mute", 70), (1.25, "conga_hi", 84), (1.5, "conga_hi", 74),
                                    (2.75, "conga_mute", 68), (3.0, "conga_lo", 86), (3.5, "conga_hi", 78)):
                    if pos < stop:
                        self.perc.hit(hit, self.T(o + pos, 6), self.V(v * vel, 6))

    def fill(self, at, kind, vel=1.0):
        """Fills differ per section. `at` = beat where the fill starts."""
        F = {
            "pickup": [(0.5, "snare", 70), (0.75, "snare", 84), (1.0, "snare", 96), (1.25, "snare", 104)],
            "small": [(0.0, "snare", 100), (0.5, "snare", 60), (0.75, "tom_high", 96), (1.25, "tom_low", 104),
                      (1.5, "kick", 100)],
            "toms_down": [(0.0, "tom_high", 104), (0.5, "tom_high", 96), (1.0, "tom_low", 110), (1.5, "tom_low", 100)],
            "build": [(k * 0.25, "snare", 56 + k * 7) for k in range(8)],
            "rolling": [(0.0, "tom_high", 108), (0.25, "tom_high", 96), (0.5, "tom_high", 92), (0.75, "tom_low", 108),
                        (1.0, "tom_low", 100), (1.25, "tom_low", 96), (1.5, "snare", 112), (1.75, "kick", 104)],
            "drag": [(0.0, "snare", 92), (0.25, "snare", 40), (0.5, "snare", 100), (1.0, "tom_low", 104),
                     (1.5, "snare", 108)],
            "big": [(k * 0.25, ("snare", "snare", "tom_high", "tom_high", "tom_high", "tom_low", "tom_low", "tom_low")[k],
                     88 + k * 4) for k in range(8)],
            "long": [(k * 0.25, "snare", 40 + k * 5) for k in range(12)] +
                    [(3.0, "tom_high", 112), (3.25, "tom_high", 104), (3.5, "tom_low", 118), (3.75, "tom_low", 110)],
            "flam": [(0.0, "snare", 90), (0.04, "snare", 112), (1.0, "ride_bell", 96)],
            "tag": [(0.5, "snare", 64), (0.75, "tom_high", 92)],
            "end": [(0.0, "tom_high", 110), (0.25, "tom_high", 100), (0.5, "tom_low", 116), (0.75, "tom_low", 108),
                    (1.0, "snare", 120), (1.5, "snare", 112)],
        }[kind]
        for pos, hit, v in F:
            tr = self.toms if hit.startswith("tom") else self.kick if hit == "kick" else \
                self.cym if hit.startswith("ride") else self.snare
            tr.hit(hit, self.T(at + pos, 5), self.V(v * vel))

    # -- guitar, brass ---------------------------------------------------------------------
    def guitar_part(self, start, n_bars, style, vel=1.0):
        for bar in range(n_bars):
            o = start + bar * 4
            if style == "A":
                for pos, d, v in ((1.0, 0.15, 98), (1.75, 0.1, 64), (2.5, 0.2, 86), (3.0, 0.15, 94), (3.75, 0.1, 66)):
                    self.gtr.notes_at(self.ch(o + pos)[1], self.T(o + pos, 5), d, self.V(v * vel), strum=0.012)
            elif style == "B":
                for pos, d, v in ((1.5, 0.3, 90), (3.5, 0.25, 84)):
                    self.gtr.notes_at(self.ch(o + pos + 0.5)[1], self.T(o + pos, 5), d, self.V(v * vel), strum=0.012)
            elif style == "C":
                for k in range(16):
                    pos = k * 0.25
                    v = 92 if k % 4 == 2 else 52 if k % 2 else 66
                    self.gtr.notes_at(self.ch(o + pos)[1], self.T(o + pos, 4), 0.07, self.V(v * vel, 6), strum=0.006)
            elif style == "arp":
                for k in range(8):
                    pos = k * 0.5
                    pad = self.ch(o + pos)[3]
                    self.gtr.note(pad[(0, 1, 2, 3, 2, 1, 2, 3)[k]] + 12, self.T(o + pos, 6), 0.45, self.V(70 * vel, 6))

    def brass_pads(self, start, n_bars, kind, vel=1.0, swell=(72, 112, 96), late=0.25):
        lo_tr, hi_tr = {"A": (self.tbn, self.hn), "B": (self.tbn, self.tpt), "C": (self.hn, self.harmon),
                        "T": (None, self.tpt)}[kind]
        for st, en, *_ in self.spans(start, start + n_bars * 4):
            pad = self.ch(st)[3]
            t = self.T(st + late, 8)
            d = en - st - late - 0.1
            for tr_, notes in ((lo_tr, pad[:2]), (hi_tr, pad[2:])):
                if tr_ is None:
                    continue
                tr_.notes_at(notes, t, d, self.V(86 * vel))
                tr_.cc_ramp(11, st + late, st + late + d * 0.45, swell[0], swell[1])
                tr_.cc_ramp(11, st + late + d * 0.45, st + late + d, swell[1], swell[2])

    def brass_hits(self, beats, kind, dur=0.35, vel=104):
        """Short section hits on the staccato samples (own tracks, so pads keep their swells)."""
        lo_tr, hi_tr = {"A": (self.tbn_st, self.hn_st), "B": (self.tbn_st, self.tpt_st)}[kind]
        for b in beats:
            pad = self.ch(b + 0.5 if (b * 2) % 2 == 1 else b)[3]
            t = self.T(b, 5)
            for tr_, notes in ((lo_tr, pad[:2]), (hi_tr, pad[2:])):
                tr_.notes_at(notes, t, dur, self.V(vel))

    # -- leads -----------------------------------------------------------------------------
    def play(self, track, start, phrase, tr=0, vel=96, sax=True, octave=0):
        notes = sorted(((start + b * 4 + p, note_number(n) + tr + 12 * octave, d, rest[0] if rest else vel)
                        for b, p, n, d, *rest in phrase))
        if sax:
            track.cc(64, 127, notes[0][0] - 0.5).cc(80, 60, notes[0][0] - 0.5).cc(1, 0, notes[0][0] - 0.5)
        for i, (beat, pitch, d, v) in enumerate(notes):
            nxt = notes[i + 1][0] if i + 1 < len(notes) else None
            legato = nxt is not None and nxt - (beat + d) < 0.05
            t = self.T(beat, 6, 3)
            length = (nxt - beat + 0.06) if legato else d - 0.04
            phrase_start = i == 0 or notes[i - 1][0] + notes[i - 1][2] < beat - 0.05
            track.note(pitch, t, length, self.V(v, 3))
            if sax:
                track.cc(11, min(127, 96 + (v - 96)), t - 0.01)
                if phrase_start and d >= 0.5:   # scoop into the first note of a phrase
                    track.bend(-1600, t - 0.005).bend(-500, t + 0.06).bend(0, t + 0.14)
                if d >= 1.0:
                    track.cc_ramp(1, t + 0.35, t + d, 0, 76, step=0.25).cc(1, 0, t + d + 0.02)
                    track.cc_ramp(11, t + 0.1, t + d * 0.6, 100 + (v - 96), 112 + (v - 96), step=0.25)
            elif d >= 1.0:
                track.vibrato(t + 0.3, t + d, rate_hz=5.2, cents=14)

    # -- sections --------------------------------------------------------------------------
    def intro(self):
        st, n, tr = self.bars("intro")
        self.s.marker(st, "intro")
        self.keys_bounce(st, 8, vel=0.92)
        # hats come in on bar 3, the band on bar 5
        for bar in (2, 3):
            for k in range(8):
                self.hats.hit("hh_closed", self.T(st + bar * 4 + k * 0.5, 4), self.V(84 if k % 2 == 0 else 62))
        self.fill(st + 3 * 4 + 2.5, "pickup", 0.9)
        self.bass_part(st + 8, 6, "A", vel=0.95)
        self.groove(st + 16, 4, "A", vel=0.92)
        self.fill(st + 7 * 4 + 2.0, "small")
        self.guitar_part(st + 16, 4, "A", vel=0.85)
        self.rhodes_pad(st + 16, 4, vel=50)
        self.play(self.syn, st + 16, TEASER, vel=86, sax=False)

    def verse(self, name, phrases, extra=False):
        st, n, tr = self.bars(name)
        self.s.marker(st, name)
        self.keys_bounce(st, n)
        self.bass_part(st, n, "A")
        self.groove(st, n, "A", crash=True, congas=extra, open_every=4)
        self.fill(st + (n - 1) * 4 + 2.0, "toms_down" if not extra else "rolling")
        self.rhodes_pad(st, n, vel=54 if not extra else 60)
        self.guitar_part(st + (0 if extra else 32), n - (0 if extra else 8), "A", vel=0.9)
        if not extra:
            self.fill(st + 7 * 4 + 3.0, "tag", 0.9)
        else:
            self.brass_pads(st + 16, n - 4, "C", vel=0.8, swell=(64, 96, 84))
        for i, ph in enumerate(phrases):
            self.play(self.sax, st + i * 32, ph, vel=92)

    def pre(self, name, last=False):
        st, n, tr = self.bars(name)
        self.s.marker(st, name)
        self.keys_pushes(st, n, ob=True)
        self.keys_pushes(st, n, vel=0.7, inst=self.rhodes)
        self.bass_part(st, n, "B")
        self.groove(st, n, "B", double=True, congas=True, crash=False, skip_last=0.0 if last else 2.0)
        self.fill(st + (n - 1) * 4 + (0.0 if last else 2.0), "long" if last else "build")
        self.guitar_part(st, n, "B")
        self.brass_pads(st + 16, 4, "A", vel=0.9, swell=(64, 104, 112))
        if last:
            self.brass_hits([st + (n - 1) * 4 + 3.5], "B", dur=0.5, vel=110)
        self.play(self.sax, st, PRE_MEL, vel=96)

    def chorus(self, name, ending="B"):
        st, n, tr = self.bars(name)
        self.s.marker(st, name)
        final = name == "final chorus"
        self.keys_16ths(st, n, vel=1.0)
        self.bass_part(st, n, "C")
        self.groove(st, n, "C", tamb=True, double=final, open_every=2, skip_last=2.0)
        if n == 16:
            self.cym.hit("crash", self.T(st + 32, 4), self.V(104))
        self.guitar_part(st, n, "C", vel=0.85)
        self.rhodes_pad(st, n, vel=58)
        self.brass_pads(st, n, "A", vel=1.0)
        if final:
            self.brass_pads(st, n, "T", vel=0.95, swell=(80, 118, 104))
        # brass answers while the sax holds its long notes
        for half in range(n // 8):
            o = st + half * 32
            self.brass_hits([o + 16 + 3.0, o + 16 + 3.5], "B" if final else "A", dur=0.3)
            if half == 0 and n == 16:
                self.brass_hits([o + 28 + 3.5], "B" if final else "A", dur=0.5)
        passes = [HOOK + HOOK_END_A, HOOK + HOOK_END_B] if n == 16 else [HOOK + HOOK_END_PIVOT]
        for i, ph in enumerate(passes):
            self.play(self.sax, st + i * 32, ph, tr=tr, vel=100)
            if final and i == 1:   # the synth doubles the last pass an octave up
                self.play(self.syn, st + i * 32, ph, tr=tr, vel=80, sax=False, octave=1)
        kind = {"chorus 1": "big", "chorus 2": "big", "final chorus": "rolling"}[name]
        self.fill(st + (n - 1) * 4 + 2.0, kind)
        if n == 16:
            self.fill(st + 7 * 4 + 2.0, "small")

    def riff(self):
        st, n, tr = self.bars("riff")
        self.s.marker(st, "riff")
        self.keys_bounce(st, n)
        self.bass_part(st, n, "A")
        self.groove(st, n, "A", skip_last=2.0)
        self.fill(st + (n - 1) * 4 + 2.0, "drag")
        self.rhodes_pad(st, n, vel=54)
        for b, p, notes, d in RIFF_LICK:
            self.gtr.notes_at(notes, self.T(st + b * 4 + p, 6), d, self.V(96))

    def bridge(self):
        st, n, tr = self.bars("bridge")
        self.s.marker(st, "bridge (B major)")
        self.keys_pushes(st, n, vel=0.85, inst=self.rhodes)
        for st_, en_, *_ in self.spans(st, st + n * 4):   # the piano only marks the changes
            self.piano.notes_at(self.ch(st_)[3], self.T(st_, 5), min(2.0, en_ - st_), self.V(76))
            root = self.ch(st_)[2]
            self.piano.notes_at([root - 12, root], self.T(st_, 5), min(2.0, en_ - st_), self.V(84))
            self.piano.sustain(st_ + 0.02, en_ - 0.1)
        self.bass_part(st, n, "R")
        self.groove(st, n, "R", congas=True, crash=True, skip_last=0.0)
        self.fill(st + 7 * 4 + 3.0, "flam")
        self.fill(st + (n - 1) * 4, "long")
        self.guitar_part(st, n - 4, "arp", vel=0.9)
        self.brass_pads(st, 8, "C", vel=0.75, swell=(60, 90, 80))
        self.brass_pads(st + 48, 4, "B", vel=1.0, swell=(70, 120, 124))
        self.cym.hit("crash", self.T(st + 48, 4), self.V(100))
        self.play(self.syn, st, SOLO, vel=98, sax=False)
        self.play(self.sax, st + n * 4, PICKUP, tr=1, vel=100)

    def outro(self):
        st, n, tr = self.bars("outro")
        self.s.marker(st, "outro")
        self.keys_bounce(st, n, last_push=True)
        self.bass_part(st, n, "A")
        self.groove(st, n, "A", tamb=True, double=True, skip_last=2.0)
        self.fill(st + (n - 1) * 4 + 2.0, "end")
        self.rhodes_pad(st, n, vel=56)
        self.brass_pads(st, 4, "A", vel=0.95, swell=(96, 116, 92))
        self.cym.hit("crash", self.T(st + 16, 4), self.V(96))
        self.guitar_part(st, n, "A")
        self.brass_hits([st + 4 * k + 3.5 for k in (0, 2, 4, 6)], "B", dur=0.4, vel=100)
        self.play(self.sax, st, OUTRO_SAX, vel=96)
        e = st + n * 4
        self.sax.ccs = [c for c in self.sax.ccs if not (c[1] == 11 and c[0] > e + 1.0)]
        self.sax.cc_ramp(11, e + 1.0, e + 7.0, 112, 50, step=0.25)
        # ending: E6/9 rings out
        e0 = st + n * 4
        self.s.marker(e0, "ending")
        v1, v2, root, pad, _ = self.ch(e0)
        for i, p in enumerate(sorted(set(v1 + v2))):
            self.piano.note(p, e0 + i * 0.06, 7.5, self.V(92))
        self.piano.notes_at([28, 40], e0, 7.5, 100).sustain(e0 + 0.02, e0 + 7.9)
        self.ob.notes_at(v2, e0, 6.0, 80)
        self.rhodes.notes_at(pad, e0, 7.5, 70)
        self.bass.note(28, self.T(e0, 3), 6.0, 108)
        self.gtr.notes_at(v2, self.T(e0, 3), 6.0, 92, strum=0.03)
        self.kick.hit("kick", e0, 118)
        self.cym.hit("crash", e0, 116).hit("crash_sizzle", e0 + 0.02, 100)
        self.snare.hit("snare", e0, 116)
        for tr_, notes in ((self.tbn, pad[:2]), (self.hn, pad[2:]), (self.tpt, [pad[2] + 12, pad[3] + 12])):
            tr_.cc(11, 120, e0 - 0.05).notes_at(notes, e0, 6.0, 100)
            tr_.cc_ramp(11, e0 + 1.0, e0 + 6.0, 120, 70)


def compose() -> Song:
    a = Arranger()
    s = a.s
    a.intro()
    a.verse("verse 1", [VERSE_A + [(4 + b, p, n, d, *r) for b, p, n, d, *r in VERSE_A2],
                        VERSE_B + [(4 + b, p, n, d, *r) for b, p, n, d, *r in VERSE_C]])
    a.pre("pre 1")
    a.chorus("chorus 1")
    a.riff()
    a.verse("verse 2", [VERSE_B + [(4 + b, p, n, d, *r) for b, p, n, d, *r in VERSE_C]], extra=True)
    a.pre("pre 2", last=True)
    a.chorus("chorus 2")
    a.bridge()
    a.chorus("final chorus")
    a.outro()

    # tempo: a live band leaning into the choruses (reference 118.9 -> 122)
    bar = lambda name: s.bar(a.sec[name][0])
    s.tempo_ramp(bar("pre 1"), bar("chorus 1"), 119.0, 120.0, step=2.0)
    s.tempo(bar("chorus 1"), 121.0)
    s.tempo(bar("riff"), 120.5)
    s.tempo_ramp(bar("pre 2"), bar("chorus 2"), 120.5, 121.0, step=2.0)
    s.tempo(bar("chorus 2"), 121.5)
    s.tempo(bar("bridge"), 121.0)
    s.tempo(bar("final chorus"), 122.0)
    s.tempo_ramp(bar("ending") - 4, bar("ending"), 122.0, 110.0, step=0.5)
    s.length_beats = bar("ending") + 8 + 4

    s.mix = {
        "tracks": {
            "kick": {"gain": -4, "eq": [("hpf", 45), ("bell", 80, -1.5, 1.5), ("bell", 380, -4, 1.4), ("bell", 3500, 2.5, 1.0)],
                     "comp": {"threshold": -18, "ratio": 3, "attack": 15, "release": 90}, "tape": {"drive_db": 5},
                     "sends": {"room": -8}},
            "snare": {"gain": -3, "eq": [("hpf", 100), ("bell", 220, 1.5, 1.0), ("bell", 900, -2, 2.0), ("hshelf", 5000, 2)],
                      "comp": {"threshold": -20, "ratio": 3, "attack": 10, "release": 120}, "tape": {"drive_db": 5},
                      "sends": {"plate": -12, "room": -8}},
            "snare 2": {"gain": -10, "eq": [("hpf", 120), ("bell", 220, 2, 1.0), ("hshelf", 6000, -3)], "pan": -0.15,
                        "tape": {"drive_db": 5}, "sends": {"room": -12}},
            "hats": {"gain": -9, "eq": [("hpf", 300), ("hshelf", 7000, 2)], "pan": 0.35, "tape": {"drive_db": 3},
                     "sends": {"room": -10}},
            "toms": {"gain": -6, "eq": [("hpf", 60), ("bell", 600, -3, 1.0)], "sends": {"room": -8}},
            "cymbals": {"gain": -11, "eq": [("hpf", 400), ("hshelf", 7000, 2)], "width": 1.1},
            "perc": {"gain": -15, "eq": [("hpf", 150)], "pan": -0.4, "sends": {"room": -10}},
            "bass": {"gain": -5, "eq": [("hpf", 42), ("bell", 700, 1.5, 1.0), ("bell", 2000, 1.5, 1.0)],
                     "comp": {"threshold": -20, "ratio": 3, "attack": 20, "release": 120}, "tape": {"drive_db": 4},
                     "mono": True},
            "piano": {"gain": -2.5, "eq": [("hpf", 70), ("bell", 300, -2.5, 1.0), ("bell", 900, 1.5, 1.0), ("hshelf", 4500, 3.5)],
                      "width": 0.6, "mono_below": 150,
                      "sends": {"plate": -16}},
            "OB-8": {"gain": -13, "eq": [("hpf", 200), ("lpf", 4000)], "chorus": {"rate_hz": 0.5, "depth_ms": 2.0, "mix": 0.35}},
            "rhodes": {"gain": -9, "eq": [("hpf", 100), ("bell", 250, -2.5, 1.0), ("bell", 2500, 2, 1.0)],
                       "tremolo": {"rate_hz": 4.2, "depth": 0.3},
                       "sends": {"plate": -16}},
            "guitar": {"gain": -9, "eq": [("hpf", 150), ("bell", 400, -2, 1.0)],
                       "comp": {"threshold": -24, "ratio": 4, "attack": 5, "release": 80},
                       "chorus": {"rate_hz": 0.8, "depth_ms": 2.5, "mix": 0.4}, "pan": -0.35, "sends": {"plate": -14}},
            "trombones": {"gain": -7, "eq": [("hpf", 100), ("bell", 350, -2, 1.0)], "pan": 0.25, "sends": {"plate": -10}},
            "horns": {"gain": -7, "eq": [("hpf", 120), ("bell", 350, -2, 1.0)], "pan": -0.25, "sends": {"plate": -10}},
            "trumpets": {"gain": -8, "eq": [("hpf", 200)], "pan": 0.35, "sends": {"plate": -10}},
            "harmon trumpets": {"gain": -9, "eq": [("hpf", 300)], "pan": -0.35, "sends": {"plate": -10}},
            "trombone stabs": {"gain": -8, "eq": [("hpf", 100), ("bell", 350, -2, 1.0)], "pan": 0.25, "sends": {"plate": -9}},
            "horn stabs": {"gain": -8, "eq": [("hpf", 120)], "pan": -0.25, "sends": {"plate": -9}},
            "trumpet stabs": {"gain": -9, "eq": [("hpf", 200)], "pan": 0.35, "sends": {"plate": -9}},
            "tenor sax": {"gain": -1, "eq": [("hpf", 100), ("bell", 250, -2, 1.0), ("bell", 900, 1, 1.0),
                                             ("bell", 2500, 2, 0.8), ("hshelf", 6500, 2.5)],
                          "comp": {"threshold": -22, "ratio": 2.5, "attack": 15, "release": 150},
                          "sends": {"plate": -10, "dly": -18}},
            "synth lead": {"gain": -3, "eq": [("hpf", 150)], "sends": {"plate": -12, "dly": -14}},
        },
        "fx": {
            "plate": {"type": "reverb", "kind": "plate", "decay": 2.0, "predelay": 25, "hpf": 250, "lpf": 8000},
            "room": {"type": "reverb", "kind": "room", "decay": 0.6, "predelay": 5, "hpf": 200, "lpf": 7000},
            "dly": {"type": "delay", "beats": 0.75, "feedback": 0.25, "hpf": 400, "lpf": 3500},
        },
        "master": {"eq": [("lshelf", 120, -5, 0.7), ("hpf", 32), ("hshelf", 5500, 1.5, 0.7)],
                   "glue": {"threshold": -18, "ratio": 2, "attack": 30, "release": 250}, "target_lufs": -14},
    }
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        sec = s.seconds(beat)
        print(f"{int(sec // 60)}:{sec % 60:04.1f}  bar {beat / 4 + 1:5.0f}  {label}")
    print("length", round(s.seconds(s.end_beat), 1), "s")
