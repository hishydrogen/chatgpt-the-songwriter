"""Bake sounds into early-sampler instruments (Ensoniq Mirage, Fairlight CMI, LinnDrum).

The character of those machines comes from three things, all reproduced here:
  1. storage: low sample rate and 8-bit words (LinnDrum/DMX: mu-law companded),
  2. transposition by changing playback speed with no interpolation, so every key
     away from the root gets its own aliasing and grit (and lower keys get longer),
  3. an analog low-pass with an envelope after the DAC (sfizz lpf_4p + fileg).
Each key is rendered ahead of time and written as an SFZ instrument that the normal
`sfz` engine plays, so baked instruments behave like any other catalog entry.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

from . import config, dsp

SR = config.SAMPLE_RATE
GEN = config.LIB_DIR / "_generated"


@dataclass
class Source:
    audio: np.ndarray          # (2, N) or (N,) float at SR
    root: float                # MIDI note the audio sounds at (fractional = detuned source)
    lovel: int = 1
    hivel: int = 127


@dataclass
class Machine:
    rate: float = 30000.0      # storage sample rate (Mirage up to ~33 kHz, LinnDrum ~28-35 kHz)
    bits: int = 8
    mulaw: bool = False
    out_lpf: float = 15000.0   # output smoothing after the DAC
    stereo: bool = False       # those machines were mono


MIRAGE = Machine(rate=30000, bits=8)
FAIRLIGHT = Machine(rate=24000, bits=8, out_lpf=11000)
LINNDRUM = Machine(rate=28000, bits=8, mulaw=True, out_lpf=13000)
SP12 = Machine(rate=26040, bits=12, out_lpf=12000)


def store(audio: np.ndarray, m: Machine) -> np.ndarray:
    """What the machine keeps in memory: band-limited at input, resampled, quantised."""
    x = audio.mean(axis=0) if (audio.ndim == 2 and not m.stereo) else audio
    up, down = _ratio(m.rate)
    y = signal.resample_poly(x, up, down, axis=-1)
    q = 2 ** (m.bits - 1)
    peak = np.abs(y).max() + 1e-12
    y = y / peak * 0.98                     # sampled hot, like everyone did
    if m.mulaw:
        mu = 255.0
        c = np.sign(y) * np.log1p(mu * np.abs(y)) / np.log1p(mu)
        c = np.round(c * q) / q
        y = np.sign(c) * np.expm1(np.abs(c) * np.log1p(mu)) / mu
    else:
        y = np.round(y * q) / q
    return y.astype(np.float32)


def play(stored: np.ndarray, m: Machine, ratio: float = 1.0) -> np.ndarray:
    """Read memory at rate*ratio with zero-order hold, out at SR, then DAC smoothing."""
    n_in = stored.shape[-1]
    step = m.rate * ratio / SR
    n_out = int(n_in / step)
    idx = np.minimum((np.arange(n_out) * step).astype(np.int64), n_in - 1)
    y = stored[..., idx]
    sos = signal.butter(4, min(m.out_lpf, 0.45 * SR), "lp", fs=SR, output="sos")
    return signal.sosfilt(sos, y, axis=-1).astype(np.float32)


def _ratio(rate: float) -> tuple[int, int]:
    from fractions import Fraction
    f = Fraction(int(rate), SR).limit_denominator(400)
    return f.numerator, f.denominator


def trim(x: np.ndarray, floor_db=-60.0, max_s: float | None = None, fade_ms=8.0) -> np.ndarray:
    a = np.abs(x) if x.ndim == 1 else np.abs(x).max(axis=0)
    thr = a.max() * 10 ** (floor_db / 20)
    nz = np.flatnonzero(a > thr)
    end = (nz[-1] + 1) if len(nz) else len(a)
    if max_s:
        end = min(end, int(max_s * SR))
    y = x[..., :end].copy()
    f = min(int(SR * fade_ms / 1000), y.shape[-1])
    y[..., -f:] *= np.linspace(1, 0, f)
    return y


@dataclass
class Bake:
    iid: str                       # catalog id, e.g. "mirage.timpani"
    desc: str
    sources: list[Source]
    keys: range                    # keys to render
    machine: Machine = field(default_factory=lambda: MIRAGE)
    sfz_global: dict = field(default_factory=dict)   # e.g. {"fil_type": "lpf_4p", "cutoff": 2000}
    max_s: float | None = None     # cap per-key length (seconds)
    gain_db: float = 0.0

    def run(self) -> Path:
        folder = GEN / self.iid
        folder.mkdir(parents=True, exist_ok=True)
        stored = [(store(s.audio, self.machine), s) for s in self.sources]
        lines = [f"// {self.desc}", f"// baked by songwriter.vintage ({self.machine})", "<control>",
                 f"default_path={self.iid}/", "<global>"]
        lines += [f"{k}={v}" for k, v in self.sfz_global.items()]
        for key in self.keys:
            # every velocity layer picks its nearest root, then plays it at the key's speed
            for lv, hv in sorted({(s.lovel, s.hivel) for _, s in stored}):
                layer = [(st, s) for st, s in stored if (s.lovel, s.hivel) == (lv, hv)]
                st, s = min(layer, key=lambda p: abs(p[1].root - key))
                y = play(st, self.machine, 2 ** ((key - s.root) / 12))
                y = trim(y, max_s=self.max_s) * dsp.db(self.gain_db)
                name = f"k{key:03d}_v{hv:03d}.wav"
                sf.write(folder / name, y.T if y.ndim == 2 else y, SR, subtype="FLOAT")
                lines.append(f"<region> sample={name} key={key} pitch_keycenter={key} lovel={lv} hivel={hv}")
        sfz = GEN / f"{self.iid}.sfz"
        sfz.write_text("\n".join(lines) + "\n")
        return sfz


@dataclass
class Voice:
    key: int
    audio: np.ndarray
    tune: float = 0.0          # semitones, by playback speed like the Linn's tuning pots
    gain_db: float = 0.0
    sfz: str = ""              # extra region opcodes, e.g. "group=1 off_by=2"


@dataclass
class Kit:
    """One-shot drum kit through a drum machine's converters (no per-key transposition)."""
    iid: str
    desc: str
    voices: dict[str, Voice]
    machine: Machine = field(default_factory=lambda: LINNDRUM)
    amp_veltrack: int = 40

    def run(self) -> tuple[Path, dict]:
        folder = GEN / self.iid
        folder.mkdir(parents=True, exist_ok=True)
        lines = [f"// {self.desc}", "<control>", f"default_path={self.iid}/", "<global>",
                 "loop_mode=one_shot", f"amp_veltrack={self.amp_veltrack}"]
        drum_map = {}
        for name, v in self.voices.items():
            y = play(store(v.audio, self.machine), self.machine, 2 ** (v.tune / 12)) * dsp.db(v.gain_db)
            sf.write(folder / f"{name}.wav", trim(y), SR, subtype="FLOAT")
            lines.append(f"<region> sample={name}.wav key={v.key} {v.sfz}".rstrip())
            drum_map[name] = v.key
        sfz = GEN / f"{self.iid}.sfz"
        sfz.write_text("\n".join(lines) + "\n")
        return sfz, drum_map
