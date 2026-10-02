"""Signal processing building blocks: LSP / Dragonfly VST3 wrappers + numpy DSP.

All audio is float32 shaped (2, N) at config.SAMPLE_RATE.
"""
from __future__ import annotations

import functools
import os
import sys

import numpy as np
from scipy import signal

from . import config

SR = config.SAMPLE_RATE


@functools.lru_cache(maxsize=None)
def _pb():
    import pedalboard
    return pedalboard


class _quiet:
    """Silence plugin chatter written straight to fd 1/2 (LSP, DPF)."""
    def __enter__(self):
        sys.stdout.flush(); sys.stderr.flush()
        self.saved = os.dup(1), os.dup(2)
        self.null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.null, 1); os.dup2(self.null, 2)

    def __exit__(self, *a):
        os.dup2(self.saved[0], 1); os.dup2(self.saved[1], 2)
        for fd in (*self.saved, self.null):
            os.close(fd)


def setp(plugin, name: str, value):
    """Set a plugin parameter, clamping numbers into the parameter's range."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        lo, hi, _ = plugin.parameters[name].range
        if lo is not None and hi is not None:
            value = float(min(max(value, lo), hi))
    setattr(plugin, name, value)


def load_plugin(path, plugin_name=None, **params):
    with _quiet():
        p = _pb().load_plugin(str(path), plugin_name=plugin_name)
        for k, v in params.items():
            setp(p, k, v)
    return p


def lsp(name: str, **params):
    return load_plugin(config.LSP_VST3, plugin_name=name, **params)


def run(plugin, x: np.ndarray, linear: bool = True) -> np.ndarray:
    """Process with latency compensation (pedalboard does not compensate VST3 latency).

    Latency is measured with a quiet impulse, so it is exact for plugins that are linear
    at low level (EQ, compressors, limiters). Pass linear=False for wet-only effects.
    """
    lat = 0
    if linear:
        imp = np.zeros((x.shape[0], SR // 2), np.float32)
        imp[:, 100] = 1e-3
        with _quiet():
            y = plugin(imp, SR)
            plugin.reset()
        lat = max(0, int(np.argmax(np.abs(y[0]))) - 100)
    pad = np.zeros((x.shape[0], lat), np.float32)
    with _quiet():
        y = plugin(np.concatenate([x, pad], axis=1).astype(np.float32), SR)
        plugin.reset()
    return np.ascontiguousarray(y[:, lat:lat + x.shape[1]], dtype=np.float32)


# -- EQ ---------------------------------------------------------------------

_EQ_TYPES = {
    "hpf": "Hi-pass", "lpf": "Lo-pass", "bell": "Bell", "lshelf": "Lo-shelf",
    "hshelf": "Hi-shelf", "notch": "Notch", "bandpass": "Bandpass",
}


def eq(x: np.ndarray, bands: list, linear_phase: bool = False) -> np.ndarray:
    """Parametric EQ (LSP x16). Each band is a tuple:
        ("hpf", freq[, slope 1-4])       slope 1 = 12 dB/oct ... 4 = 48 dB/oct
        ("lpf", freq[, slope])
        ("bell", freq, gain_db[, q])
        ("lshelf"|"hshelf", freq, gain_db[, q])
        ("notch", freq[, q])
    """
    if not bands:
        return x
    p = lsp("Parametric Equalizer x16 Stereo")
    setp(p, "equalizer_mode", "SPM" if linear_phase else "IIR")
    for i, b in enumerate(bands):
        kind, freq, *rest = b
        setp(p, f"filter_type_{i}", _EQ_TYPES[kind])
        setp(p, f"filter_mode_{i}", "RLC (BT)" if kind not in ("hpf", "lpf") else "BWC (BT)")
        setp(p, f"frequency_{i}_hz", float(freq))
        if kind in ("hpf", "lpf"):
            setp(p, f"filter_slope_{i}", f"x{rest[0] if rest else 2}")
        elif kind == "notch":
            setp(p, f"quality_factor_{i}", float(rest[0] if rest else 4.0))
        else:
            setp(p, f"gain_{i}_db", float(rest[0]))
            setp(p, f"quality_factor_{i}", float(rest[1] if len(rest) > 1 else 0.7))
    return run(p, x)


# -- dynamics -----------------------------------------------------------------

def compress(x, threshold=-18.0, ratio=3.0, attack=15.0, release=120.0, knee=-6.0,
             makeup=0.0, mix=1.0, hpf_sidechain=None, mode="RMS", lookahead=0.0):
    """LSP Compressor. mix < 1 gives parallel (New York) compression."""
    p = lsp("Compressor Stereo")
    setp(p, "sidechain_mode", mode)
    setp(p, "attack_threshold_db", float(threshold))
    setp(p, "ratio", float(ratio))
    setp(p, "attack_time_ms", float(attack))
    setp(p, "release_time_ms", float(release))
    setp(p, "knee_db", float(knee))
    setp(p, "makeup_gain_db", float(makeup))
    if lookahead:
        setp(p, "sidechain_lookahead_ms", float(lookahead))
    if hpf_sidechain:
        setp(p, "high_pass_filter_mode", "12 dB/oct")
        setp(p, "high_pass_filter_frequency_hz", float(hpf_sidechain))
    y = run(p, x)
    return y if mix >= 1 else (1 - mix) * x + mix * y


def limit(x, ceiling_db=-1.0, lookahead=5.0, release=8.0, mode="Herm Thin"):
    """LSP brickwall limiter with 4x oversampling (true-peak safe-ish; verify with true_peak)."""
    p = lsp("Limiter Stereo")
    setp(p, "operating_mode", mode)
    setp(p, "oversampling", "Full x4/24 bit")
    setp(p, "threshold_db", float(ceiling_db))
    setp(p, "lookahead_ms", float(lookahead))
    setp(p, "release_time_ms", float(release))
    setp(p, "automatic_level_regulation", False)
    setp(p, "gain_boost", False)
    setp(p, "dithering", "None")
    return run(p, x)


def envelope(x: np.ndarray, attack_ms=1.0, release_ms=100.0) -> np.ndarray:
    """Peak envelope follower of a (2, N) or (N,) signal -> (N,)."""
    mono = np.max(np.abs(x), axis=0) if x.ndim == 2 else np.abs(x)
    ga = np.exp(-1.0 / (SR * attack_ms / 1000))
    gr = np.exp(-1.0 / (SR * release_ms / 1000))
    # fast path: decimate, follow, interpolate back
    hop = 16
    m = mono[: len(mono) // hop * hop].reshape(-1, hop).max(axis=1)
    ga_h, gr_h = ga ** hop, gr ** hop
    env = np.empty_like(m)
    e = 0.0
    for i, v in enumerate(m):
        e = ga_h * e + (1 - ga_h) * v if v > e else gr_h * e + (1 - gr_h) * v
        env[i] = e
    full = np.repeat(env, hop)
    return np.pad(full, (0, len(mono) - len(full)), mode="edge")


def duck(x, trigger, depth_db=6.0, attack_ms=2.0, release_ms=120.0):
    """Sidechain-style ducking of x by trigger's envelope (kick -> bass/pads)."""
    env = envelope(trigger, attack_ms, release_ms)
    env = env / (env.max() + 1e-9)
    gain = 10 ** (-depth_db * env / 20)
    return (x * gain).astype(np.float32)


