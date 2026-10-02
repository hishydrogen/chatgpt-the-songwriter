"""Render each track of a Song to a stereo float32 stem at config.SAMPLE_RATE."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from . import config
from .instruments import Instrument, get_instrument
from .song import Song, Track


def _fit(audio: np.ndarray, n: int) -> np.ndarray:
    """(2, N) float32, padded/trimmed to n samples."""
    if audio.ndim == 1:
        audio = np.stack([audio, audio])
    if audio.shape[0] != 2 and audio.shape[1] == 2:
        audio = audio.T
    if audio.shape[0] == 1:
        audio = np.repeat(audio, 2, axis=0)
    out = np.zeros((2, n), dtype=np.float32)
    m = min(n, audio.shape[1])
    out[:, :m] = audio[:, :m]
    return out


def _render_sfz(song: Song, track: Track, inst: Instrument, n: int) -> np.ndarray:
    if not inst.path.exists():
        raise FileNotFoundError(f"{inst.id}: {inst.path} missing - run scripts/fetch_libraries.sh")
    for cc, val in inst.setup_cc.items():
        track.ccs.insert(0, (0.0, cc, val))
    with tempfile.TemporaryDirectory() as td:
        mid = Path(td) / "t.mid"
        wav = Path(td) / "t.wav"
        song.track_midi(track).save(mid)
        cmd = [config.SFIZZ_RENDER, "--sfz", str(inst.path), "--midi", str(mid), "--wav", str(wav),
               "-s", str(config.SAMPLE_RATE), "-q", "3", "-p", str(inst.params.get("polyphony", 256))]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not wav.exists():
            raise RuntimeError(f"sfizz_render failed for {track.name}: {r.stderr[-2000:]}")
        audio, sr = sf.read(wav, dtype="float32", always_2d=True)
    assert sr == config.SAMPLE_RATE, sr
    return _fit(audio.T, n)


SURGE_PLAY_MODES = {"poly": 0, "mono": 1, "mono_st": 2, "mono_fp": 3, "mono_st_fp": 4, "latch": 5}


def _surge_overrides(s, params: dict):
    """Apply surge(..., portamento_ms=, play_mode=, bend_range=, **{"Param Name": raw}) to
    every parameter with that name (both scenes)."""
    if not params:
        return
    from surgepy import constants as c
    named: dict = {}
    for cg in (c.cg_GLOBAL, c.cg_OSC, c.cg_MIX, c.cg_FILTER, c.cg_ENV, c.cg_LFO, c.cg_FX):
        for e in s.getControlGroup(cg).getEntries():
            for p in e.getParams():
                named.setdefault(p.getName(), []).append(p)

    def put(name, val):
        if name not in named:
            raise KeyError(f"Surge has no parameter {name!r}")
        for p in named[name]:
            s.setParamVal(p, float(val))

    for k, v in params.items():
        if k == "portamento_ms":
            put("Portamento", -8.0 if v <= 0 else float(np.log2(v / 1000)))
        elif k == "play_mode":
            put("Play Mode", SURGE_PLAY_MODES[v])
        elif k == "bend_range":
            put("Pitch Bend Up Range", v)
            put("Pitch Bend Down Range", v)
        else:
            put(k, v)


def _render_surge(song: Song, track: Track, inst: Instrument, n: int) -> np.ndarray:
    import surgepy

    s = surgepy.createSurge(config.SAMPLE_RATE)
    if hasattr(s, "setTempo"):
        s.setTempo(float(song.bpm))
    if not s.loadPatch(str(inst.path)):
        raise RuntimeError(f"Surge could not load patch {inst.path}")
    _surge_overrides(s, inst.params)
    bs = s.getBlockSize()
    # let the patch settle (FX, smoothing) before the first note
    warm = s.createMultiBlock(64)
    s.processMultiBlock(warm)

    nblocks = int(np.ceil(n / bs))
    buf = s.createMultiBlock(nblocks)
    pos = 0
    for t, msg in song.timed_messages(track):
        blk = min(nblocks, int(round(t * config.SAMPLE_RATE / bs)))
        if blk > pos:
            s.processMultiBlock(buf, pos, blk - pos)
            pos = blk
        ch = 0
        if msg.type == "note_on" and msg.velocity > 0:
            s.playNote(ch, msg.note, msg.velocity, 0)
        elif msg.type in ("note_off", "note_on"):
            s.releaseNote(ch, msg.note, 0)
        elif msg.type == "control_change":
            s.channelController(ch, msg.control, msg.value)
        elif msg.type == "pitchwheel":
            s.pitchBend(ch, msg.pitch)
    if pos < nblocks:
        s.processMultiBlock(buf, pos, nblocks - pos)
    return _fit(np.asarray(buf, dtype=np.float32), n)


def _render_vst3(song: Song, track: Track, inst: Instrument, n: int) -> np.ndarray:
    import pedalboard

    plug = pedalboard.load_plugin(str(inst.path), plugin_name=inst.params.get("plugin_name"))
    if "preset" in inst.params:
        plug.load_preset(inst.params["preset"])
    for k, v in inst.params.get("set", {}).items():
        setattr(plug, k, v)
    msgs = [m.copy(time=t) for t, m in song.timed_messages(track)]
    audio = plug(msgs, duration=n / config.SAMPLE_RATE, sample_rate=config.SAMPLE_RATE, num_channels=2)
    return _fit(np.asarray(audio, dtype=np.float32), n)


ENGINES = {"sfz": _render_sfz, "surge": _render_surge, "vst3": _render_vst3}


def song_length_samples(song: Song) -> int:
    tail = max([get_instrument(t.instrument).tail for t in song.tracks.values()] + [2.0])
    return int((song.seconds(song.end_beat) + tail) * config.SAMPLE_RATE)


def render_track(song: Song, track: Track, n: int | None = None) -> np.ndarray:
    inst = get_instrument(track.instrument)
    n = n or song_length_samples(song)
    return ENGINES[inst.engine](song, track, inst, n)


def render_stems(song: Song, out_dir: Path, only: list[str] | None = None,
                 cache: bool = True) -> dict[str, np.ndarray]:
    """Render all tracks to out_dir/<name>.wav. Re-renders only tracks whose MIDI changed."""
    out_dir.mkdir(parents=True, exist_ok=True)
    n = song_length_samples(song)
    stems = {}
    for name, track in song.tracks.items():
        wav = out_dir / f"{name}.wav"
        sig = out_dir / f".{name}.sig"
        mf = song.track_midi(track)
        signature = f"{track.instrument}|{n}|" + "|".join(str(m) for t in mf.tracks for m in t)
        if only and name not in only and wav.exists():
            stems[name] = _fit(sf.read(wav, dtype="float32", always_2d=True)[0].T, n)
            continue
        if cache and wav.exists() and sig.exists() and sig.read_text() == signature:
            stems[name] = _fit(sf.read(wav, dtype="float32", always_2d=True)[0].T, n)
            print(f"  [cached] {name}")
            continue
        print(f"  rendering {name} ({track.instrument}, {len(track.notes)} notes)")
        audio = render_track(song, track, n)
        sf.write(wav, audio.T, config.SAMPLE_RATE, subtype="FLOAT")
        sig.write_text(signature)
        stems[name] = audio
    return stems
