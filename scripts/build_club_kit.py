#!/usr/bin/env python3
"""Build drums.club: a clean electronic kit synthesised from scratch (sines, noise and
808-style square clusters), for modern dance-pop / vocaloid tracks. Self-made, so it is
fine for releases.

  python scripts/build_club_kit.py   -> libs/_generated/drums.club.sfz (+ .json sidecar)
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from songwriter import config  # noqa: E402
from songwriter.vintage import GEN, Kit, Machine, Voice  # noqa: E402

SR = config.SAMPLE_RATE
CLEAN = Machine(rate=SR, bits=24, out_lpf=20000)
rng = np.random.default_rng(7)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def env(t, attack=0.001, decay=0.2, curve=1.0):
    a = np.clip(t / attack, 0, 1)
    return a * np.exp(-(t / decay) ** curve)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, min(hi, 0.45 * SR)], "bandpass", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "highpass", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "lowpass", fs=SR, output="sos"), x)


def noise(n):
    return rng.standard_normal(n)


def sweep_sine(t, f_end, f_add, tau):
    f = f_end + f_add * np.exp(-t / tau)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def norm(x, peak=0.9):
    return x / (np.abs(x).max() + 1e-12) * peak


def kick_house():
    t = t_(0.55)
    body = sweep_sine(t, 49, 150, 0.032) * env(t, 0.0005, 0.30, 1.6)
    click = hp(noise(len(t)), 2500) * env(t, 0.0002, 0.004)
    return norm(np.tanh(1.8 * (body + 0.35 * click)))


def kick_808():
    t = t_(1.3)
    body = sweep_sine(t, 44, 70, 0.045) * env(t, 0.0005, 0.85, 1.3)
    click = hp(noise(len(t)), 3000) * env(t, 0.0002, 0.003)
    return norm(np.tanh(1.3 * (body + 0.2 * click)))


def kick_punch():
    t = t_(0.35)
    body = sweep_sine(t, 58, 220, 0.022) * env(t, 0.0003, 0.16, 1.4)
    click = bp(noise(len(t)), 1500, 9000) * env(t, 0.0002, 0.006)
    return norm(np.tanh(2.5 * (body + 0.5 * click)))


def snare():
    t = t_(0.35)
    tone = (np.sin(2 * np.pi * 186 * t) + 0.6 * np.sin(2 * np.pi * 332 * t)) * env(t, 0.0005, 0.07)
    nz = bp(noise(len(t)), 1800, 11000) * env(t, 0.0005, 0.13, 1.2)
    return norm(np.tanh(1.5 * (0.8 * tone + nz)))


def clap():
    t = t_(0.45)
    x = np.zeros(len(t))
    for k, d in enumerate((0.0, 0.009, 0.019, 0.030)):
        tt = np.clip(t - d, 0, None)
        x += (t >= d) * env(tt, 0.0003, 0.006 if k < 3 else 0.09) * (0.8 if k < 3 else 1.0)
    y = bp(noise(len(t)), 900, 5200, 2) * x
    y += 0.25 * bp(noise(len(t)), 600, 2500) * env(t, 0.01, 0.16) * (t > 0.03)
    return norm(y)


def metal(t, freqs=(205.3, 304.4, 369.6, 522.7, 540.0, 800.0)):
    return sum(signal.square(2 * np.pi * f * t) for f in freqs) / len(freqs)


def hat(decay, tone=0.6):
    t = t_(max(0.12, decay * 5))
    m = hp(bp(metal(t), 6000, 16000, 2), 7000)
    nz = hp(noise(len(t)), 8000)
    return norm((tone * m + (1 - tone) * 0.5 * nz) * env(t, 0.0003, decay))


def shaker():
    t = t_(0.15)
    return norm(hp(noise(len(t)), 5500, 4) * env(t, 0.012, 0.04, 1.5) * (1 - np.exp(-t / 0.01)))


def rim():
    t = t_(0.12)
    tone = np.sin(2 * np.pi * 1720 * t) * env(t, 0.0002, 0.012) + 0.6 * np.sin(2 * np.pi * 820 * t) * env(t, 0.0002, 0.02)
    return norm(tone + 0.3 * hp(noise(len(t)), 3000) * env(t, 0.0002, 0.004))


def crash():
    t = t_(2.6)
    m = hp(metal(t, (205.3, 304.4, 369.6, 522.7, 540.0, 800.0, 1080.0, 1395.0)), 3500)
    nz = hp(noise(len(t)), 4000)
    return norm((0.5 * m + 0.7 * nz) * env(t, 0.001, 0.9, 0.9))


def tom(f):
    t = t_(0.6)
    return norm(np.tanh(1.4 * sweep_sine(t, f, f * 0.6, 0.05) * env(t, 0.0005, 0.22)))


def snap():
    t = t_(0.2)
    return norm(bp(noise(len(t)), 1800, 7000) * env(t, 0.0003, 0.022) + 0.3 * np.sin(2 * np.pi * 2100 * t) * env(t, 0.0002, 0.01))


def riser(bars=2, bpm=132):
    """Noise sweep that ends exactly `bars` later (lands on the next downbeat)."""
    dur = bars * 240 / bpm
    t = t_(dur)
    x = noise(len(t))
    out = np.zeros(len(t))
    blk = 1024
    for i in range(0, len(t), blk):
        u = i / len(t)
        f = 300 * (9000 / 300) ** (u ** 1.5)
        seg = bp(x[max(0, i - 4096):i + blk], f * 0.7, f * 1.4)[-min(blk, len(t) - i):]
        out[i:i + len(seg)] = seg
    amp = (t / dur) ** 2.2
    return norm(out * amp * (1 - np.exp(-(dur - t) / 0.004)))


def impact():
    t = t_(2.5)
    sub = sweep_sine(t, 36, 40, 0.15) * env(t, 0.001, 0.9, 1.2)
    nz = lp(noise(len(t)), 2500) * env(t, 0.001, 0.35)
    return norm(np.tanh(1.5 * (sub + 0.5 * nz)))


def main():
    voices = {
        "kick": Voice(36, kick_house()), "kick_808": Voice(35, kick_808()), "kick_punch": Voice(34, kick_punch()),
        "snare": Voice(38, snare()), "clap": Voice(39, clap()), "rim": Voice(37, rim()), "snap": Voice(40, snap()),
        "hh_closed": Voice(42, hat(0.035), sfz="group=1"), "hh_pedal": Voice(44, hat(0.02, 0.4), sfz="group=1"),
        "hh_open": Voice(46, hat(0.32), sfz="group=2 off_by=1"),
        "shaker": Voice(70, shaker()), "crash": Voice(49, crash()),
        "riser": Voice(60, riser()), "impact": Voice(61, impact()),
        "tom_low": Voice(41, tom(98)), "tom_mid": Voice(45, tom(130)), "tom_high": Voice(48, tom(175)),
    }
    sfz, drum_map = Kit("drums.club", "Clean electronic kit synthesised from scratch (self-made, releasable).",
                        voices, CLEAN, amp_veltrack=55).run()
    (GEN / "drums.club.json").write_text(json.dumps({
        "desc": "Clean electronic dance kit, synthesised (house kick, 808 kick, punch kick, clap, snare, "
                "808-style hats, shaker, rim, snap, crash, toms). Self-made: releasable.",
        "drum_map": drum_map, "tail": 2.5}, ensure_ascii=False, indent=1))
    print(sfz)


if __name__ == "__main__":
    main()
