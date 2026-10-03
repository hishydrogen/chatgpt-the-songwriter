"""Render checkpoint 1 and measure/match candidate loudness after channel effects.

Run from the repository: python songs/low-tide-palette/build.py
The standard CLI and scripts/audition_levels.py remain usable.
"""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from songwriter.__main__ import main, load_song, read_audio  # noqa: E402
from songwriter import analyze  # noqa: E402

HERE = Path(__file__).resolve().parent
TRIMS = HERE / "loudness_trims.json"


def measure():
    report = json.loads((HERE / "out/report.json").read_text())
    groups = {}
    for row in report["sections"]:
        label = row["label"]
        parts = [v for n, v in row["tracks"].items() if n == label or n.startswith(label + " |")]
        assert parts and all(np.isfinite(v) for v in parts) and max(parts) > -70, \
            f"Silent or missing audition candidate: {label}"
        level = float(10 * np.log10(sum(10 ** (v / 10) for v in parts)))
        groups.setdefault(label.split()[0], []).append((label, level, row["master_lufs"]))
    return report, groups


def validate_exports():
    song = load_song(HERE)
    phrases = {}
    for beat, label in song.markers:
        parts = {}
        for name, track in song.tracks.items():
            if name == label or name.startswith(label + " |"):
                voice = name[len(label):]
                parts[voice] = [(n.pitch, round(n.start - beat, 7), round(n.dur, 7), n.vel)
                                for n in track.notes]
        assert parts, label
        phrases.setdefault(label.split()[0], []).append(parts)
    for category, candidates in phrases.items():
        assert all(candidate == candidates[0] for candidate in candidates), category
    audio = read_audio(HERE / "out/master.mp3")
    assert np.isfinite(audio).all() and np.max(np.abs(audio)) < 1
    stats = analyze.stats(audio)
    assert stats["true_peak_dbtp"] < 0, stats
    result = {"identical_candidate_note_phrases": True,
              "mp3_decoded_duration_s": round(audio.shape[1] / 48000, 3), "mp3_stats": stats}
    (HERE / "out/export-validation.json").write_text(json.dumps(result, indent=2) + "\n")


def build():
    for attempt in range(3):
        print(f"\nCheckpoint render / loudness match pass {attempt + 1}", flush=True)
        main(["build", str(HERE)])
        report, groups = measure()
        trims = json.loads(TRIMS.read_text()) if TRIMS.exists() else {}
        changes = {}
        for rows in groups.values():
            target = float(np.median([v for _, v, _ in rows]))
            for label, level, _ in rows:
                dev = level - target
                print(f"  {label}: {level:.2f} LUFS, group difference {dev:+.2f} dB", flush=True)
                if abs(dev) > .45:
                    changes[label] = round(trims.get(label, 0) - dev, 2)
        if not changes:
            break
        if attempt == 2:
            raise RuntimeError("Audition matching did not converge; inspect report.json")
        trims.update(changes)
        TRIMS.write_text(json.dumps(trims, indent=2) + "\n")
    # Fail on a substantive problem; this complements the existing reporting helper,
    # which does not signal an out-of-tolerance result with a nonzero exit status.
    for rows in groups.values():
        levels = [v for _, v, _ in rows]
        assert max(levels) - min(levels) <= 1.0, rows
        masters = [v for _, _, v in rows]
        assert max(masters) - min(masters) <= 1.0, rows
    master = report["master"]
    assert abs(master["integrated_lufs"] + 14) < .15, master
    assert master["true_peak_dbtp"] <= -1.0, master
    assert master["plr_db"] >= 12, master
    assert master["stereo_correlation"] >= .3, master
    subprocess.run([sys.executable, str(ROOT / "scripts/audition_levels.py"), str(HERE)], check=True)
    matched = {group: [{"label": label, "candidate_lufs": round(level, 2), "master_lufs": m}
                       for label, level, m in rows] for group, rows in groups.items()}
    (HERE / "out/audition-validation.json").write_text(
        json.dumps({"groups": matched, "master": master, "warnings": report["warnings"]}, indent=2) + "\n")
    validate_exports()
    print("Candidate phrases, loudness matching, exports, peaks and mono compatibility passed.", flush=True)


if __name__ == "__main__":
    build()
