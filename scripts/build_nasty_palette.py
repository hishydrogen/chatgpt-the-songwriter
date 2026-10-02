#!/usr/bin/env python3
"""Build the mid-80s Minneapolis palette (Jam & Lewis / Control era) from CC0 sources.

  drums.linn86        LinnDrum-style kit: CC0 one-shots through 28 kHz mu-law 8-bit
                      converters, synthesized claps, CC0 metal hits for industrial layers
  mirage.timpani      VSCO timpani, pitch-measured, stretched across the keys Mirage-style
  mirage.metal        pitched metal hit (anvil/brake drum family) for "metallic licks"
  fairlight.orchhit   orchestra hit made the way ORCH5 was: a whole orchestra on one chord,
  fairlight.orchhit_m sampled to 8 bit and played chromatically (major / minor)
  mirage.bass_*       crunchy bass candidates: sources sampled high, played low on 8 bit

Everything lands in libs/_generated and appears in `python -m songwriter instruments`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from songwriter import config, dsp, render  # noqa: E402
from songwriter.instruments import Instrument, get_instrument, surge  # noqa: E402
from songwriter.song import Song  # noqa: E402
from songwriter.vintage import (FAIRLIGHT, GEN, LINNDRUM, MIRAGE, Bake, Kit, Source,  # noqa: E402
                                Voice)

SR = config.SAMPLE_RATE
LIB = config.LIB_DIR
rng = np.random.default_rng(1986)


# -- helpers ---------------------------------------------------------------

def render_notes(instrument: str | Instrument, notes, seconds=2.5, ccs=()):
    """Render [(pitch, vel, dur_beats)] at beat 0 (bpm 60) through any instrument."""
    s = Song("tmp", bpm=60)
    iid = instrument
    if isinstance(instrument, Instrument):
        from songwriter.instruments import register
        register(instrument)
        iid = instrument.id
    t = s.track("t", iid)
    for cc, val in ccs:
        t.cc(cc, val, 0.0)
    for p, v, d in notes:
        t.note(p, 0.01, d, v)
    s.length_beats = seconds
    inst = get_instrument(iid)
    return render.ENGINES[inst.engine](s, t, inst, int(seconds * SR))


def sfz_hit(rel_sfz: str, key: int, vel=110, seconds=2.0, ccs=()):
    inst = Instrument(f"tmp.{abs(hash((rel_sfz, key)))}", "sfz", rel_sfz, tail=seconds)
    return render_notes(inst, [(key, vel, 0.25)], seconds, ccs)


def wav(path: Path) -> np.ndarray:
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    x = x.T
    if sr != SR:
        x = signal.resample_poly(x, SR, sr, axis=1).astype(np.float32)
    return x


def start(x, thr_db=-40):
    a = np.abs(x).max(axis=0)
    i = int(np.argmax(a > a.max() * 10 ** (thr_db / 20)))
    return x[:, max(0, i - 24):]


def env_cut(x, seconds, fade=0.03):
    n = min(x.shape[1], int(seconds * SR))
    y = x[:, :n].copy()
    f = int(fade * SR)
    y[:, -f:] *= np.linspace(1, 0, f)
    return y


def eq(x, bands):
    return dsp.eq(x, bands)


def f0_midi(x: np.ndarray) -> float:
    m = x.mean(axis=0)
    a = int(np.argmax(np.abs(m) > 0.1 * np.abs(m).max()))
    seg = m[a + int(0.03 * SR): a + int(0.03 * SR) + int(0.35 * SR)]
    seg = seg * np.hanning(len(seg))
    n = 1 << 17
    spec = np.abs(np.fft.rfft(seg, n))
    freqs = np.fft.rfftfreq(n, 1 / SR)
    lo, hi = np.searchsorted(freqs, [40, 1500])
    k = lo + int(np.argmax(spec[lo:hi]))
    return 69 + 12 * np.log2(freqs[k] / 440)


def sidecar(iid, **meta):
    (GEN / f"{iid}.json").write_text(json.dumps(meta, indent=1))


# -- 1. drums.linn86 -------------------------------------------------------------

def synth_clap(seed=0, bursts=4, spread_ms=9.0, tail_s=0.16, center=1150.0):
    """Hand clap the way drum machines voiced it: a few noise bursts in quick
    succession (several people) plus a band-passed diffuse tail."""
    r = np.random.default_rng(seed)
    n = int(SR * 0.45)
    y = np.zeros(n)
    t = 0
    for b in range(bursts):
        L = int(SR * 0.006)
        burst = r.standard_normal(L) * np.exp(-np.arange(L) / (SR * 0.0025)) * (0.7 + 0.3 * r.random())
        y[t:t + L] += burst
        t += int(SR * (spread_ms + r.normal(0, 1.5)) / 1000)
    tail = r.standard_normal(n - t) * np.exp(-np.arange(n - t) / (SR * tail_s / 3))
    y[t:] += 0.8 * tail
    sos = signal.butter(2, [center / 1.9, center * 2.4], "bandpass", fs=SR, output="sos")
    y = signal.sosfilt(sos, y)
    b, a = dsp._biquad("peak", center, 4.0, 1.2)
    y = signal.lfilter(b, a, y)
    st = np.stack([y, np.roll(y, int(SR * 0.0007))]).astype(np.float32)  # tiny stereo smear
    return st / np.abs(st).max()


def build_drums():
    V = "VirtuosityDrums/Programs"
    kick = start(sfz_hit(f"{V}/03-kick-mic.sfz", 36, 118, 1.2))
    kick = eq(env_cut(kick, 0.42), [("hpf", 30, 2), ("bell", 65, 4, 1.0), ("bell", 380, -5, 1.2),
                                    ("bell", 3200, 4, 1.0)])
    snare = start(sfz_hit(f"{V}/04-snare-mic.sfz", 38, 120, 1.2))
    snare = eq(env_cut(snare, 0.38), [("hpf", 90), ("bell", 220, 3, 1.2), ("bell", 900, -3, 1.0),
                                      ("bell", 4500, 4, 0.9)])
    snare_rim = start(sfz_hit(f"{V}/04-snare-mic.sfz", 40, 120, 1.2))
    snare_rim = eq(env_cut(snare_rim, 0.35), [("hpf", 120), ("bell", 3500, 3, 1.0)])
    sidestick = start(sfz_hit(f"{V}/02-full-kit.sfz", 37, 110, 0.8))
    sidestick = eq(env_cut(sidestick, 0.2), [("hpf", 300)])
    hh_c = start(sfz_hit(f"{V}/05-oh-mic.sfz", 42, 100, 0.6, ccs=[(4, 127)]))
    hh_c = eq(env_cut(hh_c, 0.12, 0.02), [("hpf", 3000, 2), ("hshelf", 9000, 3)])
    hh_o = start(sfz_hit(f"{V}/05-oh-mic.sfz", 42, 100, 1.4, ccs=[(4, 0)]))
    hh_o = eq(env_cut(hh_o, 0.55, 0.12), [("hpf", 2500, 2), ("hshelf", 9000, 2)])
    hh_p = start(sfz_hit(f"{V}/05-oh-mic.sfz", 44, 100, 0.6))
    hh_p = eq(env_cut(hh_p, 0.12, 0.02), [("hpf", 2500, 2)])
    crash = start(sfz_hit(f"{V}/05-oh-mic.sfz", 49, 115, 3.0))
    crash = eq(env_cut(crash, 1.6, 0.6), [("hpf", 400, 2)])
    ride = start(sfz_hit(f"{V}/05-oh-mic.sfz", 51, 100, 2.0))
    ride = eq(env_cut(ride, 0.9, 0.4), [("hpf", 400, 2)])
    tom_hi = start(sfz_hit(f"{V}/06-mid-mic.sfz", 48, 115, 1.5))
    tom_lo = start(sfz_hit(f"{V}/06-mid-mic.sfz", 41, 115, 1.5))
    tom_hi = eq(env_cut(tom_hi, 0.55, 0.15), [("hpf", 70), ("bell", 450, -3, 1.0), ("bell", 4000, 3, 1.0)])
    tom_lo = eq(env_cut(tom_lo, 0.7, 0.2), [("hpf", 50), ("bell", 450, -3, 1.0), ("bell", 4000, 3, 1.0)])
    shaker = start(sfz_hit(f"{V}/02-full-kit.sfz", 82, 100, 0.6))
    cabasa = start(sfz_hit(f"{V}/02-full-kit.sfz", 69, 100, 0.6))
    P = LIB / "VSCO2CE/Percussion"
    cowbell = env_cut(start(wav(P / "Cowbell1_Hit_v3_rr1_Sum.wav") if (P / "Cowbell1_Hit_v3_rr1_Sum.wav").exists()
                            else wav(sorted(P.glob("Cowbell1_Hit*"))[-1])), 0.45, 0.1)
    tamb = env_cut(start(wav(sorted(P.glob("Tamb1-Hit*"))[-1])), 0.45, 0.1)
    M = LIB / "VSCO2CE/Miscellania Raw/Misc 1"
    metals = {f"metal{i}": env_cut(start(wav(M / f"metal_hit{i}.wav")), 0.6, 0.2)
              for i in (1, 2, 3, 4, 5, 6) if (M / f"metal_hit{i}.wav").exists()}
    anvil = env_cut(start(wav(sorted(P.glob("Anvil_Hit1*"))[-1])), 0.7, 0.2)
    brake = env_cut(start(wav(sorted(P.glob("BrakeDrum1_Hammer*"))[-1])), 0.6, 0.2)
    clap = synth_clap(1)
    clap2 = synth_clap(7, bursts=5, spread_ms=11, center=1000)

    voices = {
        "kick": Voice(36, kick, tune=-0.5, gain_db=0), "snare": Voice(38, snare, tune=0.7),
        "snare_rim": Voice(40, snare_rim), "sidestick": Voice(37, sidestick),
        "clap": Voice(39, clap), "clap2": Voice(54, clap2),
        "hh_closed": Voice(42, hh_c, sfz="group=1"), "hh_pedal": Voice(44, hh_p, sfz="group=1"),
        "hh_open": Voice(46, hh_o, sfz="group=2 off_by=1"),
        "tom_high": Voice(48, tom_hi, tune=1), "tom_mid": Voice(45, tom_hi, tune=-3),
        "tom_low": Voice(41, tom_lo),
        "crash": Voice(49, crash), "ride": Voice(51, ride), "cowbell": Voice(56, cowbell, tune=1),
        "tambourine": Voice(55, tamb), "shaker": Voice(70, shaker), "cabasa": Voice(69, cabasa),
        "anvil": Voice(60, anvil), "brake": Voice(61, brake),
    }
    for i, (name, a) in enumerate(metals.items()):
        voices[name] = Voice(62 + i, a)
    sfz, drum_map = Kit("drums.linn86", "LinnDrum-style kit rebuilt from CC0 sources (28 kHz mu-law 8-bit).",
                        voices, LINNDRUM, amp_veltrack=45).run()
    sidecar("drums.linn86", desc="LinnDrum-style 80s drum machine (CC0 sources, 8-bit mu-law). Clap/claps "
            "synthesized; metal/anvil/brake for industrial layers.", drum_map=drum_map, tail=2.0)
    print("  drums.linn86:", ", ".join(drum_map))


# -- 2. mirage.timpani ------------------------------------------------------------

def build_timpani():
    # Principal tones read from each drum's partial series (ratios ~1 : 1.5 : 2 : 2.45),
    # not from the loudest peak: a timpani's loudest partial is often the fifth above.
    T = LIB / "VSCO2CE/Percussion/Timpani"
    principal = {1: 41.47, 2: 46.70, 3: 49.52, 4: 52.50, 5: 54.80}
    srcs = []
    for drum, root in principal.items():
        layers = (("v1", 1, 70), ("v4" if drum != 1 else "v3", 71, 127))
        for vname, lo, hi in layers:
            x = start(wav(T / f"Timpani{drum}_Hit_{vname}_rr1_Sum.wav"))
            srcs.append(Source(env_cut(x, 2.5, 0.4), root, lo, hi))
    Bake("mirage.timpani", "Timpani sampled into a Mirage: 8-bit, played across the keys by speed.",
         srcs, range(31, 80), MIRAGE, {"loop_mode": "one_shot", "amp_veltrack": "70"}, max_s=2.5).run()
    sidecar("mirage.timpani", desc="Mirage-style 8-bit timpani (VSCO CC0). Quirky melodic timpani lines.",
            range=[31, 79], tail=2.5)


# -- 3. mirage.metal ---------------------------------------------------------------

def build_metal():
    M = LIB / "VSCO2CE/Miscellania Raw/Misc 1"
    x = env_cut(start(wav(M / "metal_hit3.wav")), 1.2, 0.3)
    root = int(round(f0_midi(x)))
    Bake("mirage.metal", "Metal hit sampled into a Mirage, played as a pitched instrument.",
         [Source(x, root)], range(36, 90), MIRAGE, {"loop_mode": "one_shot", "amp_veltrack": "60"},
         max_s=1.5).run()
    sidecar("mirage.metal", desc="Pitched 8-bit metal hit (VSCO CC0). Industrial metallic licks/bell.",
            range=[36, 89], tail=1.5)
    print("  mirage.metal root", root)


# -- 4. fairlight.orchhit ------------------------------------------------------------

def build_orchhit():
    # one chord through the whole orchestra, everyone short and loud, like ORCH5
    for iid, third in (("fairlight.orchhit", 4), ("fairlight.orchhit_m", 3)):
        C = 48  # C3 root
        parts = {
            "strings.contrabass_spic": [C - 12, C],
            "strings.celli_spic": [C, C + 7],
            "strings.violas_spic": [C + 12 + third, C + 19],
            "strings.violins_spic": [C + 24, C + 24 + third, C + 31],
            "brass.horn_stac": [C + 12, C + 12 + third, C + 19],
            "brass.trumpet_stac": [C + 24, C + 24 + third],
            "brass.trombone_stac": [C, C + 7, C + 12],
            "brass.tuba_stac": [C - 12],
            "winds.flute_stac": [C + 36],
        }
        mix = np.zeros((2, int(SR * 1.6)), np.float32)
        for inst, notes in parts.items():
            y = render_notes(inst, [(n, 127, 0.4) for n in notes], 1.6)
            mix += y / (np.sqrt(np.mean(y ** 2)) + 1e-9) * 0.05
        timp = start(wav(sorted((LIB / "VSCO2CE/Percussion/Timpani").glob("Timpani3_Hit_v4_rr1_Sum.wav"))[0]))
        bd = start(wav(sorted((LIB / "VSCO2CE/Percussion").glob("BDrumNewhit_v7_rr1_Sum.wav"))[0]))
        for extra, g in ((timp, 0.6), (bd, 0.5)):
            n = min(mix.shape[1], extra.shape[1])
            mix[:, :n] += extra[:, :n] / np.abs(extra).max() * g * np.abs(mix).max()
        mix = env_cut(start(mix, -30), 0.9, 0.35)
        mix = dsp.eq(mix, [("hpf", 60), ("bell", 2500, 3, 0.8)])
        Bake(iid, f"Orchestra hit ({'major' if third == 4 else 'minor'}), Fairlight/ORCH5 style, 8-bit.",
             [Source(mix, C)], range(36, 85), FAIRLIGHT, {"loop_mode": "one_shot", "amp_veltrack": "40"},
             max_s=1.0).run()
        sidecar(iid, desc=f"80s orchestra hit, {'major' if third == 4 else 'minor'} chord (VSCO CC0 -> 8-bit).",
                range=[36, 84], tail=1.0)
        print(f"  {iid} baked")


# -- 5. crunchy bass candidates ------------------------------------------------------

def build_basses():
    filt = {"fil_type": "lpf_4p", "cutoff": "650", "resonance": "6", "fil_veltrack": "1800",
            "fileg_depth": "2600", "fileg_attack": "0", "fileg_decay": "0.22", "fileg_sustain": "15",
            "fileg_release": "0.08", "ampeg_release": "0.06", "ampeg_sustain": "100"}
    cands = {
        # sampled high (C3) and played two octaves down: the Mirage "misused sample" crunch
        "mirage.bass_fm": (surge("Basses/FM Bass 2"), 48, "FM bass sampled at C3, played low on an 8-bit Mirage"),
        "mirage.bass_brass": (surge("Brass/OB-8 Jump"), 48, "OB-8 style brass sampled at C3, played as bass (car-horn trick)"),
        "mirage.bass_finger": ("bass.darkblack_bright", 40, "Electric bass (CC0) sampled at E2, 8-bit Mirage"),
    }
    for iid, (src, root, desc) in cands.items():
        x = render_notes(src, [(root, 115, 1.6)], 2.2)
        x = env_cut(start(x, -35), 1.8, 0.1)
        Bake(iid, desc, [Source(x, root)], range(24, 61), MIRAGE, filt, max_s=1.8).run()
        sidecar(iid, desc=desc + " (lpf_4p filter env).", range=[24, 60], tail=0.5)
        print(f"  {iid} baked")


if __name__ == "__main__":
    steps = sys.argv[1:] or ["drums", "timpani", "metal", "orchhit", "basses"]
    for st in steps:
        print(f"build {st}")
        globals()[f"build_{st}"]()