# -- colour -----------------------------------------------------------------

def saturate(x, drive_db=6.0, mix=1.0, asym=0.0):
    """Oversampled tanh saturation, output level-matched. asym adds even harmonics."""
    if drive_db <= 0:
        return x
    g = 10 ** (drive_db / 20)
    up = signal.resample_poly(x, 4, 1, axis=1)
    y = np.tanh(g * up + asym) - np.tanh(asym)
    y = signal.resample_poly(y, 1, 4, axis=1)[:, : x.shape[1]]
    rms_in = np.sqrt(np.mean(x ** 2)) + 1e-12
    rms_out = np.sqrt(np.mean(y ** 2)) + 1e-12
    y = y * (rms_in / rms_out)
    return ((1 - mix) * x + mix * y).astype(np.float32)


def tube(x, drive=3.0, bass=5.0, mids=5.0, treble=5.0):
    """ZamTube triode emulation (amp-like colour, good on guitars, bass, keys)."""
    p = load_plugin("/usr/lib/vst3/ZamTube.vst3", tube_drive=float(drive), bass=float(bass),
                    mids=float(mids), treble=float(treble))
    y = np.concatenate([run(p, x[c:c + 1]) for c in range(2)])  # mono plugin: one pass per side
    rms_in = np.sqrt(np.mean(x ** 2)) + 1e-12
    return y * (rms_in / (np.sqrt(np.mean(y ** 2)) + 1e-12))


