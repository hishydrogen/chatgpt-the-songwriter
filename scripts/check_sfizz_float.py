#!/usr/bin/env python3
"""Functional check: SFZ rendering preserves precision and floating-point headroom.

Uses a temporary, layered sine fixture; no instrument library download is needed.
Run from the repository with the studio environment activated.
"""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from songwriter.instruments import Instrument, register  # noqa: E402
from songwriter.render import render_track  # noqa: E402
from songwriter.song import Song  # noqa: E402


def main():
    with TemporaryDirectory(prefix="sfizz-float-check-") as temp:
        folder = Path(temp)
        sr = 48000
        tone = (.8 * np.sin(2 * np.pi * 1000 * np.arange(12000) / sr)).astype(np.float32)
        sf.write(folder / "tone.wav", tone, sr, subtype="FLOAT")
        source = ("<group> key=60 volume=6 amp_veltrack=0 loop_mode=loop_continuous "
                  "loop_start=0 loop_end=11999 ampeg_attack=0.001 ampeg_release=0.03\n")
        (folder / "tone.sfz").write_text(source + "<region> sample=tone.wav\n" * 16)
        register(Instrument("test.sfizz-float", "sfz", str(folder / "tone.sfz"), "Renderer fixture"))
        song = Song("Float renderer check", bpm=120)
        track = song.track("tone", "test.sfizz-float").note(60, 0, 1, 127)
        song.length_beats = 2
        audio = render_track(song, track)
        peak = float(np.max(np.abs(audio)))
        assert np.isfinite(audio).all() and peak > 1.1, peak
        assert np.max(np.abs(audio * 32768 - np.rint(audio * 32768))) > .01
        print(f"Float SFZ output verified: peak {peak:.6f} is preserved; sub-16-bit precision survives.")


if __name__ == "__main__":
    main()
