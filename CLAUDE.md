# Claude the Songwriter

A code-driven studio: songs are Python files, rendered with real sampled instruments and
Surge XT, mixed with LSP/Dragonfly plugins, mastered to streaming loudness, and checked
with measurements. The user listens; Claude can't, so **every mix decision is verified
with `report.png` / `report.json`** (and against a reference track when one is given).

## Environment

Fresh container? Run `scripts/setup.sh` (~20-30 min; Surge XT build dominates).
Check with `python -m songwriter instruments` (a `!` prefix = library missing).

- `libs/` (gitignored, ~13 GB) holds SFZ sample libraries from `scripts/fetch_libraries.sh`.
  `libs/_generated/` holds VSCO 2 CE mappings from `scripts/build_vsco_sfz.py`.
- `sfizz_render` (built from source) renders SFZ offline.
- `surgepy` (Surge XT python bindings, patched with `setTempo`, see
  `scripts/surgepy-settempo.patch`) renders any of the ~3,500 Surge patches.
- VST3 in `/usr/lib/vst3`: LSP (EQ, compressors, limiter...), Dragonfly reverbs, ZAM, DPF;
  Surge XT + Surge XT Effects in `/usr/local/lib/vst3`.
- pedalboard does **not** compensate plugin latency; always go through `dsp.run()`.

## Workflow

1. `songs/<slug>/song.py` defines `compose() -> Song` (notes in beats) and `song.mix`.
2. `python -m songwriter build songs/<slug>` -> `songs/<slug>/out/`:
   `master.mp3` / `master.wav` (24-bit 48 kHz), `midi/` (per-track + full type-1 file
   for DAW import), `stems/` (gitignored), `report.png`, `report.json`.
   Stems are cached by MIDI content; `--only bass` re-renders one track.
3. Read the report, fix warnings, iterate. Send the mp3 + report to the user.
4. `python -m songwriter compare out/master.wav ref.mp3` matches tonal balance /
   loudness / width against a reference the user supplies.

Commit `song.py`, `out/master.mp3`, `out/midi/`, `out/report.*`. Never commit wav stems or libs.

## Instrument choice (best available, by role)

- Grand piano: `piano.salamander` (bright, pop) / `piano.maestro` (warm, ballad, cinematic);
  `piano.upright` for intimate/lo-fi.
- Keys: `epiano.rhodes` (neo-soul, R&B, lo-fi), `epiano.wurlitzer`, `epiano.cp80` (city pop).
- Drums: `drums.virtuosity` (natural, versatile), `drums.drskit` (rock), `drums.smdrums`
  (tight modern). Hit names via `track.hit("kick"|"snare"|"hh_closed"|...)`.
  Electronic drums: Surge `Percussion/*` patches or layer samples.
- Bass: `bass.darkblack` (finger, warm), `bass.babyblue` (short-scale), `bass.upright_pizz`;
  synth bass: `surge("Basses/...")`.
- Guitars: `guitar.green_twang` / `guitar.black_twang` clean; add `tube` for grit.
  Distorted rhythm guitar is a weak spot of free samples - prefer synths or keep clean.
- Orchestra (VSCO 2 CE): `strings.violins_sus`, `violas_sus`, `celli_sus`, `contrabass_sus`,
  plus spic/pizz/trem; `brass.*`, `winds.*`, `strings.harp`, `perc.*`.
- Synths/pads/leads/plucks: Surge XT. `python -m songwriter surge-patches pad`.
  Watch stereo correlation of Surge patches (wide unison can go negative).

## Mixing conventions

- Every stem is normalised to -20 LUFS before its strip, so `gain` is a true balance.
- Strip: eq -> comp -> tube/saturate -> duck -> mono/width/pan -> gain -> sends -> bus.
- Typical moves: HPF everything but kick/bass; cut 200-500 Hz on keys/pads/guitars;
  keep low end mono (`mono_below`, or `mono: True` on bass); duck bass/pads from kick;
  reverb/delay on sends with HPF ~250 Hz.
- Master: glue comp 2:1 slow, then loudness-targeted limiting to -14 LUFS / -1 dBTP
  (adjust `target_lufs` per genre; PLR under 8 dB means over-limited).
- Analysis warnings are heuristics; reference tracks beat rules of thumb.
