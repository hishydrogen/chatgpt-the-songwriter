"""Mixing and mastering driven by a declarative `song.mix` dict.

    song.mix = {
      "tracks": {
        "kick":  {"gain": 0, "eq": [("hpf", 30), ("bell", 60, 3, 1.0)],
                  "comp": {"threshold": -16, "ratio": 4, "attack": 10, "release": 80},
                  "bus": "drums", "sends": {"room": -18}},
        "bass":  {"gain": -2, "duck": {"by": "kick", "depth": 4}, "mono_below": 150},
        "pad":   {"gain": -8, "pan": 0, "width": 1.4, "sends": {"hall": -10}},
      },
      "buses":  {"drums": {"comp": {...}, "saturate": {"drive_db": 3, "mix": 0.4}}},
      "fx":     {"room": {"type": "reverb", "kind": "room", "decay": 0.8},
                 "hall": {"type": "reverb", "kind": "hall", "decay": 2.8, "predelay": 30},
                 "dly":  {"type": "delay", "beats": 0.75, "feedback": 0.3}},
      "master": {"eq": [...], "glue": {...}, "target_lufs": -14, "ceiling": -1.0},
    }

Strip order: gain staging -> eq -> comp -> saturate/tube -> duck -> pan/width -> fader
-> (post-fader sends) -> bus. Every stem is first normalised to STEM_LUFS so "gain"
values are true relative balances.
"""
from __future__ import annotations

import numpy as np
import pyloudnorm as pyln

from . import config, dsp
from .song import Song

STEM_LUFS = -20.0
_meter = None


def lufs(x: np.ndarray) -> float:
    global _meter
    if _meter is None:
        _meter = pyln.Meter(config.SAMPLE_RATE)
    v = _meter.integrated_loudness(x.T.astype(np.float64))
    return float(v) if np.isfinite(v) else -120.0


def true_peak_db(x: np.ndarray) -> float:
    from scipy import signal
    up = signal.resample_poly(x, 4, 1, axis=1)
    return float(20 * np.log10(np.max(np.abs(up)) + 1e-12))


def strip(x: np.ndarray, cfg: dict, song: Song, stems: dict[str, np.ndarray]) -> np.ndarray:
    """Insert chain of one channel or bus."""
    if cfg.get("mute"):
        return np.zeros_like(x)
    bands = list(cfg.get("eq", []))
    if "hpf" in cfg:
        bands.insert(0, ("hpf", cfg["hpf"]))
    if "lpf" in cfg:
        bands.append(("lpf", cfg["lpf"]))
    if bands:
        x = dsp.eq(x, bands)
    if "comp" in cfg:
        x = dsp.compress(x, **cfg["comp"])
    if "comp2" in cfg:            # serial second stage (e.g. fast peak + slow leveller)
        x = dsp.compress(x, **cfg["comp2"])
    if "tube" in cfg:
        x = dsp.tube(x, **cfg["tube"])
    if "saturate" in cfg:
        x = dsp.saturate(x, **cfg["saturate"])
    if "eq_post" in cfg:
        x = dsp.eq(x, cfg["eq_post"])
    if "duck" in cfg:
        d = dict(cfg["duck"])
        trig = stems[d.pop("by")]
        x = dsp.duck(x, trig, **{"depth_db": d.pop("depth", 6), **d})
    if "mono_below" in cfg:
        x = dsp.mono_bass(x, cfg["mono_below"])
    if cfg.get("mono"):
        x = dsp.width(x, 0.0)
    if "width" in cfg:
        x = dsp.width(x, cfg["width"])
    if "pan" in cfg:
        x = dsp.pan(x, cfg["pan"])
    return x * dsp.db(cfg.get("gain", 0.0))


