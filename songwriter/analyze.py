"""Objective mix analysis: a technical check for what Claude cannot hear.

Produces numbers (loudness, peaks, dynamics, stereo, tonal balance, masking, per-section
track levels) and a PNG dashboard, so technical problems (clipping, mono collapse, mud,
resonances, masking, a buried lead) show up. Sound choices stay with the listener.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import signal

from . import config
from .mix import lufs, true_peak_db

SR = config.SAMPLE_RATE
BANDS = {  # name: (lo, hi)
    "sub": (20, 60), "bass": (60, 150), "low-mid": (150, 400), "mid": (400, 1500),
    "hi-mid": (1500, 4000), "presence": (4000, 8000), "air": (8000, 18000),
}
THIRD_OCT = [round(1000 * 2 ** (k / 3), 1) for k in range(-17, 14)]  # 20 Hz .. 20 kHz


def _psd(x: np.ndarray):
    mono = x.mean(axis=0) if x.ndim == 2 else x
    f, p = signal.welch(mono, SR, nperseg=8192, scaling="spectrum")
    return f, p


def band_levels(x: np.ndarray, bands=BANDS) -> dict[str, float]:
    f, p = _psd(x)
    out = {}
    for name, (lo, hi) in bands.items():
        m = (f >= lo) & (f < hi)
        out[name] = float(10 * np.log10(p[m].sum() + 1e-20))
    return out


def third_octave(x: np.ndarray) -> tuple[list[float], list[float]]:
    f, p = _psd(x)
    lv = []
    for fc in THIRD_OCT:
        m = (f >= fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6))
        lv.append(float(10 * np.log10(p[m].sum() + 1e-20)))
    return THIRD_OCT, lv


def short_term_lufs(x: np.ndarray, hop_s=0.5, win_s=3.0) -> tuple[np.ndarray, np.ndarray]:
    import pyloudnorm as pyln
    meter = pyln.Meter(SR, block_size=0.4)
    w, h = int(win_s * SR), int(hop_s * SR)
    t, v = [], []
    for s in range(0, max(1, x.shape[1] - w), h):
        seg = x[:, s:s + w]
        try:
            v.append(meter.integrated_loudness(seg.T.astype(np.float64)))
        except ValueError:
            v.append(-70.0)
        t.append((s + w / 2) / SR)
    v = np.array(v)
    v[~np.isfinite(v)] = -70.0
    return np.array(t), v


def stats(x: np.ndarray) -> dict:
    peak = float(20 * np.log10(np.abs(x).max() + 1e-12))
    rms = float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12))
    L, R = x[0], x[1]
    corr = float(np.corrcoef(L, R)[0, 1]) if np.std(L) > 0 and np.std(R) > 0 else 1.0
    mid, side = (L + R) / 2, (L - R) / 2
    side_db = float(20 * np.log10((np.sqrt(np.mean(side ** 2)) + 1e-12) / (np.sqrt(np.mean(mid ** 2)) + 1e-12)))
    _, st = short_term_lufs(x)
    active = st[st > st.max() - 20] if len(st) else st
    integ = lufs(x)
    fc, lv = third_octave(x)
    sel = [(np.log2(f), l) for f, l in zip(fc, lv) if 100 <= f <= 10000]
    slope = float(np.polyfit([a for a, _ in sel], [b for _, b in sel], 1)[0]) if sel else 0.0
    return {
        "integrated_lufs": round(integ, 2),
        "short_term_max_lufs": round(float(st.max()), 2) if len(st) else None,
        "loudness_range_lu": round(float(np.percentile(active, 95) - np.percentile(active, 10)), 2) if len(active) else None,
        "true_peak_dbtp": round(true_peak_db(x), 2),
        "sample_peak_db": round(peak, 2),
        "plr_db": round(true_peak_db(x) - integ, 2),       # peak-to-loudness ratio
        "crest_db": round(peak - rms, 2),
        "stereo_correlation": round(corr, 3),
        "side_to_mid_db": round(side_db, 2),
        "tonal_slope_db_per_oct": round(slope, 2),          # 1/3-oct band energy, 100 Hz-10 kHz
        "bands_db": {k: round(v, 1) for k, v in band_levels(x).items()},
    }


def masking_report(tracks: dict[str, np.ndarray], top_db: float = 3.0) -> list[str]:
    """Bands where two or more tracks compete within `top_db` of the loudest one."""
    levels = {n: band_levels(x) for n, x in tracks.items() if not n.startswith(("fx:", "bus:"))}
    notes = []
    for b in BANDS:
        ranked = sorted(((lv[b], n) for n, lv in levels.items()), reverse=True)
        if len(ranked) < 2:
            continue
        top = ranked[0][0]
        crowd = [n for v, n in ranked if v >= top - top_db]
        if len(crowd) >= 2:
            notes.append(f"{b}: {', '.join(crowd)} within {top_db:g} dB of each other")
    return notes


def dashboard(x: np.ndarray, out_png: Path, tracks: dict[str, np.ndarray] | None = None,
              title: str = "", markers=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = 4 if tracks else 3
    fig, ax = plt.subplots(rows, 1, figsize=(13, 3.2 * rows), constrained_layout=True)
    fig.suptitle(title)
    # tonal balance
    fc, lv = third_octave(x)
    off = np.mean(lv[10:24])
    ax[0].semilogx(fc, np.array(lv) - off, "-o", ms=3, label="mix")
    ax[0].set_xlim(20, 20000); ax[0].grid(True, which="both", alpha=.3)
    ax[0].set_ylabel("1/3-oct level (dB, rel.)"); ax[0].legend(); ax[0].set_title("Tonal balance")
    # spectrogram
    mono = x.mean(axis=0)
    f, t, S = signal.spectrogram(mono, SR, nperseg=4096, noverlap=3072)
    ax[1].pcolormesh(t, f, 10 * np.log10(S + 1e-14), shading="auto", vmin=-130, vmax=-40, cmap="magma")
    ax[1].set_yscale("symlog", linthresh=200); ax[1].set_ylim(30, 20000); ax[1].set_title("Spectrogram")
    # loudness over time
    tt, st = short_term_lufs(x)
    ax[2].plot(tt, st); ax[2].set_ylim(max(-50, st.min() - 3), st.max() + 3)
    ax[2].set_ylabel("short-term LUFS"); ax[2].grid(alpha=.3); ax[2].set_title("Loudness / arrangement")
    for sec, label in markers or []:
        for a in ax[1:3]:
            a.axvline(sec, color="c", alpha=.5)
        ax[2].text(sec, st.max() + 1, label, fontsize=8)
    # per-track band energy heatmap
    if tracks:
        names = [n for n in tracks if not n.startswith("bus:")]
        levels = [band_levels(tracks[n]) for n in names]   # one PSD per track
        M = np.array([[lv[b] for b in BANDS] for lv in levels])
        im = ax[3].imshow(M, aspect="auto", cmap="viridis", vmin=M.max() - 40, vmax=M.max())
        ax[3].set_yticks(range(len(names)), names); ax[3].set_xticks(range(len(BANDS)), list(BANDS))
        fig.colorbar(im, ax=ax[3], label="dB"); ax[3].set_title("Where each track lives (band energy)")
    fig.savefig(out_png, dpi=90)
    plt.close(fig)


def _corr(x: np.ndarray) -> float:
    if np.std(x[0]) == 0 or np.std(x[1]) == 0:
        return 1.0
    return float(np.corrcoef(x[0], x[1])[0, 1])


def warnings(master_stats: dict, track_info: dict) -> list[str]:
    """Rule-of-thumb checks. Not laws - reasons to listen/look again."""
    w = []
    m = master_stats
    if m["stereo_correlation"] < 0.3:
        w.append(f"master stereo correlation {m['stereo_correlation']} is low: mono playback will thin out")
    if m["true_peak_dbtp"] > -0.95:
        w.append(f"true peak {m['true_peak_dbtp']} dBTP above -1: risk of codec clipping")
    if m["plr_db"] < 8:
        w.append(f"PLR {m['plr_db']} dB: very squashed, consider less limiting")
    b = m["bands_db"]
    if b["low-mid"] - b["mid"] > 9:
        w.append(f"low-mid exceeds mid by {b['low-mid'] - b['mid']:.1f} dB: likely muddy (cut 200-500 Hz on keys/guitars/pads)")
    if b["presence"] < b["mid"] - 18:
        w.append(f"presence is {b['mid'] - b['presence']:.1f} dB under mid: likely dull/dark")
    if b["sub"] > b["bass"] + 3:
        w.append("sub louder than bass band: boomy, check kick/bass below 60 Hz")
    for n, t in track_info.items():
        if t["stereo_correlation"] < 0.1 and not n.startswith("fx:"):
            w.append(f"{n}: stereo correlation {t['stereo_correlation']} - phasey, will collapse in mono "
                     "(reduce width / use mono_below / check unison)")
    return w


def section_levels(master: np.ndarray, tracks: dict, song) -> list[dict]:
    """Per marker section: master LUFS and the LUFS of every track that plays in it
    (after its channel strip). Used to balance sections and to loudness-match auditions."""
    marks = sorted(song.markers)
    if not marks:
        return []
    marks.append((song.end_beat, "end"))
    out = []
    for (b0, label), (b1, _) in zip(marks, marks[1:]):
        s0, s1 = int(song.seconds(b0) * SR), int(song.seconds(b1) * SR)
        if s1 - s0 < SR // 2:
            continue
        lv = {}
        for n, x in tracks.items():
            seg = x[:, s0:s1]
            if np.abs(seg).max() > 1e-5:
                v = lufs(seg)
                if v > -70:
                    lv[n] = round(v, 1)
        out.append({"label": label, "start_s": round(s0 / SR, 2), "end_s": round(s1 / SR, 2),
                    "master_lufs": round(lufs(master[:, s0:s1]), 1), "tracks": lv})
    return out


def write_report(out_dir: Path, master: np.ndarray, tracks: dict, song=None, extra: dict | None = None):
    s = stats(master)
    report = {"master": s, "masking": masking_report(tracks), **(extra or {})}
    if song is not None:
        report["sections"] = section_levels(master, tracks, song)
    report["tracks"] = {n: {"lufs": round(lufs(x), 1),
                            "peak_db": round(float(20 * np.log10(np.abs(x).max() + 1e-12)), 1),
                            "stereo_correlation": round(_corr(x), 2)}
                        for n, x in tracks.items()}
    report["warnings"] = warnings(s, report["tracks"])
    (out_dir / "report.json").write_text(json.dumps(report, indent=2))
    markers = [(song.seconds(b), l) for b, l in song.markers] if song else None
    dashboard(master, out_dir / "report.png", tracks, title=song.title if song else "", markers=markers)
    return report
