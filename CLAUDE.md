# Claude the Songwriter

A code-driven studio: songs are Python files, rendered with real sampled instruments and
Surge XT, mixed with LSP/Dragonfly plugins, mastered to streaming loudness, and checked
with measurements. The user listens; Claude can't, so **every mix decision is verified
with `report.png` / `report.json`** (and against a reference track when one is given),
and **every sound choice is made by the user from a listening checkpoint**.

Finished example: `songs/mirage/` (Control-era Jam & Lewis style instrumental, released
as ALAC with art). Read its `song.py` before writing a new song: it shows the Arranger
pattern (section methods, riff/answer/stab helpers, per-voice drum tracks, mix dict).

## Environment

Fresh container? Run `scripts/setup.sh` (~30 min; Surge XT build dominates). Check with
`python -m songwriter instruments` (a `!` prefix = library missing). The setup is not
CI-tested; if a step fails, fix the script and commit the fix.

- `libs/` (gitignored, ~13 GB): SFZ libraries from `scripts/fetch_libraries.sh`.
  `libs/_generated/`: VSCO 2 CE mappings (`scripts/build_vsco_sfz.py`) and baked vintage
  instruments (`scripts/build_nasty_palette.py`). Generated instruments may have a
  `<id>.json` sidecar (desc, drum_map, range, tail).
- `sfizz_render` (built from source) renders SFZ offline. It supports `fil_type=lpf_4p`
  and `fileg_*` filter envelopes.
- `surgepy` (Surge XT python bindings, patched with `setTempo`, see
  `scripts/surgepy-settempo.patch`) renders any of the ~3,500 Surge patches.
- VST3 in `/usr/lib/vst3`: LSP (EQ, compressors, limiter...), Dragonfly reverbs, ZAM, DPF;
  Surge XT + Surge XT Effects in `/usr/local/lib/vst3`.
- Network: GitHub clone + raw.githubusercontent, PyPI, Google Fonts work. GitHub release
  assets, archive.org, sourceforge, most web pages (WebFetch) are blocked; WebSearch works.
