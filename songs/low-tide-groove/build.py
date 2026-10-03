"""Render, match whole-groove loudness, and validate WAV/MP3 plus raw stems.

Run: python songs/low-tide-groove/build.py
"""
import io
import json
from pathlib import Path
import sys

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from songwriter.__main__ import main, read_audio, load_song  # noqa: E402
from songwriter import analyze  # noqa: E402

HERE = Path(__file__).resolve().parent
TRIMS = HERE / "loudness_trims.json"


def validate():
    report = json.loads((HERE / "out/report.json").read_text())
    levels = [row["master_lufs"] for row in report["sections"]]
    assert len(levels) == 3 and max(levels) - min(levels) <= .6, levels
    master = report["master"]
    assert abs(master["integrated_lufs"] + 14) < .15, master
    assert master["true_peak_dbtp"] <= -1.3, master
    assert master["plr_db"] >= 12, master
    assert master["stereo_correlation"] >= .3, master
    song = load_song(HERE)
    assert len(song.markers) == 3 and len(song.tracks) == 21
    raw = {}
    for name, track in song.tracks.items():
        expected_midi = io.BytesIO()
        song.track_midi(track).save(file=expected_midi)
        assert (HERE / "out/midi" / f"{name}.mid").read_bytes() == expected_midi.getvalue(), \
            f"Source changed since render: {name}"
        audio, sr = sf.read(HERE / "out/stems" / f"{name}.wav", dtype="float32", always_2d=True)
        assert sr == 48000 and np.isfinite(audio).all(), name
        # Detect exact, repeated full-scale plateaus, including clipping baked into
        # the sample-rendering stage. Peaks above 1 in a float stem alone are legal.
        plateau = ((np.abs(audio[1:-1]) >= .9999)
                   & (np.abs(audio[:-2] - audio[1:-1]) < 1e-8)
                   & (np.abs(audio[2:] - audio[1:-1]) < 1e-8))
        count = int(np.count_nonzero(plateau))
        assert count == 0, (name, "full-scale flat tops", count)
        raw[name] = {"sample_peak_dbfs": round(float(20 * np.log10(np.max(np.abs(audio)) + 1e-12)), 3),
                     "full_scale_plateau_samples": count}
    wav, sr = sf.read(HERE / "out/master.wav", dtype="float32", always_2d=True)
    assert sr == 48000 and np.isfinite(wav).all() and np.max(np.abs(wav)) < 1
    mp3 = read_audio(HERE / "out/master.mp3")
    assert np.isfinite(mp3).all() and np.max(np.abs(mp3)) < 1
    mp3_stats = analyze.stats(mp3)
    assert mp3_stats["true_peak_dbtp"] <= -1.0, mp3_stats
    assert abs(mp3_stats["integrated_lufs"] + 14) < .2, mp3_stats
    result = {
        "palette_choice": "BBBB", "bars_per_version": 8, "source_midi_exports_current": True,
        "duration_s": round(len(wav) / sr, 3),
        "sections": [{"label": row["label"], "master_lufs": row["master_lufs"]}
                     for row in report["sections"]],
        "whole_groove_loudness_spread_db": round(max(levels) - min(levels), 2),
        "master": master, "decoded_mp3": mp3_stats,
        "raw_stems": raw, "warnings": report["warnings"],
    }
    (HERE / "out/validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "raw_stems"}, indent=2), flush=True)
    print("Eight-bar grooves, raw stems, loudness, WAV/MP3 peaks and mono checks passed.", flush=True)


def build():
    for attempt in range(3):
        print(f"\nGroove render / loudness match pass {attempt + 1}", flush=True)
        main(["build", str(HERE)])
        report = json.loads((HERE / "out/report.json").read_text())
        rows = report["sections"]
        target = float(np.median([r["master_lufs"] for r in rows]))
        trims = json.loads(TRIMS.read_text()) if TRIMS.exists() else {}
        changes = {}
        for row in rows:
            difference = row["master_lufs"] - target
            print(f"  {row['label']}: {row['master_lufs']:.2f} LUFS ({difference:+.2f} dB)", flush=True)
            if abs(difference) > .3:
                changes[row["label"]] = round(trims.get(row["label"], 0) - difference, 2)
        if not changes:
            break
        if attempt == 2:
            raise RuntimeError("Whole-groove loudness matching did not converge")
        trims.update(changes)
        TRIMS.write_text(json.dumps(trims, indent=2) + "\n")
    validate()


if __name__ == "__main__":
    build()