# -- space ------------------------------------------------------------------

def pan(x, position=0.0):
    """Constant-power pan of a stereo signal. -1 left ... +1 right."""
    if position == 0:
        return x
    a = (position + 1) * np.pi / 4
    l, r = np.cos(a) * np.sqrt(2), np.sin(a) * np.sqrt(2)
    return np.stack([x[0] * l, x[1] * r]).astype(np.float32)


def width(x, amount=1.0):
    """Mid/side width. 0 = mono, 1 = unchanged, >1 wider."""
    if amount == 1.0:
        return x
    mid = (x[0] + x[1]) / 2
    side = (x[0] - x[1]) / 2 * amount
    return np.stack([mid + side, mid - side]).astype(np.float32)


def mono_bass(x, below_hz=120.0):
    """Collapse side signal below a frequency (keeps low end centred and punchy)."""
    sos = signal.butter(4, below_hz, "hp", fs=SR, output="sos")
    mid = (x[0] + x[1]) / 2
    side = signal.sosfiltfilt(sos, (x[0] - x[1]) / 2)
    return np.stack([mid + side, mid - side]).astype(np.float32)


def haas(x, ms=12.0, amount=1.0):
    """Widen a mono-ish source by delaying one side slightly (use sparingly)."""
    d = int(SR * ms / 1000)
    r = np.concatenate([np.zeros(d, np.float32), x[1][:-d]])
    return np.stack([x[0], (1 - amount) * x[1] + amount * r]).astype(np.float32)


REVERBS = {
    "plate": ("DragonflyPlateReverb", {"dry_level": 0.0, "wet_level": 100.0}),
    "hall": ("DragonflyHallReverb", {"dry_level": 0.0, "early_level": 10.0, "late_level": 100.0}),
    "room": ("DragonflyRoomReverb", {"dry_level": 0.0, "early_level": 40.0, "late_level": 100.0}),
}


def reverb(x, kind="plate", decay=1.8, predelay=20.0, size=None, hpf=250.0, lpf=9000.0,
           width_pct=100.0, **extra):
    """Wet-only Dragonfly reverb return. kind: plate | hall | room."""
    plug, base = REVERBS[kind]
    p = load_plugin(f"/usr/lib/vst3/{plug}.vst3", **base)
    for k, v in {"predelay_ms": predelay, "width": width_pct, "low_cut_hz": hpf,
                 "high_cut_hz": lpf, "decay_s": decay, "size_m": size, **extra}.items():
        if v is not None and k in p.parameters:
            setp(p, k, v)
    tail = np.zeros((2, int(SR * min(decay * 1.5, 8))), np.float32)
    y = run(p, np.concatenate([x, tail], axis=1), linear=False)
    return y[:, : x.shape[1]]


def delay(x, seconds, feedback=0.35, pingpong=True, hpf=300.0, lpf=4500.0, repeats=10):
    """Tempo-synced feedback delay (wet only). Each repeat is filtered again (darker tails)."""
    d = int(round(seconds * SR))
    if d <= 0:
        return np.zeros_like(x)
    sos = signal.butter(2, [hpf, lpf], "bandpass", fs=SR, output="sos")
    out = np.zeros_like(x)
    tap = np.mean(x, axis=0) if pingpong else x.copy()
    g = 1.0
    for k in range(1, repeats + 1):
        tap = signal.sosfilt(sos, tap, axis=-1)
        g *= feedback if k > 1 else 1.0
        if g < 1e-3 or k * d >= x.shape[1]:
            break
        if pingpong:
            ch = (k - 1) % 2
            out[ch, k * d:] += g * tap[: x.shape[1] - k * d]
        else:
            out[:, k * d:] += g * tap[:, : x.shape[1] - k * d]
    return out.astype(np.float32)


