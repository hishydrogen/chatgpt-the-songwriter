#!/usr/bin/env python3
"""Export and verify the approved final master, tags, cover and delivery hashes.

Run after art/make_art.py and export_delivery.py. No musical content is changed.
"""
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
from PIL import Image
import soundfile as sf
from mutagen.id3 import APIC, COMM, ID3, TALB, TBPM, TCOM, TDRC, TIT2, TPE1, TPE2, TCON, USLT
from mutagen.mp4 import MP4

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TITLE = "Swing, Milk! (feat. Milk)"
ARTIST = "Claude the Songwriter"
ALBUM = TITLE + " - Single"


def decode_hash(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return hashlib.sha256(raw).hexdigest()


def main():
    cover = HERE / "art" / "cover.jpg"
    assert Image.open(cover).size == (3000, 3000)
    lyrics = (HERE / "LYRICS.txt").read_text()
    credits = (HERE / "CREDITS.md").read_text()
    master = HERE / "out" / "master.wav"
    info = sf.info(master)
    assert info.samplerate == 48000 and info.channels == 2 and info.subtype == "PCM_24"
    master_hash = hashlib.sha256(master.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "release.py"), str(HERE),
                    "--title", TITLE, "--artist", ARTIST, "--album", ALBUM,
                    "--composer", "Codex", "--genre", "Jazz", "--year", "2026", "--bpm", "124",
                    "--comment", credits, "--lyrics", lyrics, "--cover", str(cover)], check=True)
    assert hashlib.sha256(master.read_bytes()).hexdigest() == master_hash

    mp3 = HERE / "out" / "master.mp3"
    original_mp3_pcm = decode_hash(mp3)
    tags = ID3(mp3)
    for frame in [TIT2(encoding=3, text=TITLE), TPE1(encoding=3, text=ARTIST),
                  TPE2(encoding=3, text=ARTIST), TALB(encoding=3, text=ALBUM),
                  TCON(encoding=3, text="Jazz"), TDRC(encoding=3, text="2026"),
                  TCOM(encoding=3, text="Codex"), TBPM(encoding=3, text="124")]:
        tags.add(frame)
    for frame_id in ["COMM", "USLT", "APIC"]:
        tags.delall(frame_id)
    tags.add(COMM(encoding=3, lang="eng", desc="Credits", text=credits))
    tags.add(USLT(encoding=3, lang="eng", desc="Scat syllables", text=lyrics))
    tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover.read_bytes()))
    tags.save(mp3, v2_version=3)
    assert decode_hash(mp3) == original_mp3_pcm, "MP3 audio changed during tagging"
    assert ID3(mp3).getall("APIC")[0].data == cover.read_bytes()

    checks = []
    for suffix, rate, bits in [("", 48000, 24), ("_16bit", 44100, 16)]:
        path = HERE / "release" / (TITLE + suffix + ".m4a")
        f = MP4(path)
        assert (f.info.sample_rate, f.info.bits_per_sample, f.info.channels) == (rate, bits, 2)
        assert f.tags["\xa9nam"] == [TITLE] and f.tags["\xa9ART"] == [ARTIST]
        assert f.tags["\xa9wrt"] == ["Codex"] and f.tags["tmpo"] == [124]
        assert f.tags["\xa9lyr"] == [lyrics] and f.tags["\xa9cmt"] == [credits]
        assert bytes(f.tags["covr"][0]) == cover.read_bytes()
        assert Image.open(io.BytesIO(f.tags["covr"][0])).size == (3000, 3000)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0",
                              "-f", "s32le", "-"], capture_output=True, check=True).stdout
        pcm = np.frombuffer(raw, dtype="<i4").reshape(-1, 2)
        assert abs(len(pcm) / rate - info.duration) <= 1 / rate
        sample_peak = float(np.max(np.abs(pcm.astype(np.int64))) / 2**31)
        assert sample_peak < 1
        meter = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-map", "0:a:0",
                                "-af", "ebur128=peak=true", "-f", "null", "-"],
                               capture_output=True, text=True, check=True).stderr
        summary = meter.rsplit("Summary:", 1)[-1]
        loudness = float(re.search(r"I:\s+([-\d.]+) LUFS", summary).group(1))
        peak = float(re.search(r"Peak:\s+([-\d.]+) dBFS", summary).group(1))
        assert -14.3 <= loudness <= -13.7 and peak <= -.8
        checks.append({"file": str(path.relative_to(HERE)), "sample_rate_hz": rate,
                       "bits": bits, "channels": 2, "decoded_frames": len(pcm),
                       "duration_seconds": len(pcm) / rate, "sample_peak": sample_peak,
                       "integrated_lufs": loudness, "true_peak_dbtp": peak,
                       "tags_and_cover_verified": True,
                       "bit_exact_to_24bit_master": True if bits == 24 else None,
                       "conversion": "ALAC, original PCM" if bits == 24 else
                                     "SoX rate -v -s; noise-shaped dither -s; ALAC"})
        print(path.name, f"{path.stat().st_size / 2**20:.2f} MiB", loudness, "LUFS", peak, "dBTP")

    delivery = [mp3, cover, HERE / "out" / "swing-milk-midi.zip", HERE / "out" / "midi" / "song.mid",
                HERE / "CREDITS.md", HERE / "LYRICS.txt", HERE / "song.py",
                *sorted((HERE / "release").glob("*.m4a"))]
    manifest = {"title": TITLE, "artist": ARTIST, "composer": "Codex", "bpm": 124,
                "status": "Final master; noncommercial sharing",
                "approved_arrangement_commit": "a965d1b70f0b55f60b6736f9132d2bc2ba8eee6d",
                "commercial_use": "Milk voicebank requires individual author approval (Xepheris).",
                "master_wav_sha256": master_hash, "mp3_pcm_preserved": True,
                "cover": {"width": 3000, "height": 3000, "original_vector_design": True},
                "audio_checks": checks,
                "files": [{"path": str(p.relative_to(HERE)), "bytes": p.stat().st_size,
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in delivery]}
    (HERE / "release" / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("Final audio, metadata, cover and checksums verified.")


if __name__ == "__main__":
    main()