- Chromium: `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (album art rendering).

## Workflow (what worked)

1. **Research + ask.** Research the target style (WebSearch: producers, gear, tempo, key,
   recording/mixing story). Then ask the user the 3-4 decisions that change the song with
   AskUserQuestion (era fidelity vs modern finish, lead/hook instrument, rights, reference).
2. **Reference track.** Ask the user to upload the reference (uploads land in
   `/root/.claude/uploads/...`, video files are fine). Extract audio to `refs/` (gitignored,
   never commit or sample it) and measure: tempo (`librosa.beat.beat_track`, tight),
   16th swing (onset phase histogram vs beat grid), key (chroma + key profiles), tuning,
   band balance **relative to the mid band**, LUFS / PLR / LRA, structure
   (`librosa.segment.agglomerative` on beat-synced chroma+MFCC) and energy per 4 bars.
   Use it to set tempo, swing, balance targets; style only - never copy melody/riff/hook.
3. **Sound palette checkpoint.** Build candidates, render one audition file where every
   candidate plays the same phrase over the same groove, loudness-matched within +/-1 dB,
   and send a timestamp table. Let the user pick.
4. **Groove sketch checkpoint.** 8 bars, 2-3 variants back to back (e.g. bass choices).
5. **Full arrangement + rough mix checkpoint.** Then polish mix against the reference.
6. **Release.** Album art (HTML/SVG -> Chromium -> 3000x3000), then
   `python scripts/release.py songs/<slug> --title ... --genre ... --bpm ... --comment ...`
   -> 24-bit ALAC (bit-exact, verified) + 16-bit/44.1 ALAC. The app upload limit is below
   45 MiB: send the 16-bit file, `git add -f` the 24-bit one and give the GitHub link.

Build: `python -m songwriter build songs/<slug>` -> `songs/<slug>/out/` (`master.mp3`,
`master.wav` 24-bit 48 kHz, `midi/`, `stems/` gitignored, `report.png`, `report.json`).
Stems are cached by MIDI content, so mix-only changes re-run fast (~5 min for a full song
mostly mixing). Commit `song.py`, `out/master.mp3`, `out/midi/`, `out/report.*`, art.

## Hard-won lessons

- pedalboard does **not** compensate VST3 latency (LSP limiter 372 samples, FIR EQ 6144):
  always process through `dsp.run()`. Set parameters with `dsp.setp()` (clamps to each
  plugin's range; ranges differ, e.g. LSP limiter release max 20 ms). ZamTube is mono.
- Pitch detection lies on bass, chords and percussion (FFT max peak picks harmonics; pYIN
  sticks to fmin). Verify pipelines with a pure sine instead; for timpani-like sources
  read the partial series (1 : 1.5 : 2 : 2.45) to find the principal tone.
- VSCO 2 CE file names use C3 = middle C for most instruments: `build_vsco_sfz.py` checks
  octaves by measurement. Generated instruments were verified within 0.1 semitone.
- Surge patches: measure stereo correlation (some go negative), loudness, centroid before
  offering them. Some "Chords/*" patches play a whole chord per note. Chorus + width
  stacked on a source easily drives correlation under 0.1 - the report warns.
- Kick resonance shows up as a single +9 dB 1/3-octave spike near 60-80 Hz: notch it.
- Master loudness loop must include the true-peak trim (already in `mix.master`).
- Headless Chromium screenshots are shorter than `--window-size`: render taller, crop.
- `pkill -f <pattern>` can kill your own shell if the pattern is in the command line.
- Long loops in generators: guard against non-advancing steps (an art stripe loop hung).

## Rights (for anything that may be released)

Prefer CC0 / CC-BY / self-made sounds and say which were used in the release comment.
CC0: VSCO 2 CE, Virtuosity Drums, Karoryfer libs (basses, guitars, cello), double bass.
CC-BY (credit): Salamander piano (3.0), Greg Sullivan e-pianos (3.0), DRSKit (4.0), MTG sax (4.0).
jRhodes: samples BY-NC to redistribute, but music made with it is CC0 (fine).
SM Drums, Maestro piano, Damien's guitar: no license file - avoid for releases.
`ritchse/tidal-drum-machines` (real LinnDrum/808 etc.): no license - only rebuild such
sounds yourself (see `drums.linn86`). Surge XT output is the user's.

## Instrument choice (best available, by role)

- Grand piano: `piano.salamander` (bright, pop) / `piano.maestro` (warm, ballad, cinematic);
  `piano.upright` for intimate/lo-fi.
- Keys: `epiano.rhodes` (neo-soul, R&B, yacht), `epiano.wurlitzer`, `epiano.cp80` (city pop).
- Drums: `drums.virtuosity` (natural, versatile), `drums.drskit` (rock), `drums.smdrums`
  (tight modern, unlicensed), `drums.linn86` (80s drum machine). Hit names via
  `track.hit(...)`; give each voice its own track (kick/snare/hats/perc/toms) for mixing.
- Bass: `bass.darkblack` (finger, warm), `bass.babyblue` (short-scale), `bass.upright_pizz`;
  synth bass: `surge("Basses/...")`; 8-bit: `mirage.bass_*`.
- Guitars: `guitar.green_twang` / `guitar.black_twang` clean; add `tube` for grit.
  Distorted rhythm guitar is a weak spot of free samples - prefer synths or keep clean.
- Orchestra (VSCO 2 CE): `strings.violins_sus`, `violas_sus`, `celli_sus`, `contrabass_sus`,
  plus spic/pizz/trem; `brass.*`, `winds.*`, `strings.harp`, `perc.*`.
- 80s sampler sounds: `mirage.timpani`, `mirage.metal`, `fairlight.orchhit(_m)`.
  Bake new ones with `songwriter/vintage.py` (`Bake`, `Kit`, machines MIRAGE, FAIRLIGHT,
  LINNDRUM, SP12).
- Synths: Surge XT (`python -m songwriter surge-patches <filter>`). Era-named patches exist:
  "Brass/JX-10 Double Brass", "Brass/OB-8 Jump", "Brass/Toto Brass", "Keys/DX EP",
  "Rozzer/Keys/DX Tonez", "Vincent Zauhar/Pads/CS-80", "Vincent Zauhar/Pads/Classic Warm Jupiters".

## Mixing conventions

- Every stem is normalised to -20 LUFS before its strip, so `gain` is a true balance.
- Strip: eq -> comp -> crush/tape/tube/saturate -> duck -> chorus -> mono/width/pan -> gain
  -> sends -> bus. FX returns: `reverb` (plate/hall/room), `gated` (80s non-linear), `delay`.
- Typical moves: HPF everything but kick/bass; cut 200-500 Hz on keys/pads/guitars;
  keep low end mono (`mono_below`, or `mono: True` on bass); reverb/delay on sends, HPF ~250 Hz.
- Compare bands relative to the mid band with the reference; decide deliberately how far
  a "modern finish" departs from it (Mirage: same sub, +6 dB at 60-150 Hz).
- Master: glue comp 2:1 slow, loudness-targeted limiting to -14 LUFS / -1 dBTP; PLR under
  8 dB means over-limited.

## Talking to the user

Korean. Ranges with "-" (never "~"). Don't overuse the middle dot. Give timestamp tables
for every audition. Report measurements in plain words, not just numbers.
