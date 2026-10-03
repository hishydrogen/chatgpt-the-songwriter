# Claude the Songwriter

A code-driven studio: songs are Python files, rendered with real sampled instruments and
Surge XT, mixed with LSP/Dragonfly plugins, mastered to streaming loudness and released as
ALAC with album art. The user listens and chooses; Claude can't hear, so **every sound
choice is made by the user at a listening checkpoint**, and Claude checks the technical
side (clipping, mono, mud, resonance, masking, lead vs band) with `report.png` /
`report.json`.

Finished examples - read one `song.py` before writing a new song:
- `songs/mirage/`: Control-era Jam & Lewis style (1986), drum machine, 8-bit sampler sounds.
  Arranger pattern: section methods, riff/answer/stab helpers, per-voice drum tracks, mix dict.
- `songs/catalina-blue/`: 1978 West Coast / yacht rock, live band feel, tenor sax lead,
  key changes, fade-out. Adds a chord timeline (`FORM` -> `chord_at()`), voicing tables,
  groove engines (bounce / pushes / 16ths), humanized timing `T()` with swing, sax and
  synth phrasing, brass standing in for backing vocals.
- `songs/neon-night/`: "ドゥームスクロール (feat. 筆墨クミ)", 2025 vocaloid-style dance pop with
  a **sung Japanese vocal** (UTAU voicebank through `songwriter/voice.py`), self-made
  electronic kit, house-piano riff, pumping supersaw, harmony vocals, half-step key change,
  classic Mac OS UI cover. Before any song with lyrics read `docs/vocal-songwriting.md`.

## New song from a reference (the usual request)

The user uploads a song and says something like "make a really good song like this one".
The full user-facing prompt is `docs/prompts/new-song.md`; this is the same plan.

1. **Base.** Work on the branch the session gives you; if `songs/catalina-blue/` is missing,
   fetch `claude/ecstatic-dirac-t1kvly` (or the newest branch with it) and build on it.
   Fresh container: start `scripts/setup.sh` in the background and research meanwhile.
2. **Understand the reference.** WebSearch the title: era, genre, players and producer,
   gear, recording story, why people love it. From the audio take only what you need to
   write in its spirit: tempo and feel (straight / swung, 8th or 16th hats), key and
   harmonic colour, rough form, the instruments you hear (`scripts/measure_ref.py` helps
   with tempo, feel, key changes and form). The reference sets instruments, era, mood and
   groove. Report briefly, facts apart from guesses. Uploads land in
   `/root/.claude/uploads/...`; extract audio to `refs/` (gitignored, never commit or
   sample it).
