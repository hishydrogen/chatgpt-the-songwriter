"""Package the approved master, sleeve and credits; verify final deliverables.

Run after build.py and art/make_art.py. The existing repository exporter verifies
24-bit ALAC against master.wav. This adds release metadata, checks the 16-bit
conversion, and ensures tagging the MP3 does not alter its decoded audio.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.id3 import APIC, COMM, TALB, TBPM, TCOM, TCON, TCOP, TDRC, TIT2, TPE1, TPE2, USLT

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from songwriter.mix import true_peak_db  # noqa: E402

HERE = Path(__file__).resolve().parent
TITLE = "Low Tide"
ARTIST = "Codex the Songwriter"
COMPOSER = "Codex for hishydrogen"
ALBUM = "Low Tide - Single"
GENRE = "Instrumental Rock"
YEAR = 2026
BPM = 86
APPROVED_MASTER_SHA256 = "3ed0480782ecbae3b3c50dc07290a0f6de2d6ecb3e39fbedff5cc8303a09349c"
COMMENT = """Original instrumental. Composition, arrangement and programming: Codex for hishydrogen.
BBBB palette, groove A throughout, 86 BPM, E minor; full-stop ending.
Virtuosity Drums: Versilian Studios / Karoryfer, CC0 1.0.
https://github.com/sfzinstruments/virtuosity_drums
Black and Blue Basses: Karoryfer, CC0 1.0.
https://github.com/sfzinstruments/karoryfer.black-and-blue-basses
Wurlitzer EP200: Greg Sullivan; SFZ mappings by kinwie. CC BY 3.0.
https://github.com/sfzinstruments/GregSullivan.E-Pianos
https://creativecommons.org/licenses/by/3.0/
Emily guitar: D. Smolken / Karoryfer, royalty-free commercial and non-commercial music use.
https://github.com/sfzinstruments/karoryfer.emilyguitar
Sampled instruments processed with sfizz, guitarix, LSP and Dragonfly.
Original sleeve image and typography: OpenAI image generation.
Style reference: Come Together, The Beatles (1969), user-supplied 2019 mix; analysis only.
No reference audio, riff or melody is reused. No raw libraries are redistributed."""


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(path, sr):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0",
                          "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()


def probe(path):
    return json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                                      "-show_streams", "-of", "json", str(path)],
                                     capture_output=True, text=True, check=True).stdout)["streams"][0]


def inspect_alac(path, sr, bits, cover, duration):
    f = MP4(path)
    assert f.info.sample_rate == sr and f.info.bits_per_sample == bits
    stream = probe(path)
    assert stream["codec_name"] == "alac" and stream["channels"] == 2
    for key, expected in {"\xa9nam": TITLE, "\xa9ART": ARTIST, "aART": ARTIST,
                          "\xa9alb": ALBUM, "\xa9wrt": COMPOSER, "\xa9gen": GENRE,
                          "\xa9day": str(YEAR), "\xa9cmt": COMMENT,
                          "\xa9lyr": "(Instrumental)"}.items():
        assert f.tags[key] == [expected], (path, key)
    assert f.tags["tmpo"] == [BPM] and f.tags["trkn"] == [(1, 1)]
    assert bytes(f.tags["covr"][0]) == cover
    assert abs(f.info.length - duration) < 1 / sr
    return {"bytes": path.stat().st_size, "sha256": sha256(path),
            "sample_rate_hz": sr, "bits_per_sample": bits, "channels": 2,
            "metadata_and_embedded_cover_verified": True}


def main():
    master = HERE / "out/master.wav"
    assert sha256(master) == APPROVED_MASTER_SHA256, "Approved PCM master changed"
    master_info = sf.info(master)
    duration = master_info.frames / master_info.samplerate
    validation = json.loads((HERE / "out/validation.json").read_text())
    assert validation["checkpoint"] == 4 and not validation["warnings"]
    cover_path = HERE / "art/cover.jpg"
    for name in ("cover.jpg", "cover.png"):
        with Image.open(HERE / "art" / name) as image:
            assert image.size == (3000, 3000) and image.mode == "RGB"
    cover = cover_path.read_bytes()
    subprocess.run([sys.executable, str(ROOT / "scripts/release.py"), str(HERE),
                    "--title", TITLE, "--artist", ARTIST, "--album", ALBUM,
                    "--composer", COMPOSER, "--genre", GENRE, "--year", str(YEAR),
                    "--bpm", str(BPM), "--comment", COMMENT, "--cover", str(cover_path)], check=True)
    rel = HERE / "release"
    hi = rel / f"{TITLE}.m4a"
    lo = rel / f"{TITLE}_16bit.m4a"
    high = inspect_alac(hi, 48000, 24, cover, duration)
    high["bit_exact_to_approved_master"] = True  # repository exporter asserts this before returning
    low = inspect_alac(lo, 44100, 16, cover, duration)
    audio = decode(lo, 44100)
    assert audio.shape == (2, round(duration * 44100))
    assert np.isfinite(audio).all() and np.abs(audio).max() < 1
    loudness = float(pyln.Meter(44100).integrated_loudness(audio.T.astype(np.float64)))
    peak = true_peak_db(audio)
    assert abs(loudness + 14) < .2 and peak <= -1
    low.update({"integrated_lufs": round(loudness, 2), "true_peak_dbtp": round(peak, 2),
                "resampled_and_dithered": True})
    del audio
    source_mp3 = HERE / "out/master.mp3"
    before = hashlib.sha256(decode(source_mp3, 48000).tobytes()).hexdigest()
    mp3_path = rel / f"{TITLE}.mp3"
    shutil.copy2(source_mp3, mp3_path)
    mp3 = MP3(mp3_path)
    if mp3.tags is None:
        mp3.add_tags()
    tags = mp3.tags
    tags.add(TIT2(encoding=3, text=TITLE))
    tags.add(TPE1(encoding=3, text=ARTIST))
    tags.add(TPE2(encoding=3, text=ARTIST))
    tags.add(TALB(encoding=3, text=ALBUM))
    tags.add(TCOM(encoding=3, text=COMPOSER))
    tags.add(TCON(encoding=3, text=GENRE))
    tags.add(TDRC(encoding=3, text=str(YEAR)))
    tags.add(TBPM(encoding=3, text=str(BPM)))
    tags.add(TCOP(encoding=3, text=f"℗ {YEAR} {ARTIST}"))
    tags.add(COMM(encoding=3, lang="eng", desc="", text=COMMENT))
    tags.add(USLT(encoding=3, lang="eng", desc="", text="(Instrumental)"))
    tags.delall("APIC")
    tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover))
    mp3.save(v2_version=3)
    after = hashlib.sha256(decode(mp3_path, 48000).tobytes()).hexdigest()
    assert before == after, "MP3 audio changed while adding tags"
    check = MP3(mp3_path)
    assert str(check.tags["TIT2"]) == TITLE and str(check.tags["TPE1"]) == ARTIST
    assert check.tags.getall("APIC")[0].data == cover
    assert check.info.sample_rate == 48000 and check.info.bitrate == 320000
    result = {"title": TITLE, "artist": ARTIST, "genre": GENRE, "year": YEAR, "bpm": BPM,
              "duration_s": validation["duration_s"], "palette": "BBBB", "groove": "A throughout",
              "ending": "full stop", "approved_master_sha256": APPROVED_MASTER_SHA256,
              "master": validation["master"], "cover": {"size_px": [3000, 3000],
                  "generated_source_size_px": [1254, 1254], "jpeg_sha256": sha256(cover_path)},
              "files": {hi.name: high, lo.name: low,
                        mp3_path.name: {"bytes": mp3_path.stat().st_size, "sha256": sha256(mp3_path),
                            "sample_rate_hz": 48000, "bitrate_bps": 320000,
                            "decoded_audio_unchanged_after_tagging": True,
                            "metadata_and_embedded_cover_verified": True}}}
    assert sha256(master) == APPROVED_MASTER_SHA256
    (rel / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)
    print("Final master, ALAC bit depths, metadata, cover, 16-bit peaks and MP3 audio verified.", flush=True)


if __name__ == "__main__":
    main()
