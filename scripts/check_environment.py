#!/usr/bin/env python3
"""Verify studio packages, instruments, rendering, effects and final audio export."""
from __future__ import annotations

import importlib
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import soundfile as sf

from songwriter import analyze, config, dsp, instruments, mix, render
from songwriter.song import Song


def main():
    report = {"packages": {}, "tools": {}, "renders": {}}
    for line in (ROOT / "requirements.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, expected = line.split("==")
        actual = importlib.metadata.version(name)
        assert actual == expected, f"{name}: {actual} != {expected}"
        importlib.import_module(name)
        report["packages"][name] = actual
    import surgepy
    assert callable(surgepy.createSurge(config.SAMPLE_RATE).setTempo)
    for tool in ("ffmpeg", "sox", "sfizz_render", "lv2host", "fluidsynth"):
        report["tools"][tool] = shutil.which(tool)
        assert report["tools"][tool], f"missing {tool}"
    catalog = instruments.catalog()
    missing = [i.id for i in catalog if not i.available]
    assert not missing, f"missing instruments: {missing}"
    report["instrument_count"] = len(catalog)
    library_names = re.findall(r'^\s*"([^|"\n]+)\|https://',
                               (ROOT / "scripts/fetch_libraries.sh").read_text(), re.MULTILINE)
    report["sample_libraries"] = {}
    for name in library_names:
        marker = config.LIB_DIR / name / ".fetched"
        assert marker.exists(), f"incomplete sample library: {name}"
        report["sample_libraries"][name] = marker.read_text().strip()
    for voice in ("hitsuboku-kumi-ja-act4", "milk-ja", "hikari-one-crystal-ja",
                  "viki-hopper-ja", "adachi-rei"):
        assert (config.LIB_DIR / "voice" / voice / ".fetched").exists(), voice
    patches = sorted(config.SURGE_DATA_DIR.rglob("*.fxp"))
    assert patches, "Surge patches missing"
    report["surge_patch_count"] = len(patches)
    # Exercise each engine, including every installed voicebank.
    choices = ["piano.salamander", "bass.darkblack", "drums.virtuosity",
               instruments.surge(str(patches[0])),
               "voice.kumi", "voice.milk", "voice.hikari", "voice.viki", "voice.adachi"]
    vst = Path("/usr/local/lib/vst3/Surge XT.vst3")
    assert vst.exists(), "Surge XT VST3 missing"
    instruments.register(instruments.Instrument("check.surge_vst3", "vst3", str(vst)))
    choices.append("check.surge_vst3")
    seconds = 4
    n = seconds * config.SAMPLE_RATE
    combined = np.zeros((2, n), np.float32)
    for iid in choices:
        song = Song("Environment check", bpm=120)
        song.length_beats = seconds * 2
        track = song.track("check", iid)
        inst = instruments.get_instrument(iid)
        track.note(36 if iid.startswith("drums.") else 60, 0.25, 2, 100,
                   lyric="ら" if inst.engine == "voice" else None)
        audio = render.ENGINES[inst.engine](song, track, inst, n)
        assert audio.shape == (2, n) and np.isfinite(audio).all(), iid
        peak = float(np.max(np.abs(audio)))
        assert peak > 1e-6, f"silent render: {iid}"
        report["renders"][iid] = {"engine": inst.engine, "peak": peak}
        combined += audio * (0.08 / max(peak, 1e-6))
        print(f"render OK: {iid}", flush=True)
    audio = dsp.eq(combined, [("hpf", 35, 2), ("bell", 1000, -1, 0.7)])
    audio = dsp.compress(audio, threshold=-20, ratio=2)
    for kind in ("plate", "hall", "room"):
        wet = dsp.reverb(audio, kind=kind, decay=0.6)
        assert np.isfinite(wet).all() and np.max(np.abs(wet)) > 1e-8, kind
        audio += 0.03 * wet
    audio = dsp.tube(audio, drive=1)
    amp_audio = dsp.amp(audio, [{"type": "amp", "Distortion": 20}])
    assert np.isfinite(amp_audio).all() and np.max(np.abs(amp_audio)) > 1e-8
    report["effects"] = ["LSP EQ", "LSP compressor", "LSP limiter",
                         "Dragonfly plate/hall/room", "ZamTube", "Guitarix LV2"]
    final, stats = mix.master(audio, {"target_lufs": -14, "ceiling": -1})
    assert np.isfinite(final).all() and abs(stats["lufs"] + 14) < 0.2, stats
    assert stats["true_peak"] <= -0.9, stats
    out = ROOT / "songs/_environment-check/out"
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "master.wav"
    mp3 = out / "master.mp3"
    sf.write(wav, final.T, config.SAMPLE_RATE, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav),
                    "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "null", "-"], check=True)
    analyze.dashboard(final, out / "report.png", title="Studio environment check")
    report["master"] = stats
    report["status"] = "passed"
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
