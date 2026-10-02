#!/usr/bin/env python3
"""Package a finished song as Apple Lossless with metadata and cover art.

  python scripts/release.py songs/<slug> --title "Mirage" --artist "Claude the Songwriter" \
      --genre "R&B/Soul" --year 2026 --bpm 103 --comment "..." [--cover songs/<slug>/art/cover.jpg]

Writes songs/<slug>/release/<Title>.m4a (24-bit/48 kHz ALAC, bit-exact to out/master.wav,
verified) and <Title>_16bit.m4a (44.1 kHz/16-bit, SoX resampled + dithered; small enough
to send through the app). The 24-bit file is gitignored: `git add -f` it to share via GitHub.
"""
import argparse
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from mutagen.mp4 import MP4, MP4Cover


def tag(path: Path, a, cover: Path | None):
    f = MP4(path)
    if f.tags is None:
        f.add_tags()
    t = f.tags
    t["\xa9nam"] = a.title
    t["\xa9ART"] = a.artist
    t["aART"] = a.album_artist or a.artist
    t["\xa9alb"] = a.album or f"{a.title} - Single"
    t["\xa9gen"] = a.genre
    t["\xa9day"] = str(a.year)
    t["\xa9wrt"] = a.composer or a.artist
    t["trkn"] = [(a.track, a.tracks)]
    t["disk"] = [(1, 1)]
    if a.bpm:
        t["tmpo"] = [int(round(a.bpm))]
    if a.comment:
        t["\xa9cmt"] = a.comment
    t["\xa9lyr"] = a.lyrics
    t["cprt"] = f"℗ {a.year} {a.artist}"
    if cover and cover.exists():
        t["covr"] = [MP4Cover(cover.read_bytes(), imageformat=MP4Cover.FORMAT_JPEG)]
    f.save()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("song_dir")
    p.add_argument("--title", required=True)
    p.add_argument("--artist", default="Claude the Songwriter")
    p.add_argument("--album-artist")
    p.add_argument("--album")
    p.add_argument("--composer")
    p.add_argument("--genre", default="Pop")
    p.add_argument("--year", default=2026, type=int)
    p.add_argument("--bpm", type=float)
    p.add_argument("--track", type=int, default=1)
    p.add_argument("--tracks", type=int, default=1)
    p.add_argument("--comment", default="")
    p.add_argument("--lyrics", default="(Instrumental)")
    p.add_argument("--cover")
    a = p.parse_args()

    d = Path(a.song_dir)
    master = d / "out" / "master.wav"
    rel = d / "release"
    rel.mkdir(exist_ok=True)
    cover = Path(a.cover) if a.cover else d / "art" / "cover.jpg"
    name = a.title.replace("/", "-")

    hi = rel / f"{name}.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-map", "0:a", "-c:a", "alac",
                    "-sample_fmt", "s32p", "-bits_per_raw_sample", "24", str(hi)], check=True)
    tag(hi, a, cover)
    # verify bit-exact against the 24-bit master
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(hi), "-f", "s32le", "-ac", "2", "-"],
                         capture_output=True, check=True).stdout
    dec = np.frombuffer(raw, np.int32).reshape(-1, 2) >> 8
    ref, _ = sf.read(master, dtype="int32")
    assert dec.shape == ref.shape and np.array_equal(dec, ref >> 8), "ALAC is not bit-exact to master.wav"

    tmp = rel / "_16_44.wav"
    subprocess.run(["sox", str(master), "-b", "16", "-r", "44100", str(tmp), "rate", "-v", "-s",
                    "dither", "-s"], check=True)
    lo = rel / f"{name}_16bit.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-c:a", "alac", str(lo)], check=True)
    tmp.unlink()
    tag(lo, a, cover)
    for f in (hi, lo):
        info = MP4(f).info
        print(f"{f}  {info.sample_rate} Hz {info.bits_per_sample}-bit  {f.stat().st_size / 2**20:.1f} MiB")
    print("24-bit ALAC verified bit-exact to out/master.wav")


if __name__ == "__main__":
    main()
