"""CLI.

  python -m songwriter build songs/<name> [--only drums,bass] [--no-cache]
  python -m songwriter instruments [filter]
  python -m songwriter surge-patches [filter]
  python -m songwriter analyze file.wav
  python -m songwriter compare mine.wav reference.mp3
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from . import analyze, config, instruments, mix, render


def load_song(song_dir: Path):
    spec = importlib.util.spec_from_file_location("song_module", song_dir / "song.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.compose()


def read_audio(path: Path) -> np.ndarray:
    """Any format ffmpeg reads -> (2, N) float32 at SAMPLE_RATE."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2",
                          "-ar", str(config.SAMPLE_RATE), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()


def export(x: np.ndarray, out: Path, stem: str = "master"):
    wav = out / f"{stem}.wav"
    sf.write(wav, x.T, config.SAMPLE_RATE, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-codec:a", "libmp3lame",
                    "-b:a", "320k", str(out / f"{stem}.mp3")], check=True)
    return wav


def cmd_build(a):
    song_dir = Path(a.song_dir)
    out = song_dir / "out"
    t0 = time.time()
    song = load_song(song_dir)
    print(f"[{song.title}] {song.bpm} BPM, {len(song.tracks)} tracks, "
          f"{song.seconds(song.end_beat):.1f}s")
    (out / "midi").mkdir(parents=True, exist_ok=True)
    song.full_midi().save(out / "midi" / "song.mid")
    for name, t in song.tracks.items():
        song.track_midi(t).save(out / "midi" / f"{name}.mid")
    print("render:")
    stems = render.render_stems(song, out / "stems", only=a.only.split(",") if a.only else None,
                                cache=not a.no_cache)
    print("mix:")
    pre, processed = mix.mix(song, stems)
    sf.write(out / "mix_premaster.wav", pre.T, config.SAMPLE_RATE, subtype="FLOAT")
    print("master:")
    final, mstats = mix.master(pre, song.mix.get("master", {}))
    export(final, out)
    rep = analyze.write_report(out, final, processed, song, {"master_chain": mstats})
    print("analysis:")
    print(json.dumps(rep["master"], indent=2))
    for line in rep["masking"]:
        print("  masking:", line)
    for line in rep["warnings"]:
        print("  WARNING:", line)
    print(f"done in {time.time() - t0:.0f}s -> {out}/master.mp3, report.png")


def cmd_instruments(a):
    for i in instruments.catalog():
        if a.filter and a.filter not in i.id:
            continue
        flag = " " if i.available else "!"
        print(f"{flag} {i.id:<26} {i.engine:<6} {i.desc}")


def cmd_surge_patches(a):
    for base in ("patches_factory", "patches_3rdparty"):
        for p in sorted((config.SURGE_DATA_DIR / base).rglob("*.fxp")):
            rel = p.relative_to(config.SURGE_DATA_DIR / base).with_suffix("")
            if not a.filter or a.filter.lower() in str(rel).lower():
                print(rel)


def cmd_analyze(a):
    x = read_audio(Path(a.file))
    print(json.dumps(analyze.stats(x), indent=2))
    png = Path(a.file).with_suffix(".analysis.png")
    analyze.dashboard(x, png, title=Path(a.file).name)
    print("->", png)


def cmd_compare(a):
    x, r = read_audio(Path(a.mine)), read_audio(Path(a.reference))
    sx, sr_ = analyze.stats(x), analyze.stats(r)
    print(f"{'metric':<26}{'mine':>12}{'reference':>12}")
    for k, v in sx.items():
        if k == "bands_db":
            continue
        print(f"{k:<26}{str(v):>12}{str(sr_[k]):>12}")
    # tonal difference after loudness alignment
    bx, br = sx["bands_db"], sr_["bands_db"]
    ox, orf = np.mean(list(bx.values())), np.mean(list(br.values()))
    print("band balance (mine - ref, loudness aligned):")
    for b in bx:
        print(f"  {b:<10}{(bx[b] - ox) - (br[b] - orf):+6.1f} dB")
    png = Path(a.mine).with_suffix(".compare.png")
    analyze.dashboard(x, png, title=f"{Path(a.mine).name} vs {Path(a.reference).name}", reference=r)
    print("->", png)


def main(argv=None):
    p = argparse.ArgumentParser(prog="songwriter")
    sub = p.add_subparsers(required=True)
    b = sub.add_parser("build"); b.add_argument("song_dir"); b.add_argument("--only")
    b.add_argument("--no-cache", action="store_true"); b.set_defaults(fn=cmd_build)
    i = sub.add_parser("instruments"); i.add_argument("filter", nargs="?"); i.set_defaults(fn=cmd_instruments)
    s = sub.add_parser("surge-patches"); s.add_argument("filter", nargs="?"); s.set_defaults(fn=cmd_surge_patches)
    an = sub.add_parser("analyze"); an.add_argument("file"); an.set_defaults(fn=cmd_analyze)
    c = sub.add_parser("compare"); c.add_argument("mine"); c.add_argument("reference"); c.set_defaults(fn=cmd_compare)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