def _fx_return(kind_cfg: dict, x: np.ndarray, song: Song) -> np.ndarray:
    c = dict(kind_cfg)
    t = c.pop("type")
    post = {k: c.pop(k) for k in ("eq", "gain", "width", "comp", "duck") if k in c}
    if t == "reverb":
        y = dsp.reverb(x, **c)
    elif t == "delay":
        beats = c.pop("beats", 0.75)
        y = dsp.delay(x, song.seconds(beats), **c)
    else:
        raise ValueError(f"unknown fx type {t}")
    return y, post


def mix(song: Song, stems: dict[str, np.ndarray], log=print) -> tuple[np.ndarray, dict]:
    """Returns (pre-master stereo mix, processed per-track signals)."""
    m = song.mix
    tcfg = m.get("tracks", {})
    n = next(iter(stems.values())).shape[1]

    # 1. gain staging: normalise every raw stem to the same loudness
    staged = {}
    for name, x in stems.items():
        lv = lufs(x)
        staged[name] = x * dsp.db(STEM_LUFS - lv) if lv > -90 else x
    # 2. channel strips
    processed, buses, sends = {}, {}, {}
    for name, x in staged.items():
        cfg = tcfg.get(name, {})
        y = strip(x, cfg, song, staged)
        processed[name] = y
        bus = cfg.get("bus", "master")
        buses[bus] = buses.get(bus, 0) + y
        for fx, level in cfg.get("sends", {}).items():
            sends[fx] = sends.get(fx, 0) + y * dsp.db(level)
        log(f"  strip {name:<12} raw {lufs(x):6.1f} LUFS -> {lufs(y):6.1f} LUFS  -> {bus}")
    # 3. buses (may also send to fx)
    out = buses.pop("master", np.zeros((2, n), np.float32))
    for bus, x in buses.items():
        cfg = m.get("buses", {}).get(bus, {})
        y = strip(x, cfg, song, staged)
        processed[f"bus:{bus}"] = y
        for fx, level in cfg.get("sends", {}).items():
            sends[fx] = sends.get(fx, 0) + y * dsp.db(level)
        log(f"  bus   {bus:<12} {lufs(y):6.1f} LUFS")
        out = out + y
    # 4. fx returns -> master
    for fx, fcfg in m.get("fx", {}).items():
        if fx not in sends:
            continue
        y, post = _fx_return(fcfg, sends[fx], song)
        y = strip(y, post, song, staged)
        processed[f"fx:{fx}"] = y
        log(f"  fx    {fx:<12} {lufs(y):6.1f} LUFS")
        out = out + y
    return out.astype(np.float32), processed


def master(x: np.ndarray, cfg: dict, log=print) -> tuple[np.ndarray, dict]:
    """Master chain: eq -> glue comp -> (sat) -> loudness-targeted limiting."""
    target = cfg.get("target_lufs", config.TARGET_LUFS)
    ceiling = cfg.get("ceiling", config.TRUE_PEAK_CEILING_DB)
    # headroom into the chain
    x = x * dsp.db(-18.0 - lufs(x))
    bands = list(cfg.get("eq", []))
    if bands:
        x = dsp.eq(x, bands)
    if "glue" in cfg:
        x = dsp.compress(x, **cfg["glue"])
    if "saturate" in cfg:
        x = dsp.saturate(x, **cfg["saturate"])
    if "width" in cfg:
        x = dsp.width(x, cfg["width"])
    x = dsp.mono_bass(x, cfg.get("mono_below", 100))
    # loudness: iterate input gain into the limiter until integrated LUFS hits target
    gain = target - lufs(x)
    y = x
    for i in range(4):
        y = dsp.limit(x * dsp.db(gain), ceiling_db=ceiling - 0.3, **cfg.get("limiter", {}))
        err = target - lufs(y)
        if abs(err) < 0.1:
            break
        gain += err
    tp = true_peak_db(y)
    if tp > ceiling:  # inter-sample overs left after the limiter: trim
        y = y * dsp.db(ceiling - tp)
        tp = ceiling
    stats = {"lufs": round(lufs(y), 2), "true_peak": round(tp, 2), "limiter_drive_db": round(gain, 2)}
    log(f"  master: {stats}")
    return y.astype(np.float32), stats
