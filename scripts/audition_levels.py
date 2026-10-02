#!/usr/bin/env python3
"""Loudness check for audition files, from out/report.json "sections" (written by build).

  python scripts/audition_levels.py songs/<slug> [--tol 1.0]

Candidates are the tracks named like the segment marker (or "<marker> | part"). Within a
category (the marker text before ":", e.g. "piano A" -> "piano") they should sit within
+/- tol dB of each other.
"""
import argparse
import json
from pathlib import Path

import numpy as np


def db_sum(levels):
    return 10 * np.log10(sum(10 ** (v / 10) for v in levels)) if levels else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("song_dir")
    p.add_argument("--tol", type=float, default=1.0)
    a = p.parse_args()
    rep = json.loads((Path(a.song_dir) / "out" / "report.json").read_text())
    rows = []
    for sec in rep["sections"]:
        label = sec["label"]
        cand = [v for n, v in sec["tracks"].items() if n == label or n.startswith(label + " |")]
        rows.append((label, db_sum(cand), sec["master_lufs"]))
    cats = {}
    for r in rows:
        cats.setdefault(r[0].split(":")[0].split(" ")[0], []).append(r)
    ok = True
    for items in cats.values():
        vals = [lv for _, lv, _ in items if lv is not None]
        ref = float(np.median(vals)) if vals else None
        mref = float(np.median([m for *_, m in items]))
        for label, lv, m in items:
            dev = None if lv is None or ref is None else lv - ref
            flag = "" if dev is None or abs(dev) <= a.tol else "  <-- off"
            ok &= not flag
            cand = "      -       " if lv is None else f"{lv:6.1f} ({dev:+.1f})"
            print(f"{label:<46} candidate {cand}   master {m:6.1f} ({m - mref:+.1f}){flag}")
    print(f"all candidates within +/-{a.tol} dB" if ok else f"NOT all within +/-{a.tol} dB")


if __name__ == "__main__":
    main()