def gated_reverb(x, decay=1.6, hold_ms=260.0, release_ms=45.0, predelay=0.0, threshold_db=-30.0,
                 kind="room", hpf=200.0, lpf=9000.0, **extra):
    """80s "non-linear" reverb (AMS RMX16 / Phil Collins snare): a dense reverb that is
    cut off by a gate keyed from the dry send, so the tail is big but stops dead."""
    wet = reverb(x, kind, decay=decay, predelay=predelay, hpf=hpf, lpf=lpf, **extra)
    env = envelope(x, attack_ms=0.5, release_ms=5.0)
    key = env > env.max() * 10 ** (threshold_db / 20)
    hold = int(SR * hold_ms / 1000)
    # extend every open region by `hold` samples
    idx = np.flatnonzero(key)
    gate = np.zeros(x.shape[1], np.float32)
    if len(idx):
        starts = np.concatenate([[idx[0]], idx[1:][np.diff(idx) > 1]])
        ends = np.concatenate([idx[:-1][np.diff(idx) > 1], [idx[-1]]])
        for s, e in zip(starts, ends):
            gate[s: min(len(gate), e + hold)] = 1.0
    # 2 ms attack ramp, exponential release: abrupt but click-free
    att = max(1, int(SR * 0.002))
    opened = np.convolve(gate, np.ones(att) / att, mode="full")[: len(gate)]
    hop = 16
    m = opened[: len(opened) // hop * hop].reshape(-1, hop).max(axis=1)
    rel = np.exp(-hop / (SR * release_ms / 1000))
    g = np.empty_like(m)
    e = 0.0
    for i, v in enumerate(m):
        e = v if v >= e else e * rel
        g[i] = e
    g = np.repeat(g, hop)
    g = np.pad(g, (0, len(gate) - len(g)), mode="edge").astype(np.float32)
    return (wet * g).astype(np.float32)


def chorus(x, rate_hz=0.6, depth_ms=2.2, delay_ms=7.0, mix=0.5, stereo=True):
    """BBD-style chorus (Juno/JX-8P flavour): two delay lines modulated in anti-phase,
    which also widens a mono source."""
    n = x.shape[1]
    t = np.arange(n) / SR
    lfo = 2 * np.abs(2 * ((t * rate_hz) % 1.0) - 1) - 1  # triangle, -1..1
    src = x.mean(axis=0) if stereo else None
    out = np.empty_like(x)
    for ch, sign in ((0, 1.0), (1, -1.0)):
        sig = src if stereo else x[ch]
        d = (delay_ms + sign * depth_ms * lfo) * SR / 1000
        pos = np.arange(n) - d
        i0 = np.floor(pos).astype(np.int64)
        frac = pos - i0
        i0c = np.clip(i0, 0, n - 1)
        i1c = np.clip(i0 + 1, 0, n - 1)
        wet = (1 - frac) * sig[i0c] + frac * sig[i1c]
        wet[i0 < 0] = 0
        out[ch] = (1 - mix) * x[ch] + mix * wet
    return out.astype(np.float32)


def tremolo(x, rate_hz=4.5, depth=0.35, stereo=True, phase=0.0, start=0.0):
    """Rhodes Suitcase "vibrato": amplitude modulation, left and right in anti-phase when
    stereo (an auto-pan), in phase otherwise. depth 0-1. `start` (s) aligns the LFO."""
    t = (np.arange(x.shape[1]) / SR) - start
    lfo = np.sin(2 * np.pi * rate_hz * t + phase)
    g_l = 1 - depth * (0.5 + 0.5 * lfo)
    g_r = 1 - depth * (0.5 - 0.5 * lfo) if stereo else g_l
    y = np.stack([x[0] * g_l, x[1] * g_r])
    rms_in = np.sqrt(np.mean(x ** 2)) + 1e-12
    return (y * (rms_in / (np.sqrt(np.mean(y ** 2)) + 1e-12))).astype(np.float32)


def _biquad(kind, f0, gain_db=0.0, q=0.707):
    """RBJ cookbook biquad -> (b, a)."""
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    cw, sw = np.cos(w0), np.sin(w0)
    alpha = sw / (2 * q)
    if kind == "peak":
        b = [1 + alpha * A, -2 * cw, 1 - alpha * A]; a = [1 + alpha / A, -2 * cw, 1 - alpha / A]
    elif kind == "lowshelf":
        sa = 2 * np.sqrt(A) * alpha
        b = [A * ((A + 1) - (A - 1) * cw + sa), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sa)]
        a = [(A + 1) + (A - 1) * cw + sa, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sa]
    elif kind == "highshelf":
        sa = 2 * np.sqrt(A) * alpha
        b = [A * ((A + 1) + (A - 1) * cw + sa), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sa)]
        a = [(A + 1) - (A - 1) * cw + sa, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sa]
    else:
        raise ValueError(kind)
    return np.array(b) / a[0], np.array(a) / a[0]


