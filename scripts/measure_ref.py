#!/usr/bin/env python3
"""Measure a reference track: tempo, swing and micro-timing, key and tuning (with key
changes), band balance relative to the mid band, loudness (LUFS / PLR / LRA), structure
and energy per N bars.

  python scripts/measure_ref.py refs/song.wav [--out refs/song] [--bars 4] [--k 6]
         [--downbeat 0.0] [--sections "intro:0,verse:8,..."]

Writes <out>.measure.json and <out>.measure.png. The numbers are design targets only:
never copy a reference's melody, riff or hook, and never commit or sample its audio.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import scipy.ndimage
import scipy.linalg
import scipy.sparse.csgraph
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from songwriter import analyze, config  # noqa: E402
from songwriter.__main__ import read_audio  # noqa: E402
from songwriter.mix import lufs  # noqa: E402

SR_A = 22050       # analysis rate for librosa features
HOP = 256
NOTES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
# Krumhansl-Kessler key profiles
KK_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def key_of(chroma_vec: np.ndarray) -> tuple[str, float, list]:
    """Best key for a 12-bin chroma vector, its correlation, and the top 3 candidates."""
    scores = []
    for tonic in range(12):
        for mode, prof in (("major", KK_MAJ), ("minor", KK_MIN)):
            r = np.corrcoef(chroma_vec, np.roll(prof, tonic))[0, 1]
            scores.append((float(r), f"{NOTES[tonic]} {mode}"))
    scores.sort(reverse=True)
    return scores[0][1], scores[0][0], [(k, round(r, 3)) for r, k in scores[:3]]


def beat_track(y, sr):
    import librosa
    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP, aggregate=np.median)
    tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=HOP,
                                           tightness=400, units="frames")
    return float(np.atleast_1d(tempo)[0]), beats, oenv


def band_onsets(x48: np.ndarray, lo: float, hi: float | None):
    """Onset strength envelope of one frequency band (48 kHz input), hop 256 (5.3 ms)."""
    import librosa
    mono = x48.mean(axis=0)
    if hi is None:
        sos = signal.butter(4, lo, "hp", fs=config.SAMPLE_RATE, output="sos")
    else:
        sos = signal.butter(4, [lo, hi], "bandpass", fs=config.SAMPLE_RATE, output="sos")
    band = signal.sosfiltfilt(sos, mono).astype(np.float32)
    env = librosa.onset.onset_strength(y=band, sr=config.SAMPLE_RATE, hop_length=HOP, lag=1,
                                       max_size=1)
    t = librosa.frames_to_time(np.arange(len(env)), sr=config.SAMPLE_RATE, hop_length=HOP)
    return t, env


def swing_profile(onset_times, onset_strength, beat_times):
    """Phase of each onset inside its beat (0-1), weighted histogram, 16th positions."""
    phases, weights = [], []
    for t, w in zip(onset_times, onset_strength):
        i = np.searchsorted(beat_times, t) - 1
        if i < 0 or i >= len(beat_times) - 1:
            continue
        b0, b1 = beat_times[i], beat_times[i + 1]
        phases.append((t - b0) / (b1 - b0))
        weights.append(w)
    phases, weights = np.array(phases), np.array(weights)
    hist, edges = np.histogram(phases, bins=100, range=(0, 1), weights=weights)
    centers = (edges[:-1] + edges[1:]) / 2

    def peak(lo, hi):
        m = (centers >= lo) & (centers < hi)
        if not m.any() or hist[m].sum() == 0:
            return None
        # weighted centroid around the argmax (robust to a flat top)
        j = np.flatnonzero(m)[np.argmax(hist[m])]
        win = slice(max(0, j - 3), min(len(hist), j + 4))
        return float(np.sum(centers[win] * hist[win]) / np.sum(hist[win]))

    # the downbeat peak may wrap around 0/1; measure everything relative to it
    wrapped = np.where(phases > 0.9, phases - 1, phases)
    near0 = (wrapped > -0.1) & (wrapped < 0.1)
    p0 = float(np.average(wrapped[near0], weights=weights[near0])) if near0.any() else 0.0
    p_e, p_and, p_a = peak(0.15, 0.40), peak(0.40, 0.62), peak(0.62, 0.92)
    rel = {k: (None if v is None else round(v - p0, 4)) for k, v in
           (("e", p_e), ("and", p_and), ("a", p_a))}
    # swing in Song.swing() terms: share of the pair taken by the first note
    sw16 = None
    if rel["e"] is not None and rel["and"] is not None and rel["a"] is not None:
        sw16 = round(((rel["e"]) / rel["and"] + (rel["a"] - rel["and"]) / (1 - rel["and"])) / 2, 3)
    sw8 = None if rel["and"] is None else round(rel["and"], 3)
    # micro-timing: spread of onsets around each 16th slot (ms, using median beat length)
    spb = float(np.median(np.diff(beat_times)))
    spread = {}
    for name, centre in (("1", p0), ("e", p_e), ("and", p_and), ("a", p_a)):
        if centre is None:
            continue
        d = wrapped - centre if name == "1" else phases - centre
        m = np.abs(d) < 0.08
        if m.sum() > 10:
            spread[name] = round(float(np.sqrt(np.average(d[m] ** 2, weights=weights[m])) * spb * 1000), 1)
    accent = {}
    for name, centre in (("1", p0), ("e", p_e), ("and", p_and), ("a", p_a)):
        if centre is None:
            continue
        d = wrapped - centre if name == "1" else phases - centre
        m = np.abs(d) < 0.06
        accent[name] = float(np.mean(weights[m])) if m.any() else 0.0
    top = max(accent.values()) or 1.0
    accent = {k: round(20 * np.log10(v / top + 1e-9), 1) for k, v in accent.items()}
    return {"offset_of_beat_peak": round(p0, 4), "positions": rel, "swing_16th": sw16,
            "swing_8th": sw8, "timing_spread_ms": spread, "accent_db": accent,
            "hist": hist.tolist()}


def laplacian_segments(Csync, Msync, k):
    """McFee & Ellis (2014) spectral clustering of beat-synchronous features."""
    import librosa
    from sklearn.cluster import KMeans
    R = librosa.segment.recurrence_matrix(Csync, width=3, mode="affinity", sym=True)
    df = librosa.segment.timelag_filter(scipy.ndimage.median_filter)
    Rf = df(R, size=(1, 7))
    path_distance = np.sum(np.diff(Msync, axis=1) ** 2, axis=0)
    sigma = np.median(path_distance)
    path_sim = np.exp(-path_distance / sigma)
    R_path = np.diag(path_sim, k=1) + np.diag(path_sim, k=-1)
    deg_path, deg_rec = np.sum(R_path, axis=1), np.sum(Rf, axis=1)
    mu = deg_path.dot(deg_path + deg_rec) / np.sum((deg_path + deg_rec) ** 2)
    A = mu * Rf + (1 - mu) * R_path
    L = scipy.sparse.csgraph.laplacian(A, normed=True)
    _, evecs = scipy.linalg.eigh(L)
    evecs = scipy.ndimage.median_filter(evecs, size=(9, 1))
    Cnorm = np.cumsum(evecs ** 2, axis=1) ** 0.5
    X = evecs[:, :k] / (Cnorm[:, k - 1:k] + 1e-9)
    return KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X), R


def main():
    import librosa
    p = argparse.ArgumentParser()
    p.add_argument("audio")
    p.add_argument("--out")
    p.add_argument("--bars", type=int, default=4, help="bars per energy block")
    p.add_argument("--k", type=int, default=6, help="number of section types to cluster")
    p.add_argument("--downbeat", type=float, help="time (s) of a known downbeat (bar 1)")
    a = p.parse_args()
    src = Path(a.audio)
    out = Path(a.out) if a.out else src.with_suffix("")
    x48 = read_audio(src)
    dur = x48.shape[1] / config.SAMPLE_RATE
    mono = x48.mean(axis=0)
    y = librosa.resample(mono, orig_sr=config.SAMPLE_RATE, target_sr=SR_A)
    res: dict = {"file": src.name, "duration_s": round(dur, 2)}

    # -- loudness, dynamics, stereo, tonal balance -----------------------------------
    st = analyze.stats(x48)
    bands = st.pop("bands_db")
    st["bands_rel_mid_db"] = {b: round(v - bands["mid"], 1) for b, v in bands.items()}
    fc, lv = analyze.third_octave(x48)
    mid_ref = np.mean([l for f, l in zip(fc, lv) if 400 <= f < 1500])
    st["third_octave_rel_mid_db"] = {str(f): round(l - mid_ref, 1) for f, l in zip(fc, lv)}
    res["loudness"] = st

    # -- tempo --------------------------------------------------------------------------
    tempo, beats, oenv = beat_track(y, SR_A)
    bt = librosa.frames_to_time(beats, sr=SR_A, hop_length=HOP)
    ibi = np.diff(bt)
    local = 60 / ibi
    win = 16
    roll = [float(np.median(local[i:i + win])) for i in range(0, max(1, len(local) - win), 4)]
    res["tempo"] = {"beat_track_bpm": round(tempo, 2), "median_bpm": round(float(np.median(local)), 2),
                    "mean_bpm": round(float(60 / np.mean(ibi)), 2),
                    "iqr_bpm": [round(float(np.percentile(local, 25)), 2), round(float(np.percentile(local, 75)), 2)],
                    "rolling16_min_max": [round(min(roll), 2), round(max(roll), 2)],
                    "n_beats": int(len(bt)), "first_beat_s": round(float(bt[0]), 3)}

    # -- swing / micro-timing / accents (hi-hat band and full band) -------------------------
    sw = {}
    for name, lo, hi in (("hats", 6000, None), ("snare", 1500, 5000), ("kick", 30, 120), ("full", 30, None)):
        t, env = band_onsets(x48, lo, hi)
        on = librosa.onset.onset_detect(onset_envelope=env, sr=config.SAMPLE_RATE, hop_length=HOP,
                                        backtrack=False, units="frames", delta=0.05)
        sw[name] = swing_profile(t[on], env[on], bt)
        sw[name]["onsets"] = int(len(on))
    res["swing"] = {k: {kk: vv for kk, vv in v.items() if kk != "hist"} for k, v in sw.items()}

    # -- bar grid: choose the downbeat phase -------------------------------------------------
    _, kenv = band_onsets(x48, 30, 120)
    _, senv = band_onsets(x48, 1500, 5000)
    tt = librosa.frames_to_time(np.arange(len(kenv)), sr=config.SAMPLE_RATE, hop_length=HOP)
    kick_at = np.interp(bt, tt, kenv)
    snare_at = np.interp(bt, tt, senv)
    y_h = librosa.effects.harmonic(y, margin=3)
    tuning = float(librosa.estimate_tuning(y=y_h, sr=SR_A))
    chroma = librosa.feature.chroma_cqt(y=y_h, sr=SR_A, hop_length=HOP, tuning=tuning)
    csync = librosa.util.sync(chroma, beats, aggregate=np.median)
    cs = csync / (np.linalg.norm(csync, axis=0, keepdims=True) + 1e-9)
    nov = np.concatenate([[0], 1 - np.sum(cs[:, 1:] * cs[:, :-1], axis=0)])
    phase_scores = {}
    for ph in range(4):
        idx = np.arange(len(bt))
        on1 = (idx - ph) % 4 == 0
        on3 = (idx - ph) % 4 == 2
        on24 = (idx - ph) % 2 == 1
        nb = min(len(nov), len(bt))
        phase_scores[ph] = {
            "snare_backbeat": float(np.mean(snare_at[on24]) / (np.mean(snare_at[~on24]) + 1e-9)),
            "kick_1_3": float(np.mean(kick_at[on1 | on3]) / (np.mean(kick_at[~(on1 | on3)]) + 1e-9)),
            "chord_change_on_1": float(np.mean(nov[:nb][on1[:nb]]) / (np.mean(nov[:nb]) + 1e-9)),
        }
    if a.downbeat is not None:
        first = int(np.argmin(np.abs(bt - a.downbeat))) % 4
        why = "given"
    else:
        score = {ph: v["snare_backbeat"] + v["kick_1_3"] + v["chord_change_on_1"] for ph, v in phase_scores.items()}
        first = max(score, key=score.get)
        why = "snare on 2/4 + kick on 1/3 + chord change on 1"
    res["bar_grid"] = {"downbeat_phase": first, "chosen_by": why,
                       "phase_scores": {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in phase_scores.items()},
                       "first_downbeat_s": round(float(bt[first]), 3)}
    bars = bt[first::4]
    res["bar_grid"]["n_bars"] = int(len(bars))

    # -- key / tuning (global and per 8 bars) ---------------------------------------------------
    gk, gr, gtop = key_of(np.mean(chroma, axis=1))
    res["key"] = {"global": gk, "corr": round(gr, 3), "top3": gtop,
                  "tuning_cents": round(tuning * 100, 1),
                  "a4_hz": round(440 * 2 ** (tuning / 12), 2)}
    per = []
    fr_bars = librosa.time_to_frames(bars, sr=SR_A, hop_length=HOP)
    for i in range(0, len(bars) - 1, 8):
        f0, f1 = fr_bars[i], fr_bars[min(i + 8, len(bars) - 1)]
        if f1 - f0 < 10:
            continue
        k, r, top = key_of(np.mean(chroma[:, f0:f1], axis=1))
        per.append({"bar": i + 1, "t": round(float(bars[i]), 1), "key": k, "corr": round(r, 2), "top3": top})
    res["key"]["per_8_bars"] = per

    # -- energy per N bars --------------------------------------------------------------------
    blocks = []
    meter_bands = {"low": (30, 150), "mid": (150, 2000), "high": (5000, 16000)}
    for i in range(0, len(bars) - 1, a.bars):
        t0, t1 = bars[i], bars[min(i + a.bars, len(bars) - 1)]
        seg = x48[:, int(t0 * config.SAMPLE_RATE):int(t1 * config.SAMPLE_RATE)]
        if seg.shape[1] < config.SAMPLE_RATE:
            continue
        bl = analyze.band_levels(seg, meter_bands)
        rms = np.sqrt(np.mean(seg ** 2, axis=0))
        blocks.append({"bar": i + 1, "t": round(float(t0), 1), "lufs": round(lufs(seg), 1),
                       **{f"{k}_db": round(v, 1) for k, v in bl.items()},
                       "crest_db": round(float(20 * np.log10(np.abs(seg).max() / (np.sqrt(np.mean(seg ** 2)) + 1e-12))), 1),
                       "corr": round(float(np.corrcoef(seg[0], seg[1])[0, 1]), 2)})
    res["energy_blocks"] = blocks

    # -- structure: beat-synchronous chroma + MFCC -------------------------------------------
    C = librosa.amplitude_to_db(np.abs(librosa.cqt(y=y, sr=SR_A, hop_length=HOP, bins_per_octave=36,
                                                   n_bins=7 * 36)), ref=np.max)
    Csync = librosa.util.sync(C, beats, aggregate=np.median)
    mfcc = librosa.feature.mfcc(y=y, sr=SR_A, hop_length=HOP, n_mfcc=20)
    Msync = librosa.util.sync(mfcc, beats)
    labels, R = laplacian_segments(Csync, Msync, a.k)
    labels = labels[: len(bt)]
    # label per bar = majority over its 4 beats; then runs of equal labels -> sections
    bar_lab = []
    for i in range(len(bars)):
        j = first + 4 * i
        seg = labels[j:j + 4]
        bar_lab.append(int(np.bincount(seg).argmax()) if len(seg) else -1)
    letters = {}
    secs = []
    for i, l in enumerate(bar_lab):
        if l not in letters:
            letters[l] = "ABCDEFGHIJ"[len(letters)]
        if not secs or secs[-1]["label"] != letters[l]:
            secs.append({"label": letters[l], "bar": i + 1, "t": round(float(bars[i]), 1), "bars": 0})
        secs[-1]["bars"] += 1
    res["structure"] = {"sections": secs, "bar_labels": "".join(letters[l] for l in bar_lab)}
    feats = np.vstack([librosa.util.normalize(csync, axis=0), librosa.util.normalize(Msync[:, :csync.shape[1]], axis=1)])
    bounds = librosa.segment.agglomerative(feats, k=12)
    res["structure"]["agglomerative_boundaries_s"] = [round(float(bt[min(b, len(bt) - 1)]), 1) for b in bounds]

    out.parent.mkdir(parents=True, exist_ok=True)
    (out.parent / (out.name + ".measure.json")).write_text(json.dumps(res, indent=1))

    # -- dashboard ----------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(5, 1, figsize=(14, 18), constrained_layout=True)
    fig.suptitle(f"{src.name}: {res['tempo']['median_bpm']} BPM, {gk}, {st['integrated_lufs']} LUFS, "
                 f"PLR {st['plr_db']} dB")
    ax[0].semilogx([float(f) for f in st["third_octave_rel_mid_db"]], list(st["third_octave_rel_mid_db"].values()), "-o", ms=3)
    ax[0].set_xlim(20, 20000); ax[0].grid(True, which="both", alpha=.3); ax[0].set_title("Tonal balance (rel. mid 400-1500 Hz)")
    centers = np.linspace(0.005, 0.995, 100)
    for name in ("hats", "full"):
        h = np.array(sw[name]["hist"])
        ax[1].plot(centers, h / (h.max() + 1e-9), label=name)
    for q in (0.25, 0.5, 0.75):
        ax[1].axvline(q, color="k", alpha=.3, ls="--")
    ax[1].legend(); ax[1].set_title("Onset phase inside the beat (straight 16ths at dashed lines)")
    tb = [b["t"] for b in blocks]
    ax[2].step(tb, [b["lufs"] for b in blocks], where="post", label="LUFS")
    for k in ("low_db", "mid_db", "high_db"):
        vals = np.array([b[k] for b in blocks])
        ax[2].step(tb, vals - vals.max() + max(b["lufs"] for b in blocks), where="post", alpha=.6, label=k)
    for s in secs:
        ax[2].axvline(s["t"], color="c", alpha=.4)
        ax[2].text(s["t"], max(b["lufs"] for b in blocks) + 0.5, s["label"], fontsize=9)
    ax[2].legend(fontsize=8); ax[2].grid(alpha=.3); ax[2].set_title(f"Energy per {a.bars} bars + sections")
    ax[3].imshow(csync, aspect="auto", origin="lower", cmap="magma",
                 extent=[bt[0], bt[min(len(bt) - 1, csync.shape[1] - 1)], -0.5, 11.5])
    ax[3].set_yticks(range(12), NOTES); ax[3].set_title("Beat-synchronous chroma")
    for pk in per:
        ax[3].text(pk["t"], 11.6, pk["key"].replace(" major", "").replace(" minor", "m"), fontsize=7, color="k")
    ax[4].imshow(R, cmap="gray_r", origin="lower"); ax[4].set_title("Recurrence (beats)")
    fig.savefig(out.parent / (out.name + ".measure.png"), dpi=80)
    print(json.dumps({k: v for k, v in res.items() if k not in ("energy_blocks",)}, indent=1)[:6000])
    print("energy per", a.bars, "bars:")
    for b in blocks:
        print(f"  bar {b['bar']:3d} {b['t']:6.1f}s  {b['lufs']:6.1f} LUFS  low {b['low_db']:6.1f} mid {b['mid_db']:6.1f} high {b['high_db']:6.1f}  crest {b['crest_db']}")


if __name__ == "__main__":
    main()
