"""Export easy-to-audition clips and DAW MIDI takes from the validated master."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import zipfile

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("groove_exports", HERE / "song.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
song = score.compose()
out = HERE / "out"
audio, sr = sf.read(out / "master.wav", dtype="float32", always_2d=True)
clips = []
for i, (version, title) in enumerate(score.VERSIONS):
    start = song.seconds(i * 68)
    end = min(song.seconds((i + 1) * 68), len(audio) / sr)
    clip = audio[round(start * sr):round(end * sr)].copy()
    # Fade only the silent/release bar; keep the final scat vowel intact.
    n = min(round(.2 * sr), len(clip))
    clip[-n:] *= np.linspace(1, 0, n)[:, None]
    wav = out / f"groove-{version}.wav"
    sf.write(wav, clip, sr, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav),
                    "-codec:a", "libmp3lame", "-b:a", "320k", str(wav.with_suffix(".mp3"))], check=True)
    clips.append({"version": version, "title": title, "file": wav.with_suffix(".mp3").name,
                  "source_start_s": round(start, 2), "source_end_s": round(end, 2),
                  "vocal_enters_s": round(song.seconds(32), 2)})
    # Eight-bar vocal takes, all tracks on their original independent channels.
    b0 = i * 68 + 32
    take = copy.deepcopy(song)
    take.title = f"Floating scat - groove {version}"
    take.markers = [(0, f"{version} - {title} - vocal")]
    take.length_beats = 32.4
    for t in take.tracks.values():
        t.notes = [n for n in t.notes if b0 <= n.start < b0 + 32]
        for n in t.notes:
            n.start -= b0
        old = t.ccs
        initial = {}
        for b, cc, v in sorted(old):
            if b < b0:
                initial[cc] = v
        t.ccs = [(0, cc, v) for cc, v in initial.items()] + [
            (b - b0, cc, v) for b, cc, v in old if b0 <= b < b0 + 32.4]
        t.bends = [(0, 0)] + [(b - b0, v) for b, v in t.bends if b0 <= b < b0 + 32.4]
    take.full_midi().save(out / "midi" / f"groove-{version}-vocal.mid")
(out / "clips.json").write_text(json.dumps(clips, indent=2))
track_map = [{"name": t.name, "instrument": t.instrument, "channel_zero_based": t.channel}
             for t in song.tracks.values()]
(out / "track-map.json").write_text(json.dumps(track_map, indent=2))
archive = out / "scat-jazz-groove-midi.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted((out / "midi").glob("*.mid")):
        z.write(p, "midi/" + p.name.replace(" ", "_"))
    for p in (HERE / "README.md", HERE / "score-check.json", out / "track-map.json"):
        z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    print(len([n for n in z.namelist() if n.endswith(".mid")]), "MIDI files verified")
print(json.dumps(clips, indent=2))
