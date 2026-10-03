"""Build and verify the full checkpoint-3 rough mix.

Run: python songs/low-tide/build.py
Optional: --validate-only checks the existing outputs without rendering again.
"""
import argparse
import io
import json
from pathlib import Path
import sys

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from songwriter.__main__ import main, read_audio, load_song  # noqa: E402
from songwriter.render import song_length_samples  # noqa: E402
from songwriter import analyze  # noqa: E402
from songwriter.mix import true_peak_db  # noqa: E402

HERE = Path(__file__).resolve().parent


def validate():
    report = json.loads((HERE / "out/report.json").read_text())
    song = load_song(HERE)
    assert len(song.tracks) == 9 and len(song.markers) == 10
    assert song.end_beat == 296 and not song.tempo_changes
    expected_n = song_length_samples(song)
    raw = {}
    for name, track in song.tracks.items():
        midi = io.BytesIO()
        song.track_midi(track).save(file=midi)
        assert (HERE / "out/midi" / f"{name}.mid").read_bytes() == midi.getvalue(), name
        stem_path = HERE / "out/stems" / f"{name}.wav"
        assert sf.info(stem_path).subtype == "FLOAT", name
        signature = (HERE / "out/stems" / f".{name}.sig").read_text()
        assert signature.startswith(f"{track.instrument}|{expected_n}|float32|"), name
        audio, sr = sf.read(stem_path, dtype="float32", always_2d=True)
        assert sr == 48000 and len(audio) == expected_n and np.isfinite(audio).all(), name
        assert np.max(np.abs(audio)) > 1e-4, name
        plateau = ((np.abs(audio[1:-1]) >= .9999)
                   & (np.abs(audio[:-2] - audio[1:-1]) < 1e-8)
                   & (np.abs(audio[2:] - audio[1:-1]) < 1e-8))
        count = int(np.count_nonzero(plateau))
        assert count == 0, (name, "full-scale flat tops", count)
        raw[name] = {"full_scale_plateau_samples": count,
                     "sample_peak_dbfs": round(float(20 * np.log10(np.max(np.abs(audio)) + 1e-12)), 3)}
    path = HERE / "out/master.wav"
    assert sf.info(path).subtype == "PCM_24"
    wav, sr = sf.read(path, dtype="float32", always_2d=True)
    assert sr == 48000 and wav.shape == (expected_n, 2)
    assert np.isfinite(wav).all() and np.max(np.abs(wav)) < 1
    duration = len(wav) / sr
    assert 207 < duration < 212, duration
    wav_peak = true_peak_db(wav.T)
    assert wav_peak <= -1.29, wav_peak
    master = report["master"]
    assert abs(master["integrated_lufs"] + 14) < .15, master
    assert master["plr_db"] >= 12 and master["stereo_correlation"] >= .3, master
    mp3 = read_audio(HERE / "out/master.mp3")
    assert mp3.shape == wav.T.shape and np.isfinite(mp3).all() and np.max(np.abs(mp3)) < 1
    mp3_stats = analyze.stats(mp3)
    assert mp3_stats["true_peak_dbtp"] <= -1.0, mp3_stats
    assert abs(mp3_stats["integrated_lufs"] + 14) < .2, mp3_stats
    result = {"checkpoint": 3, "palette_choice": "BBBB", "groove_choice": "A throughout",
              "bars": 74, "duration_s": round(duration, 3), "source_midi_exports_current": True,
              "wav_true_peak_dbtp": round(wav_peak, 3), "master": master,
              "decoded_mp3": mp3_stats, "raw_stems": raw,
              "sections": report["sections"], "warnings": report["warnings"],
              "pending": {"title": "Low Tide (working title)", "ending": "full stop (provisional)"}}
    (HERE / "out/validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("raw_stems", "sections")}, indent=2), flush=True)
    print("Full form, current MIDI/float stems, WAV/MP3 peaks, dynamics and mono checks passed.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if not args.validate_only:
        main(["build", str(HERE)])
    validate()