3. **Ask** (AskUserQuestion, max 4 questions per call): length ("몇 분 정도요?"), lead
   (an instrument, or a sung Japanese vocal from UTAU voicebanks - Japanese / katakana
   English only, classic-UTAU texture, not SynthV; say what each candidate can't do),
   lyric language and theme if sung, sound direction (era-faithful or era + modern
   clarity), mood and energy. Title and ending (fade or full stop) can wait for the
   rough mix. Max 4 options per question: put the timestamp and a plain description in
   every option - never hide candidates behind "type it in Other".
4. **Checkpoint 1 - sound palette.** One audition file: every candidate plays the same
   phrase over the same groove, candidates within +/-1 dB of each other
   (`python scripts/audition_levels.py songs/<slug>`), timestamp table. Split the
   questions over two AskUserQuestion calls when there are more than four categories.
5. **Checkpoint 2 - groove sketch.** The keyboard/guitar riff that will be the face of the
   song plus the groove, 8 bars, 2-3 versions back to back, timestamp table. Mixing
   versions per section is a valid answer (Catalina Blue: bounce verses, push pre-choruses,
   16th choruses).
6. **Checkpoint 3 - full arrangement, rough mix.** Structure and timestamp table; ask
   title and ending here.
7. **Checkpoint 4 - final mix and release.** Album art, ALAC files, credits (see Release).

Commit and push at every checkpoint. Send audio with `SendUserFile` (attach), mp3 for
checkpoints. Long builds: run in the background and keep the user posted.

## Composition craft (what worked)

- Original material only: take style, harmony vocabulary, groove and sound - never a
  melody, riff, hook or audio from the reference.
- Write the form first (`FORM` list with per-bar chords and a transpose per section), then
  generate parts from the chord timeline so pushes and anticipations land on the right
  chord across section boundaries.
- Hooks: a singable chorus with one rhythmic motif repeated over changing chords; a riff
  with a moving top voice; a peak moment. Catalina Blue: chorus floats on IV, resolves to
  I only at the end, minor iv (Abm6) for the bittersweet turn; chorus 2 pivots via
  Abm7 = G#m7 into a B major bridge whose tonic is V of E, so the last chorus arrives a
  half step up without a truck-driver jump.
- Before rendering, check every lead note against the chord under it: long or on-beat
  notes a semitone from a voiced chord tone are real clashes (fix the note or the chord,
  e.g. Bb7b9 -> Bb13 so a G pickup becomes the 13th). Check instrument ranges too.
- Leave room: in verses the lead sings two bars and the riff answers two bars.
- Live feel: `T()` = swing first, then a gaussian timing error per part (4-6 ms drums,
  6 ms leads), velocity spread +/-4; ghost notes; a different fill at every section end;
  short sustain-pedal dabs on bouncy piano; a second drummer 14 ms behind on the backbeat
  for a "floppy" double-drum feel; tempo leaning into choruses with `Song.tempo()`.
- Sax (MTG SFZ): CC64 legato with overlapping notes, a pitch-bend scoop into phrase
  starts, CC1 vibrato ramps on long notes, CC11 phrase swells, CC80 breath noise.
- Sung vocals (details in `docs/vocal-songwriting.md`): one mora per note as
  `(pitch, lyric, beats)` lists with asserted section lengths; `っ` = short rest, `ー` =
  hold; check every sung note against the chord timeline; never let the vocal stop after
  one call in the middle of a section (make it a sung post-chorus hook or clearly
  instrumental); harmony a third above, capped at F5, two takes panned L/R.
- Brass as backing vocals: sustained 4-voice pads entering just after the beat with CC11
  swells ("ooh"), stabs on separate staccato tracks.

## Environment

Fresh container? Run `scripts/setup.sh` (~30 min; Surge XT build dominates). Check with
`python -m songwriter instruments` (a `!` prefix = library missing). The setup is not
CI-tested; if a step fails, fix the script and commit the fix.

- `libs/` (gitignored, ~13 GB): SFZ libraries from `scripts/fetch_libraries.sh`.
  `libs/_generated/`: VSCO 2 CE mappings (`scripts/build_vsco_sfz.py`) and baked vintage
  instruments (`scripts/build_nasty_palette.py`), `drums.club` (`scripts/build_club_kit.py`).
  Generated instruments may have a `<id>.json` sidecar (desc, drum_map, range, tail).
- `libs/voice/` (~2.6 GB + ~3 GB analysis cache): UTAU voicebanks from
  `scripts/fetch_voices.sh` (GitHub mirrors; Hugging Face and official voicebank sites
  are blocked). `pyworld` (WORLD vocoder) does the analysis and resynthesis.
- `sfizz_render` (built from source) renders SFZ offline. It supports `fil_type=lpf_4p`
  and `fileg_*` filter envelopes, MIDI tempo maps, and CC7/CC11 volume on every SFZ.
- `surgepy` (Surge XT python bindings, patched with `setTempo`, see
  `scripts/surgepy-settempo.patch`) renders any of the ~3,500 Surge patches.
- VST3 in `/usr/lib/vst3`: LSP (EQ, compressors, limiter...), Dragonfly reverbs, ZAM, DPF;
  Surge XT + Surge XT Effects in `/usr/local/lib/vst3`.
- Network: GitHub clone + raw.githubusercontent, PyPI, Google Fonts (also via the
  google/fonts GitHub repo) work. GitHub release assets, archive.org, sourceforge, most web
  pages (WebFetch) are blocked; WebSearch works.
- Chromium: `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (album art rendering).
- Disk: ~13 GB free after setup; a 4-minute, 25-track song needs ~3 GB of stems.

## Tools

- `python -m songwriter build songs/<slug>` -> `songs/<slug>/out/`: `master.mp3`,
  `master.wav` (24-bit 48 kHz), `midi/` (per track + full type-1 file), `stems/`
  (gitignored), `report.png`, `report.json` (master stats, warnings, masking, per-section
  levels of every track). `--only bass` re-renders one track.
- Stems are cached by MIDI content: mix-only changes take 2-5 min; a changed song length
  re-renders every stem (~10 min for 4 minutes and 25 tracks; the multi-mic drum kit is
  the slowest).
- `python -m songwriter instruments [filter]`, `surge-patches [filter]`, `analyze file`.
- `scripts/measure_ref.py refs/x.wav`: tempo and drift, swing and micro-timing per band,
  key per 8 bars (finds key changes), sections and where the song builds.
- `scripts/audition_levels.py songs/<slug>`: candidate levels per audition segment.
- `scripts/release.py`: ALAC files with tags and art (see Release); `--lyrics "$(cat LYRICS.txt)"`.
- `songwriter/voice.py`: UTAU-style singer on WORLD (`voice.*` instruments). Notes carry
  `lyric` and `x` (per-note options); `track.opts` holds engine options (`voice.DEFAULTS`).
  `voice._plan(notes, bank, voice.DEFAULTS, light=True)` shows the alias each note uses.
  First render of a bank analyses its samples (minutes, cached in `libs/voice/_cache`,
  ~3 GB for all banks); later renders take seconds.
- Commit `song.py`, `out/master.mp3`, `out/midi/`, `out/report.*`, art, credits, lyrics.

## Mixing and mastering

- Every stem is normalised to -20 LUFS before its strip, so `gain` is a true balance.
- Strip: eq -> comp -> crush/tape/tube/saturate -> duck -> chorus -> tremolo ->
  mono/width/pan -> gain -> sends -> bus. FX returns: `reverb` (plate/hall/room), `gated`
  (80s non-linear), `delay`.
- Follow the genre's conventions: HPF everything but kick/bass; cut 200-500 Hz on
  keys/pads/guitars; low end mono (`mono_below`, or `mono: True` on bass); reverb/delay on
  sends with HPF ~250 Hz; plate on snare and lead for 70s records, room on drums.
- Lead vs band: `sections` in report.json gives each track's level per section; a sung
  lead sits ~4-6 dB over the loudest other track.
- Report warnings (stereo correlation, mud, dull top, PLR, masking): fix them or explain
  why not.
- Master: glue comp 2:1 slow, loudness-targeted limiting to -14 LUFS / -1 dBTP; keep PLR
  at 12 dB or more (under 8 dB is over-limited). `{"fade": {"start": s, "end": s}}` gives a
  console fade before the limiter and ends the file 0.5 s after it.

## Release

- Album art: HTML/SVG -> headless Chromium at 3x -> 3000x3000 PNG -> JPG
  (`songs/*/art/make_art.py`; fonts downloaded into `art/fonts/` with their OFL text).
  Make it look like a real sleeve of the era: one strong image, quiet period type, lots of
  space. No present-day "retro" signifiers (synthwave stripes, VHS noise, heavy grain,
  cassettes, polaroid frames). Look at the render and fix what you see.
- `python scripts/release.py songs/<slug> --title ... --genre ... --bpm ... --comment ...`
  -> `release/<Title>.m4a` (24-bit/48 kHz, verified bit-exact to master.wav) and
  `<Title>_16bit.m4a` (44.1 kHz, dithered). Put the sample libraries and licenses in the
  comment and in `songs/<slug>/CREDITS.md`.
- The app upload limit is below 45 MiB: send the 16-bit file, `git add -f` the 24-bit one
  (GitHub warns above 50 MB, refuses above 100 MB) and give the GitHub link.

## Hard-won lessons

- pedalboard does **not** compensate VST3 latency (LSP limiter 372 samples, FIR EQ 6144):
  always process through `dsp.run()`. Set parameters with `dsp.setp()` (clamps to each
  plugin's range; ranges differ, e.g. LSP limiter release max 20 ms). ZamTube is mono.
- Speed: the first LSP plugin load in a process costs ~18 s (then ~1 s); `mix.strip` runs
  heavy inserts only over a stem's active span; `saturate` oversamples in 8 s blocks.
- Pitch detection lies on bass, chords and percussion (FFT max peak picks harmonics; pYIN
  sticks to fmin). Verify pipelines with a pure sine instead; for timpani-like sources
  read the partial series (1 : 1.5 : 2 : 2.45) to find the principal tone.
- VSCO 2 CE file names use C3 = middle C for most instruments: `build_vsco_sfz.py` checks
  octaves by measurement. Generated instruments were verified within 0.1 semitone.
- Surge patches: measure stereo correlation (some go negative), loudness, centroid, attack
  and baked-in reverb before offering them. Some "Chords/*" patches play a whole chord per
  note. Chorus + width stacked on a source easily drives correlation under 0.1.
- `surge(patch, portamento_ms=, play_mode="mono_st_fp", bend_range=)` makes legato synth
  leads (glide only on overlapping notes); overrides are part of the instrument id.
- `Track.swing()` only moves notes exactly on the grid: swing before humanizing.
- Humanized notes can start a hair before 0: MIDI export clamps them.
- MTG sax SFZ: CC64 = legato (not sustain), CC1 vibrato (fades in over 2 s), CC11
  expression, CC80 breath noise; ~3.5 s per sample, so notes up to ~6 beats at 120 BPM;
  2 velocity layers (101+ is brighter). Tenor top note E5.
- Two parts writing CC11 to one track fight: give stabs their own tracks (VSCO *_stac).
- Big multi-mic pianos are wide (Splendid raw correlation 0.05): width 0.5-0.6 +
  `mono_below`, or the report warns about mono collapse. Splendid is mellow: high shelf.
- Kick resonance shows up as a single +9 dB 1/3-octave spike near 60-80 Hz: notch it.
- Master loudness loop must include the true-peak trim (already in `mix.master`).
- Headless Chromium screenshots are shorter than `--window-size`: render taller, crop.
- SVG art: mirror reflections about the waterline need translate(0, y_w * (1 + c)) with
  scale(1, -c); evenly spaced lines read as scanlines - use stretched turbulence instead.
- `pkill -f <pattern>` can kill your own shell if the pattern is in the command line.
- Long loops in generators: guard against non-advancing steps (an art stripe loop hung).
- Blocking waits on long builds can get interrupted by the user: background them.
- Voicebanks: oto.ini files are Shift-JIS or UTF-8 (try both); zip names from Japanese
  Windows are cp932 behind a cp437 flag. Banks lack some spellings (Milk has no づ):
  extend `voice.KANA_ALT` rather than changing the lyric.
- Synthesised vocals are mid-heavy: cut ~280 and ~750 Hz, lift 3.2 kHz and air; check
  the lead sits 4-6 dB over the loudest other track (an electronic kick easily beats it).
- Cover art homage: don't reuse the reference's character (palette, hair, pose) - the
  user called that plagiarism. For an OS-UI cover keep everything UI-native (documents,
  dialogs, pixel icons, cursor), put a modal dialog at the exact screen centre, draw icons
  as small-grid pixel art; no real system icons or logos.

## Rights (for anything that may be released)

Prefer CC0 / CC-BY / self-made sounds and say which were used in the release comment.
CC0: VSCO 2 CE, Virtuosity Drums, Karoryfer libs (basses, guitars, cello), double bass.
Public domain: Splendid Grand Piano (AKAI Steinway samples) - a releasable Steinway.
CC-BY (credit): Salamander piano (3.0), Greg Sullivan e-pianos (3.0), DRSKit (4.0), MTG sax (4.0).
jRhodes: samples BY-NC to redistribute, but music made with it is CC0 (fine).
SM Drums, Maestro piano, Damien's guitar: no license file - avoid for releases.
`ritchse/tidal-drum-machines` (real LinnDrum/808 etc.): no license - only rebuild such
sounds yourself (see `drums.linn86`). Surge XT output is the user's.
Self-made: `drums.club` (`scripts/build_club_kit.py`), `drums.linn86` rebuilds.
Voicebanks: 筆墨クミ (`voice.kumi`) commercial use allowed without permission (keep the
name, credit Cubialpha + link). Milk, Hikari One, Viki Hopper: commercial use needs the
author's approval. 足立レイ: doujin use free (paid ok), corporate commercial use: contact.
Release a sung song as "<Title> (feat. <voicebank>)" with the artist still Claude.

## Instrument choice (best available, by role)

- Grand piano: `piano.salamander` (bright, pop) / `piano.splendid` (Steinway, mellow, public
  domain) / `piano.maestro` (warm, unlicensed: not for release); `piano.upright` for
  intimate/lo-fi. Piano + `surge("Brass/OB-8 Jump")` played softly = 70s piano/poly double.
- Keys: `epiano.rhodes` (neo-soul, R&B, yacht; Suitcase `tremolo` in the strip),
  `epiano.wurlitzer`, `epiano.cp80` (city pop).
- Drums: `drums.virtuosity` (natural, versatile; mic mix by CC: 71 kick damping, 105
  overheads, 109 room, 111 vintage mic), `drums.drskit` (rock), `drums.smdrums` (tight
  modern, unlicensed), `drums.linn86` (80s drum machine). Hit names via `track.hit(...)`;
  give each voice its own track (kick/snare/hats/perc/toms/cymbals). Virtuosity also has
  congas, bongos, tambourine, shaker, cowbell, ride and ride bell, sidestick.
- Bass: `bass.darkblack` (finger, warm), `bass.babyblue` (short-scale), `bass.upright_pizz`;
  synth bass: `surge("Basses/...")`; 8-bit: `mirage.bass_*`.
- Guitars: `guitar.green_twang` (Gretsch, clean, bright) / `guitar.black_twang` (Hofner,
  warmer); add `tube` for grit. Distorted rhythm guitar is a weak spot of free samples.
- Brass and orchestra (VSCO 2 CE): `brass.horn_sus`, `trombone_sus`, `trumpet_sus`,
  `trumpet_harmon` (+ `_stac` versions; sustain samples are 4-25 s), `strings.*`,
  `winds.*`, `strings.harp`, `perc.*`.
- Saxes: `sax.tenor` (44-76), `sax.alto` (49-81), `sax.soprano`, `sax.baritone`.
- 80s sampler sounds: `mirage.timpani`, `mirage.metal`, `fairlight.orchhit(_m)`.
  Bake new ones with `songwriter/vintage.py` (`Bake`, `Kit`, machines MIRAGE, FAIRLIGHT,
  LINNDRUM, SP12).
- Electronic drums: `drums.club` (self-made: house / 808 / punch kicks, clap, snare,
  808-style hats, shaker, rim, crash, toms, `riser` = 2 bars at 132 BPM, `impact`).
- Vocals (Japanese): `voice.kumi` (best, clear female, A3-D5 + strong `S` / whisper
  `W` styles), `voice.milk` (soft), `voice.hikari` (airy), `voice.viki` (futuristic,
  few samples), `voice.adachi` (sine-wave robot). Fetch with `scripts/fetch_voices.sh`.
- Synths: Surge XT (`python -m songwriter surge-patches <filter>`). Era-named patches:
  "Brass/JX-10 Double Brass", "Brass/OB-8 Jump", "Brass/Toto Brass", "Keys/DX EP",
  "Polysynths/Jupiter-8", "Polysynths/Oberheim Dreams" (phasey), "Rozzer/Keys/DX Tonez",
  "Vincent Zauhar/Pads/CS-80". Leads: "Kuniklo/Leads/Mini" (dry Minimoog-like),
  "Vospi/Leads/Nice And Elegant Retro" (soft attack, own ambience).

## Talking to the user

- Korean. Ranges with "-" (never "~"). Don't overuse the middle dot.
- Timestamp table with every audition and checkpoint file.
- Explain measurements in plain words, not just numbers; separate facts from guesses.
- Short progress notes during long work; never leave the user waiting in silence.
