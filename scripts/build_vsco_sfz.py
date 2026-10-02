#!/usr/bin/env python3
"""Generate SFZ mappings for VSCO 2 Community Edition (CC0 samples ship without SFZ).

Reads note / dynamic / round-robin from the file names, verifies the octave of every
articulation by measuring the samples' fundamental (naming conventions differ per
instrument), and writes libs/_generated/<id>.sfz which songwriter.instruments picks up.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from songwriter import config  # noqa: E402

ROOT = config.LIB_DIR / "VSCO2CE"
OUT = config.LIB_DIR / "_generated"

# id: (folder, kind, description)   kind: sus (held) | short (one-shot-ish)
SPECS = {
    "strings.violins_sus": ("Strings/Violin Section/susVib", "sus", "Violin section sustain (vibrato). VSCO 2 CE"),
    "strings.violins_spic": ("Strings/Violin Section/Spic", "short", "Violin section spiccato. VSCO 2 CE"),
    "strings.violins_pizz": ("Strings/Violin Section/Pizz", "short", "Violin section pizzicato. VSCO 2 CE"),
    "strings.violins_trem": ("Strings/Violin Section/Trem", "sus", "Violin section tremolo. VSCO 2 CE"),
    "strings.violas_sus": ("Strings/Viola Section/susvib", "sus", "Viola section sustain. VSCO 2 CE"),
    "strings.violas_spic": ("Strings/Viola Section/spic", "short", "Viola section spiccato. VSCO 2 CE"),
    "strings.violas_pizz": ("Strings/Viola Section/pizz", "short", "Viola section pizzicato. VSCO 2 CE"),
    "strings.violas_trem": ("Strings/Viola Section/trem", "sus", "Viola section tremolo. VSCO 2 CE"),
    "strings.celli_sus": ("Strings/Cello Section/susvib", "sus", "Cello section sustain. VSCO 2 CE"),
    "strings.celli_spic": ("Strings/Cello Section/spic", "short", "Cello section spiccato. VSCO 2 CE"),
    "strings.celli_pizz": ("Strings/Cello Section/pizzT", "short", "Cello section pizzicato. VSCO 2 CE"),
    "strings.celli_trem": ("Strings/Cello Section/trem", "sus", "Cello section tremolo. VSCO 2 CE"),
    "strings.contrabass_sus": ("Strings/Solo Contrabass/SusVib", "sus", "Contrabass sustain (vib). VSCO 2 CE"),
    "strings.contrabass_pizz": ("Strings/Solo Contrabass/Pizz", "short", "Contrabass pizzicato. VSCO 2 CE"),
    "strings.contrabass_spic": ("Strings/Solo Contrabass/Spic", "short", "Contrabass spiccato. VSCO 2 CE"),
    "strings.violin_solo": ("Strings/Solo Violin/Arco Vib", "sus", "Solo violin arco vibrato. VSCO 2 CE"),
    "strings.violin_solo_pizz": ("Strings/Solo Violin/Pizz", "short", "Solo violin pizzicato. VSCO 2 CE"),
    "strings.harp": ("Strings/Harp", "short", "Concert harp. VSCO 2 CE"),
    "brass.horn_sus": ("Brass/F Horn/sus", "sus", "French horn sustain. VSCO 2 CE"),
    "brass.horn_stac": ("Brass/F Horn/stac", "short", "French horn staccato. VSCO 2 CE"),
    "brass.trumpet_sus": ("Brass/Trumpet/sus", "sus", "Trumpet sustain. VSCO 2 CE"),
    "brass.trumpet_vib": ("Brass/Trumpet/susvib", "sus", "Trumpet sustain vibrato. VSCO 2 CE"),
    "brass.trumpet_stac": ("Brass/Trumpet/stac", "short", "Trumpet staccato. VSCO 2 CE"),
    "brass.trumpet_harmon": ("Brass/Trumpet/harmonM-sus", "sus", "Trumpet harmon mute. VSCO 2 CE"),
    "brass.trombone_sus": ("Brass/Tenor Trombone/sus", "sus", "Tenor trombone sustain. VSCO 2 CE"),
    "brass.trombone_stac": ("Brass/Tenor Trombone/stac", "short", "Tenor trombone staccato. VSCO 2 CE"),
    "brass.tuba_sus": ("Brass/Tuba/sus", "sus", "Tuba sustain. VSCO 2 CE"),
    "brass.tuba_stac": ("Brass/Tuba/stac", "short", "Tuba staccato. VSCO 2 CE"),
    "winds.flute_sus": ("Woodwinds/Flute/susvib", "sus", "Flute sustain vibrato. VSCO 2 CE"),
    "winds.flute_stac": ("Woodwinds/Flute/stac", "short", "Flute staccato. VSCO 2 CE"),
    "winds.oboe_sus": ("Woodwinds/Oboe/Vib", "sus", "Oboe sustain vibrato. VSCO 2 CE"),
    "winds.oboe_stac": ("Woodwinds/Oboe/Stacc", "short", "Oboe staccato. VSCO 2 CE"),
    "winds.clarinet_sus": ("Woodwinds/Clarinet/susLong", "sus", "Clarinet sustain. VSCO 2 CE"),
    "winds.clarinet_stac": ("Woodwinds/Clarinet/stac", "short", "Clarinet staccato. VSCO 2 CE"),
    "winds.bassoon_sus": ("Woodwinds/Bassoon/sus", "sus", "Bassoon sustain. VSCO 2 CE"),
    "winds.bassoon_stac": ("Woodwinds/Bassoon/stac", "short", "Bassoon staccato. VSCO 2 CE"),
    "perc.glockenspiel": ("Percussion/Glock", "short", "Glockenspiel. VSCO 2 CE"),
    "perc.marimba": ("Percussion/Marimba", "short", "Marimba. VSCO 2 CE"),
    "perc.xylophone": ("Percussion/Xylo", "short", "Xylophone. VSCO 2 CE"),
    "piano.upright": ("Keys/Upright Nr1", "short", "Upright piano, intimate/felt-ish. VSCO 2 CE"),
}

DYN_ORDER = ["ppp", "pp", "p", "mp", "soft", "quiet", "mf", "medium", "f", "loud", "ff", "fff"]
NOTE_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d)$")
PREFERRED_MIC = ("sum", "main")


def parse(name: str):
    toks = Path(name).stem.split("_")
    note = vel = None
    rr = 1
    mic = ""
    for i, t in enumerate(toks):
        m = NOTE_RE.match(t)
        if m and note is None:
            L, acc, o = m.groups()
            note = 12 * (int(o) + 1) + "C D EF G A B".index(L.upper()) + (1 if acc == "#" else -1 if acc == "b" else 0)
            continue
        if note is None:
            continue
        tl = t.lower()
        if re.fullmatch(r"v\d+", tl):
            vel = ("v", int(tl[1:]))
        elif tl in DYN_ORDER:
            vel = ("d", DYN_ORDER.index(tl))
        elif re.fullmatch(r"(rr)?\d+", tl):
            rr = int(re.sub(r"\D", "", tl))
        elif tl in ("sum", "main", "mid", "far", "close", "room"):
            mic = tl
    return note, vel or ("v", 1), rr, mic


def f0_midi(path: Path) -> float | None:
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    a = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max()))
    seg = x[a + int(0.05 * sr): a + int(0.05 * sr) + int(0.5 * sr)]
    if len(seg) < 4096:
        seg = x[a: a + 8192]
    if len(seg) < 2048:
        return None
    seg = seg * np.hanning(len(seg))
    n = 1 << 17
    spec = np.abs(np.fft.rfft(seg, n))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    # harmonic product spectrum (3 harmonics), 25 Hz - 4 kHz
    hps = spec.copy()
    for h in (2, 3):
        dec = spec[::h]
        hps[: len(dec)] *= dec
    lo, hi = np.searchsorted(freqs, [25, 4000])
    k = lo + int(np.argmax(hps[lo:hi]))
    f = freqs[k]
    return 69 + 12 * np.log2(f / 440) if f > 0 else None


def build(iid: str, folder: str, kind: str, desc: str) -> str | None:
    d = ROOT / folder
    files = sorted(p for p in d.glob("*.wav"))
    if not files:
        print(f"  skip {iid}: no samples")
        return None
    parsed = [(p, *parse(p.name)) for p in files]
    parsed = [t for t in parsed if t[1] is not None]
    mics = {t[4] for t in parsed}
    if len(mics) > 1:
        keep = next((m for m in PREFERRED_MIC if m in mics), sorted(mics)[0])
        parsed = [t for t in parsed if t[4] == keep]
    # octave check on up to 6 samples spread over the range
    by_note = sorted({t[1] for t in parsed})
    probe = [next(t for t in parsed if t[1] == nn) for nn in by_note[:: max(1, len(by_note) // 6)]]
    diffs = []
    for p, nn, *_ in probe:
        m = f0_midi(p)
        if m is not None:
            diffs.append(round((m - nn) / 12))
    offset = 12 * int(np.median(diffs)) if diffs else 0
    # layout
    notes = sorted({t[1] + offset for t in parsed})
    bounds = {}
    for i, nn in enumerate(notes):
        lo = 0 if i == 0 else (notes[i - 1] + nn) // 2 + 1
        hi = 127 if i == len(notes) - 1 else (nn + notes[i + 1]) // 2
        bounds[nn] = (lo, hi)
    groups = defaultdict(list)  # note -> [(velkey, rr, path)]
    for p, nn, vel, rr, _ in parsed:
        groups[nn + offset].append((vel, rr, p))
    lines = [f"// {desc}", f"// generated by scripts/build_vsco_sfz.py (octave offset {offset:+d})",
             "<control>", "default_path=../VSCO2CE/", "<global>",
             "amp_veltrack=60" if kind == "sus" else "amp_veltrack=75",
             f"ampeg_attack={0.02 if kind == 'sus' else 0.001}",
             f"ampeg_release={0.45 if kind == 'sus' else 0.25}",
             "" if kind == "sus" else "loop_mode=one_shot"]
    for nn in notes:
        lo, hi = bounds[nn]
        layers = sorted({v for v, _, _ in groups[nn]})
        for li, v in enumerate(layers):
            vlo = 1 + (127 * li) // len(layers)
            vhi = (127 * (li + 1)) // len(layers)
            rrs = sorted((r, p) for vv, r, p in groups[nn] if vv == v)
            for si, (_, p) in enumerate(rrs):
                rel = p.relative_to(ROOT).as_posix()
                region = (f"<region> sample={rel} pitch_keycenter={nn} lokey={lo} hikey={hi} "
                          f"lovel={vlo} hivel={vhi}")
                if len(rrs) > 1:
                    region += f" seq_length={len(rrs)} seq_position={si + 1}"
                lines.append(region)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{iid}.sfz").write_text("\n".join(l for l in lines if l) + "\n")
    print(f"  {iid:<26} {len(parsed):>3} samples, {len(notes)} notes, "
          f"{max(len({v for v, _, _ in g}) for g in groups.values())} vel layers, octave {offset:+d}")
    return iid


def main():
    if not ROOT.exists():
        sys.exit(f"{ROOT} missing - run scripts/fetch_libraries.sh VSCO2CE")
    for iid, (folder, kind, desc) in SPECS.items():
        build(iid, folder, kind, desc)


if __name__ == "__main__":
    main()
