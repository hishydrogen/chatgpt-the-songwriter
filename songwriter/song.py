"""Song and track model: write music in beats, export MIDI per track.

    song = Song("Demo", bpm=92)
    keys = song.track("keys", "piano.salamander")
    keys.chord("Cmaj9", beat=0, dur=4, octave=3)
    drums = song.track("drums", "drums.virtuosity")
    drums.hit("kick", 0); drums.hit("snare", 1)
"""
from __future__ import annotations

import random
import re
import zlib
from dataclasses import dataclass, field

import mido

NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

CHORD_QUALITIES = {
    "": [0, 4, 7], "maj": [0, 4, 7], "m": [0, 3, 7], "min": [0, 3, 7],
    "dim": [0, 3, 6], "aug": [0, 4, 8], "sus2": [0, 2, 7], "sus4": [0, 5, 7],
    "5": [0, 7], "6": [0, 4, 7, 9], "m6": [0, 3, 7, 9],
    "7": [0, 4, 7, 10], "maj7": [0, 4, 7, 11], "m7": [0, 3, 7, 10],
    "mmaj7": [0, 3, 7, 11], "m7b5": [0, 3, 6, 10], "dim7": [0, 3, 6, 9],
    "7sus4": [0, 5, 7, 10], "add9": [0, 4, 7, 14], "madd9": [0, 3, 7, 14],
    "9": [0, 4, 7, 10, 14], "maj9": [0, 4, 7, 11, 14], "m9": [0, 3, 7, 10, 14],
    "11": [0, 4, 7, 10, 14, 17], "m11": [0, 3, 7, 10, 14, 17],
    "13": [0, 4, 7, 10, 14, 21], "maj13": [0, 4, 7, 11, 14, 21], "m13": [0, 3, 7, 10, 14, 21],
    "7b9": [0, 4, 7, 10, 13], "7#9": [0, 4, 7, 10, 15], "6/9": [0, 4, 7, 9, 14],
}


def note_number(n: int | str) -> int:
    """'C4' -> 60, 'F#2' -> 42, 'Bb3' -> 58. Integers pass through."""
    if isinstance(n, int):
        return n
    m = re.fullmatch(r"([A-Ga-g])([#b]*)(-?\d+)", n.strip())
    if not m:
        raise ValueError(f"bad note name: {n!r}")
    letter, acc, octv = m.groups()
    return 12 * (int(octv) + 1) + NOTE_OFFSETS[letter.upper()] + acc.count("#") - acc.count("b")


def chord_notes(symbol: str, octave: int = 3) -> list[int]:
    """'Am7' -> pitches with the root in `octave`. Slash chords ('C/E') put the bass below."""
    bass = None
    if "/" in symbol and not symbol.endswith("6/9"):
        symbol, bass = symbol.split("/")
    m = re.fullmatch(r"([A-G][#b]?)(.*)", symbol)
    if not m or m.group(2) not in CHORD_QUALITIES:
        raise ValueError(f"unknown chord: {symbol!r}")
    root = note_number(f"{m.group(1)}{octave}")
    notes = [root + i for i in CHORD_QUALITIES[m.group(2)]]
    if bass:
        b = note_number(f"{bass}{octave}")
        while b >= notes[0]:
            b -= 12
        notes = [b] + notes
    return notes


@dataclass
class Note:
    pitch: int
    start: float  # beats
    dur: float    # beats
    vel: int


@dataclass
class Track:
    name: str
    instrument: str
    song: "Song"
    notes: list[Note] = field(default_factory=list)
    ccs: list[tuple[float, int, int]] = field(default_factory=list)  # (beat, cc, value)
    bends: list[tuple[float, int]] = field(default_factory=list)      # (beat, -8192..8191)
    channel: int = 0

    # -- writing -----------------------------------------------------------
    def note(self, pitch, beat: float, dur: float = 1.0, vel: int = 90):
        self.notes.append(Note(note_number(pitch), beat, dur, int(max(1, min(127, vel)))))
        return self

    def notes_at(self, pitches, beat, dur=1.0, vel=90, strum=0.0):
        """Several pitches at once. strum > 0 rolls them upward (beats between notes)."""
        for i, p in enumerate(pitches):
            self.note(p, beat + i * strum, dur - i * strum, vel)
        return self

    def chord(self, symbol: str, beat: float, dur: float = 4.0, vel: int = 80,
              octave: int = 3, strum: float = 0.0, drop: list[int] | None = None):
        """Chord by symbol. `drop` lists chord-tone indices to move down an octave."""
        pitches = chord_notes(symbol, octave)
        for i in drop or []:
            pitches[i] -= 12
        return self.notes_at(sorted(pitches), beat, dur, vel, strum)

    def hit(self, drum: str | int, beat: float, vel: int = 100, dur: float = 0.25):
        """Drum hit by name ('kick', 'snare', 'hh_closed' ...) using the instrument's drum map."""
        from .instruments import get_instrument
        inst = get_instrument(self.instrument)
        if isinstance(drum, str):
            if drum not in inst.drum_map:
                raise KeyError(f"{self.instrument} has no drum '{drum}'. Has: {sorted(inst.drum_map)}")
            spec = inst.drum_map[drum]
        else:
            spec = drum
        if isinstance(spec, tuple):  # (key, {cc: value}) e.g. hi-hat openness via CC4
            key, ccs = spec
            for cc, val in ccs.items():
                self.cc(cc, val, beat - 0.01)
        else:
            key = spec
        return self.note(key, beat, dur, vel)

    def cc(self, number: int, value: int, beat: float):
        self.ccs.append((beat, number, int(max(0, min(127, value)))))
        return self

    def sustain(self, down: float, up: float):
        """Sustain pedal down/up (beats). Re-pedal slightly before the next chord."""
        self.cc(64, 127, down)
        self.cc(64, 0, up)
        return self

    def bend(self, value: int, beat: float):
        self.bends.append((beat, int(max(-8192, min(8191, value)))))
        return self

    # -- feel ----------------------------------------------------------------
    def humanize(self, timing_ms: float = 8.0, vel: int = 6, seed: int | None = None,
                 skip_downbeats: bool = False):
        """Small random timing/velocity drift. Deterministic per track name unless seed given."""
        rng = random.Random(seed if seed is not None else zlib.crc32(self.name.encode()))
        spb = 60.0 / self.song.bpm
        for n in self.notes:
            if skip_downbeats and abs(n.start - round(n.start)) < 1e-6:
                continue
            n.start = max(0.0, n.start + rng.gauss(0, timing_ms / 1000 / spb / 2))
            n.vel = int(max(1, min(127, n.vel + rng.randint(-vel, vel))))
        return self

    def swing(self, amount: float = 0.58, grid: float = 0.5):
        """Delay every off-beat of `grid` so pairs become amount:(1-amount)."""
        for n in self.notes:
            pos = n.start / grid
            if abs(pos - round(pos)) < 1e-3 and round(pos) % 2 == 1:
                n.start += (amount - 0.5) * 2 * grid
        return self

    @property
    def end_beat(self) -> float:
        return max([n.start + n.dur for n in self.notes] + [b for b, *_ in self.ccs] + [0.0])