def tape(x, drive_db=6.0, bump_db=1.5, hf_comp=True, mix=1.0):
    """Hot-to-tape colour ("recorded in the red"): pre-emphasis -> soft saturation ->
    de-emphasis, plus a low-frequency head bump. HF transients compress first, like tape."""
    y = x.astype(np.float64)
    if hf_comp:
        b, a = _biquad("highshelf", 3000, 6.0)
        y = signal.lfilter(b, a, y, axis=1)
    y = saturate(y.astype(np.float32), drive_db=drive_db, asym=0.08)
    if hf_comp:
        b, a = _biquad("highshelf", 3000, -6.0)
        y = signal.lfilter(b, a, y, axis=1)
    if bump_db:
        b, a = _biquad("peak", 75, bump_db, 0.9)
        y = signal.lfilter(b, a, y, axis=1)
    y = y.astype(np.float32)
    rms_in = np.sqrt(np.mean(x ** 2)) + 1e-12
    y = y * (rms_in / (np.sqrt(np.mean(y ** 2)) + 1e-12))
    return ((1 - mix) * x + mix * y).astype(np.float32)


def crush(x, bits=8, rate=28000.0, mulaw=False, reconstruct=True):
    """Early-sampler degradation: sample-and-hold at `rate` without anti-alias filtering
    (aliasing included), quantise to `bits` (optionally mu-law companded like the
    LinnDrum/DMX), then a DAC reconstruction low-pass."""
    n = x.shape[-1]
    idx = np.floor(np.arange(n) * rate / SR) * (SR / rate)
    held = x[..., np.minimum(idx.astype(np.int64), n - 1)]
    q = 2 ** (bits - 1)
    if mulaw:
        mu = 255.0
        c = np.sign(held) * np.log1p(mu * np.minimum(np.abs(held), 1)) / np.log1p(mu)
        c = np.round(c * q) / q
        y = np.sign(c) * np.expm1(np.abs(c) * np.log1p(mu)) / mu
    else:
        y = np.round(np.clip(held, -1, 1) * q) / q
    if reconstruct:
        sos = signal.butter(6, min(0.45 * rate, 0.45 * SR), "lp", fs=SR, output="sos")
        y = signal.sosfilt(sos, y, axis=-1)
    return y.astype(np.float32)


def varispeed(x, ratio):
    """Pitch by playback speed with zero-order hold and no interpolation: how a Mirage or
    Fairlight transposed one sample across the keyboard (grit and aliasing included)."""
    n_out = int(x.shape[-1] / ratio)
    idx = np.minimum((np.arange(n_out) * ratio).astype(np.int64), x.shape[-1] - 1)
    return x[..., idx]


def db(x: float) -> float:
    return 10 ** (x / 20)
