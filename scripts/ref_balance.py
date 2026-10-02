#!/usr/bin/env python3
"""Tonal balance against a reference, both relative to the mid band (400-1500 Hz).

  python scripts/ref_balance.py songs/<slug>/out/master.wav refs/<ref>.measure.json

Prints band and third-octave differences (mine - reference) after aligning the mids,
plus loudness, PLR and stereo correlation side by side. A positive number means the mix
has more of that band than the reference.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from songwriter import analyze  # noqa: E402
from songwriter.__main__ import read_audio  # noqa: E402


def main():
    mine, ref_json = Path(sys.argv[1]), Path(sys.argv[2])
    ref = json.loads(ref_json.read_text())["loudness"]
    x = read_audio(mine)
    st = analyze.stats(x)
    b = st["bands_db"]
    rel = {k: v - b["mid"] for k, v in b.items()}
    print(f"{'band':<10}{'mine':>8}{'ref':>8}{'diff':>8}")
    for k in rel:
        print(f"{k:<10}{rel[k]:8.1f}{ref['bands_rel_mid_db'][k]:8.1f}{rel[k] - ref['bands_rel_mid_db'][k]:+8.1f}")
    fc, lv = analyze.third_octave(x)
    mid = np.mean([l for f, l in zip(fc, lv) if 400 <= f < 1500])
    print("third-octave diff (mine - ref):")
    row = []
    for f, l in zip(fc, lv):
        r = ref["third_octave_rel_mid_db"].get(str(f))
        if r is not None and 25 <= f <= 16000:
            row.append(f"{f:>7.0f}:{(l - mid) - r:+5.1f}")
    for i in range(0, len(row), 6):
        print("  " + "  ".join(row[i:i + 6]))
    for k in ("integrated_lufs", "true_peak_dbtp", "plr_db", "loudness_range_lu", "stereo_correlation", "side_to_mid_db"):
        print(f"{k:<22}{st[k]:>10}{ref[k]:>10}")


if __name__ == "__main__":
    main()