class Song:
    def __init__(self, title: str, bpm: float = 100, time_sig: tuple[int, int] = (4, 4),
                 key: str | None = None):
        self.title = title
        self.bpm = bpm
        self.time_sig = time_sig
        self.key = key
        self.tracks: dict[str, Track] = {}
        self.markers: list[tuple[float, str]] = []
        self.mix: dict = {}       # filled by the song file, consumed by songwriter.mix
        self.length_beats: float | None = None

    def track(self, name: str, instrument: str, **kw) -> Track:
        if name in self.tracks:
            return self.tracks[name]
        t = Track(name, instrument, self, **kw)
        self.tracks[name] = t
        return t

    def bar(self, n: float) -> float:
        """Beat position of bar n (0-based)."""
        return n * self.time_sig[0] * 4 / self.time_sig[1]

    def marker(self, beat: float, label: str):
        self.markers.append((beat, label))

    def seconds(self, beats: float) -> float:
        return beats * 60.0 / self.bpm

    @property
    def end_beat(self) -> float:
        if self.length_beats is not None:
            return self.length_beats
        return max([t.end_beat for t in self.tracks.values()] + [0.0])

    # -- export ----------------------------------------------------------------
    TPB = 960

    def _events(self, track: Track):
        ev = []  # (tick, order, msg) - offs before ons at equal tick
        ch = track.channel
        for n in track.notes:
            on = round(n.start * self.TPB)
            off = max(on + 1, round((n.start + n.dur) * self.TPB))
            ev.append((on, 2, mido.Message("note_on", note=n.pitch, velocity=n.vel, channel=ch)))
            ev.append((off, 0, mido.Message("note_off", note=n.pitch, velocity=0, channel=ch)))
        for beat, num, val in track.ccs:
            ev.append((max(0, round(beat * self.TPB)), 1, mido.Message("control_change", control=num, value=val, channel=ch)))
        for beat, val in track.bends:
            ev.append((max(0, round(beat * self.TPB)), 1, mido.Message("pitchwheel", pitch=val, channel=ch)))
        ev.sort(key=lambda e: (e[0], e[1]))
        return ev

    def track_midi(self, track: Track) -> mido.MidiFile:
        mf = mido.MidiFile(ticks_per_beat=self.TPB)
        mt = mido.MidiTrack()
        mf.tracks.append(mt)
        mt.append(mido.MetaMessage("track_name", name=track.name, time=0))
        mt.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(self.bpm), time=0))
        mt.append(mido.MetaMessage("time_signature", numerator=self.time_sig[0], denominator=self.time_sig[1], time=0))
        last = 0
        for tick, _, msg in self._events(track):
            mt.append(msg.copy(time=tick - last))
            last = tick
        return mf

    def full_midi(self) -> mido.MidiFile:
        """All tracks in one type-1 file (for importing into a DAW)."""
        mf = mido.MidiFile(type=1, ticks_per_beat=self.TPB)
        meta = mido.MidiTrack([
            mido.MetaMessage("track_name", name=self.title, time=0),
            mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(self.bpm), time=0),
            mido.MetaMessage("time_signature", numerator=self.time_sig[0], denominator=self.time_sig[1], time=0),
        ])
        last = 0
        for beat, label in sorted(self.markers):
            tick = round(beat * self.TPB)
            meta.append(mido.MetaMessage("marker", text=label, time=tick - last))
            last = tick
        mf.tracks.append(meta)
        for i, t in enumerate(self.tracks.values()):
            mt = mido.MidiTrack([mido.MetaMessage("track_name", name=t.name, time=0)])
            last = 0
            for tick, _, msg in self._events(t):
                mt.append(msg.copy(time=tick - last, channel=9 if t.instrument.startswith("drums.") else i % 16 if i % 16 != 9 else 15))
                last = tick
            mf.tracks.append(mt)
        return mf

    def timed_messages(self, track: Track) -> list[tuple[float, mido.Message]]:
        """(seconds, message) list for engines that take live MIDI (VST3, surgepy)."""
        return [(tick / self.TPB * 60.0 / self.bpm, msg) for tick, _, msg in self._events(track)]
