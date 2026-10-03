"""Song and track model: write music in beats, export MIDI per track.

    song = Song("Demo", bpm=92)
    keys = song.track("keys", "piano.salamander")
    keys.chord("Cmaj9", beat=0, dur=4, octave=3)
    drums = song.track("drums", "drums.virtuosity")
    drums.hit("kick", 0); drums.hit("snare", 1)
"""
from __future__ import annotations

import math
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
    lyric: str | None = None   # sung syllable (voice.* instruments)
    x: dict | None = None      # per-note engine options (voice.* instruments)


@dataclass
class Track:
    name: str
    instrument: str
    song: "Song"
    notes: list[Note] = field(default_factory=list)
    ccs: list[tuple[float, int, int]] = field(default_factory=list)  # (beat, cc, value)
    bends: list[tuple[float, int]] = field(default_factory=list)      # (beat, -8192..8191)
    channel: int = 0
    opts: dict = field(default_factory=dict)  # engine options (voice.*: see songwriter.voice)

    # -- writing -----------------------------------------------------------
    def note(self, pitch, beat: float, dur: float = 1.0, vel: int = 90,
             lyric: str | None = None, x: dict | None = None):
        self.notes.append(Note(note_number(pitch), beat, dur, int(max(1, min(127, vel))), lyric, x))
        return self

    def sing(self, pitches, lyrics, beat: float, dur=0.5, vel: int = 100, x: dict | None = None):
        """A sung line: pitches and lyrics as space-separated strings or lists (one mora per
        note), `dur` a number or a list of beat lengths. Returns the beat after the line."""
        ps = pitches.split() if isinstance(pitches, str) else list(pitches)
        ls = lyrics.split() if isinstance(lyrics, str) else list(lyrics)
        ds = list(dur) if isinstance(dur, (list, tuple)) else [dur] * len(ps)
        if not (len(ps) == len(ls) == len(ds)):
            raise ValueError(f"sing: {len(ps)} pitches, {len(ls)} lyrics, {len(ds)} durations")
        b = beat
        for p, l, d in zip(ps, ls, ds):
            if p not in ("r", "_"):
                self.note(p, b, d, vel, lyric=l, x=dict(x) if x else None)
            b += d
        return b

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

    def cc_ramp(self, number: int, beat0: float, beat1: float, v0: int, v1: int,
                step: float = 0.125, curve: float = 1.0):
        """Linear (curve=1) or shaped CC sweep, e.g. a brass swell on CC11."""
        n = max(1, int(round((beat1 - beat0) / step)))
        for i in range(n + 1):
            f = (i / n) ** curve
            self.cc(number, round(v0 + (v1 - v0) * f), beat0 + i * (beat1 - beat0) / n)
        return self

    def vibrato(self, beat0: float, beat1: float, rate_hz: float = 5.5, cents: float = 20.0,
                bend_range: float = 2.0, fade: float = 0.4, step_s: float = 0.02):
        """Pitch-bend vibrato between two beats that fades in over `fade` of the span and
        returns to centre at beat1 (for synths/samples without their own vibrato)."""
        span = max(1e-6, beat1 - beat0)
        b, t = beat0, 0.0
        while b < beat1:
            env = min(1.0, (b - beat0) / (span * fade + 1e-9))
            val = cents / (bend_range * 100) * 8191 * env * math.sin(2 * math.pi * rate_hz * t)
            self.bend(int(round(val)), b)
            b += step_s * self.song.bpm_at(b) / 60.0
            t += step_s
        self.bend(0, beat1)
        return self

    # -- feel ----------------------------------------------------------------
    def humanize(self, timing_ms: float = 8.0, vel: int = 6, seed: int | None = None,
                 skip_downbeats: bool = False):
        """Small random timing/velocity drift. Deterministic per track name unless seed given."""
        rng = random.Random(seed if seed is not None else zlib.crc32(self.name.encode()))
        for n in self.notes:
            if skip_downbeats and abs(n.start - round(n.start)) < 1e-6:
                continue
            spb = 60.0 / self.song.bpm_at(n.start)
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
        self.tempo_changes: list[tuple[float, float]] = []  # (beat, bpm) after the start

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

    def tempo(self, beat: float, bpm: float):
        """Tempo change at `beat` (a live band leaning into the chorus). Written to the
        MIDI files as set_tempo events, honoured by every renderer."""
        self.tempo_changes = sorted([c for c in self.tempo_changes if abs(c[0] - beat) > 1e-9]
                                    + [(float(beat), float(bpm))])
        return self

    def tempo_ramp(self, beat0: float, beat1: float, bpm0: float, bpm1: float, step: float = 1.0):
        """Gradual drift from bpm0 to bpm1 between two beats, one small change per `step` beats."""
        n = max(1, int(round((beat1 - beat0) / step)))
        for i in range(n + 1):
            self.tempo(beat0 + i * (beat1 - beat0) / n, bpm0 + i * (bpm1 - bpm0) / n)
        return self

    def bpm_at(self, beat: float) -> float:
        bpm = self.bpm
        for b, t in self.tempo_changes:
            if b > beat:
                break
            bpm = t
        return bpm

    def seconds(self, beats: float) -> float:
        """Time of a beat position (follows tempo changes)."""
        t, prev_b, prev_bpm = 0.0, 0.0, self.bpm
        for b, bpm in self.tempo_changes:
            if b >= beats:
                break
            t += (b - prev_b) * 60.0 / prev_bpm
            prev_b, prev_bpm = b, bpm
        return t + (beats - prev_b) * 60.0 / prev_bpm

    def _tempo_events(self) -> list[tuple[int, mido.MetaMessage]]:
        ev = [(0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(self.bpm), time=0))]
        for b, bpm in self.tempo_changes:
            tick = round(b * self.TPB)
            if tick == 0:
                ev = []
            ev.append((tick, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0)))
        return ev

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
            on = max(0, round(n.start * self.TPB))  # humanized notes may start a hair before 0
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
        mt.append(mido.MetaMessage("time_signature", numerator=self.time_sig[0], denominator=self.time_sig[1], time=0))
        ev = [(tick, -1, m) for tick, m in self._tempo_events()] + self._events(track)
        ev.sort(key=lambda e: (e[0], e[1]))
        last = 0
        for tick, _, msg in ev:
            mt.append(msg.copy(time=tick - last))
            last = tick
        return mf

    def full_midi(self) -> mido.MidiFile:
        """All tracks in one type-1 file (for importing into a DAW)."""
        mf = mido.MidiFile(type=1, ticks_per_beat=self.TPB)
        meta = mido.MidiTrack([
            mido.MetaMessage("track_name", name=self.title, time=0),
            mido.MetaMessage("time_signature", numerator=self.time_sig[0], denominator=self.time_sig[1], time=0),
        ])
        ev = self._tempo_events() + [(round(b * self.TPB), mido.MetaMessage("marker", text=label, time=0))
                                     for b, label in self.markers]
        last = 0
        for tick, msg in sorted(ev, key=lambda e: e[0]):
            meta.append(msg.copy(time=tick - last))
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
        return [(self.seconds(tick / self.TPB), msg) for tick, _, msg in self._events(track)]
