"""Check the rendered comparison, rather than just the composition instructions."""
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyworld as pw
from scipy import signal
import soundfile as sf

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("groove_audio_score", HERE / "song.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
song = score.compose()
out = HERE / "out"
report = json.loads((out / "report.json").read_text())
master = report["master"]
assert abs(master["integrated_lufs"] + 14) <= .2, master
assert master["true_peak_dbtp"] <= -.95 and master["plr_db"] >= 12, master
assert master["stereo_correlation"] >= .3, master
assert not report["warnings"], report["warnings"]
balances = []
for sec in report["sections"]:
    if not sec["label"].endswith("vocal"):
        continue
    lv = sec["tracks"]
    lead = lv[score.VOICE_LABEL]
    band = max(v for n, v in lv.items() if n != score.VOICE_LABEL and not n.startswith(("fx:", "bus:")))
    assert 4 <= lead - band <= 6.1, (sec["label"], lead, band)
    balances.append({"label": sec["label"], "master_lufs": sec["master_lufs"],
                     "lead_lufs": lead, "loudest_band_track_lufs": band,
                     "lead_margin_db": round(lead - band, 1)})
assert len(balances) == 3
levels = np.array([s["master_lufs"] for s in balances])
assert np.max(np.abs(levels - np.median(levels))) <= 1, "vocal comparisons are not level matched"
band_levels = np.array([s["master_lufs"] for s in report["sections"] if s["label"].endswith("band")])
band_center = (band_levels.max() + band_levels.min()) / 2
assert np.max(np.abs(band_levels - band_center)) <= 1, "instrumental comparisons are not level matched"

def estimate(x, sr):
    x = signal.resample_poly(x, 16000, sr) if sr != 16000 else x
    return pw.harvest(np.ascontiguousarray(x, dtype=np.float64), 16000,
                      f0_floor=180, f0_ceil=750, frame_period=10)

tt = np.arange(32000) / 16000
tone = sum(.1 / k * np.sin(2 * np.pi * 440 * k * tt) for k in (1, 2, 3))
f0, _ = estimate(tone, 16000)
assert abs(np.median(f0[f0 > 0]) - 440) < 3, "measurement calibration failed"
fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True, constrained_layout=True)
pitch = []
vocal_sections = [s for s in song.groove_sections if s["role"] == "vocal"]
for ax, sec in zip(axes, vocal_sections):
    start, end = song.seconds(sec["beat"]), song.seconds(sec["beat"] + 32)
    with sf.SoundFile(out / "stems" / (score.VOICE_LABEL + ".wav")) as f:
        sr = f.samplerate
        f.seek(round(start * sr))
        x = f.read(round((end - start + .3) * sr))
    mono = x.mean(axis=1)
    f0, t = estimate(mono, sr)
    midi = np.full_like(f0, np.nan)
    voiced = f0 > 0
    midi[voiced] = 69 + 12 * np.log2(f0[voiced] / 440)
    ax.plot(t, midi, color="#2354b0", lw=.9)
    errors = []
    for n in song.tracks[score.VOICE_LABEL].notes:
        if not sec["beat"] <= n.start < sec["beat"] + 32:
            continue
        a = song.seconds(n.start) - start
        b = song.seconds(n.start + n.dur) - start
        ax.plot([a, b], [n.pitch, n.pitch], color="#d69300", lw=2, alpha=.75)
        window = (t >= a + .065) & (t <= b - .025) & voiced
        if window.sum() >= 3:
            errors.append(float(np.median(midi[window] - n.pitch) * 100))
    errors = np.abs(errors)
    assert len(errors) == 49 and np.median(errors) < 35 and np.max(errors) < 80, sec["label"]
    jumps = np.abs(np.diff(mono))
    local = np.sqrt(signal.convolve(mono ** 2, np.ones(129) / 129, mode="same"))
    candidates = np.flatnonzero((jumps > 2.5 * local[1:]) & (jumps > .035))
    assert len(candidates) == 0, (sec["label"], "large sample jumps", len(candidates))
    row = {"version": sec["version"], "measured_notes": len(errors),
           "median_absolute_error_cents": round(float(np.median(errors)), 1),
           "p90_absolute_error_cents": round(float(np.percentile(errors, 90)), 1),
           "maximum_absolute_error_cents": round(float(np.max(errors)), 1),
           "large_sample_jumps": len(candidates)}
    pitch.append(row)
    ax.set_ylim(58, 73)
    ax.set_ylabel("MIDI pitch")
    ax.set_title(sec["label"])
    ax.grid(alpha=.2)
    print(row, flush=True)
axes[-1].set_xlabel("Seconds within the eight-bar scat hook")
fig.suptitle("Milk: rendered pitch (blue), MIDI target (gold)")
fig.savefig(out / "vocal-pitch.png", dpi=120)
plt.close(fig)
result = {"status": "passed", "master": master, "vocal_balance": balances,
          "vocal_candidate_level_deviations_lu": [round(float(v), 1) for v in levels - np.median(levels)],
          "band_candidate_level_deviations_lu": [round(float(v), 1) for v in band_levels - band_center],
          "pitch": pitch}
(out / "audio-check.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
