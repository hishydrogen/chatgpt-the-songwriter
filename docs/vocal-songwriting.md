# Songs with a sung vocal (UTAU voicebanks + songwriter/voice.py)

What we learned making `songs/neon-night` ("ドゥームスクロール (feat. 筆墨クミ)", a
vocaloid-style dance-pop song after Tokyo Manaka's "Doomer"). Read this before writing
any song with lyrics. `CLAUDE.md` has the short version.

## What is possible (and what is not)

- **Yes:** Japanese singing from free UTAU voicebanks, resynthesised with the WORLD
  vocoder by our own engine (`songwriter/voice.py`). Exact pitch, drawn pitch curves,
  natural formants, breaths, phrase endings, harmonies.
- **Not here:** Synthesizer V, VOCALOID, CeVIO, NEUTRINO, DiffSinger voicebanks. Hugging
  Face, Google Drive, official voicebank sites and GitHub release assets are blocked;
  DiffSinger banks are not kept in git repos. The 重音テト UTAU bank is only on its
  official site. Plain git repos (GitHub mirrors) work.
- **Sound:** classic UTAU / early vocaloid. Clear and in tune, a little mechanical; fast
  16th syllables blur. In vocaloid-style music that texture is part of the genre. Say this
  honestly when the user asks for "a voice": it is not SynthV quality.
- **Language:** Japanese only. English lines are sung as katakana English
  (アイム ファイン = あ い む ふぁ い ん); Korean would be a rough kana approximation
  (no batchim) - offer Japanese (+ a few English words) first.

## Voicebanks (`scripts/fetch_voices.sh` -> `libs/voice/`)

| id | Bank | Type, recorded pitches | Character | Commercial use |
|---|---|---|---|---|
| `voice.kumi` | 筆墨クミ Act4 (Cubialpha) | VCV, core A3/D4/A4/D5 + Strong (`S`) + Whisper (`W`) | clear, bright female; best quality | **allowed without permission** (keep the name, credit Cubialpha + link) |
| `voice.milk` | Milk (Xepheris) | VCV, F3/A3/D4/G4 + power C5, falsetto | soft, sweet, hot samples | contact the author |
| `voice.hikari` | Hikari One Crystal (Kyomiii) | CVVC/VCV, C4/E4/G4 | airy, young | contact the author |
| `voice.viki` | Viki Hopper (Seiun) | CVVC, G4/A4 | futuristic, fewest samples, blunt diction | contact the author |
| `voice.adachi` | 足立レイ (みさいる) | CV, made of sine waves only | robot voice | free for doujin (paid ok); corporate commercial: contact |

Each mirror carries `license.md`; read it before a release. For a song meant for release,
default to **Kumi**. Never use the bank's official character art (the Kumi terms forbid
editing it, and it invites confusion).

Release metadata convention (the user asked for it): the title carries the singer,
`"<Title> (feat. 筆墨クミ)"`, while the artist stays `Claude the Songwriter`. Put the bank,
its author and terms in the comment tag and `CREDITS.md`.

## The engine in one paragraph

`voice.render()` groups notes into phrases (a gap of more than `gap` = 40 ms starts a new
one), picks an oto alias per note (`"o る"` VCV first, then `"る"` / `"- る"` CV, plus a
`"o r"` VC tail before CV notes in CVVC banks), places each sample so its preutterance
lands on the note start, keeps the consonant 1:1, plays the first 60 ms of the vowel 1:1
and stretches the rest to the note length, crossfades neighbours over the oto overlap
(spectral envelopes in the log domain), then resynthesises the whole phrase with WORLD
using a drawn f0 curve plus 60% of the sample's own pitch wobble. Pitch suffixes come
from `prefix.map` (nearest recorded pitch otherwise). Analysis (harvest + cheaptrick +
d4c) is cached per wav in `libs/voice/_cache` (Kumi + 4 others = 3.2 GB) and run in
parallel up front.

## Writing for it

```python
VOX_OPTS = {"vibrato_cents": 28, "port_pre": 0.03, "port_post": 0.045, "consonant": 0.9}
self.vox = s.track("vocal", "voice.kumi"); self.vox.opts.update(VOX_OPTS)
HOOK = [("A4", "ろ", .5), ("A4", "ん", .25), ("C5", "り", .75), ("r", "", .5), ...]
```

- **One mora per note**, hiragana or katakana: `きゃ`, `しゅ`, `ん` are single notes.
  Write melodies as `(pitch | "r", lyric, beats)` lists and assert each section's beat
  total (`sum(d for *_, d in MEL) == bars * 4`) - a wrong total shifts every later line.
- **Long vowels and holds:** `ー` (or `-`) as the lyric holds the previous vowel on a new
  pitch (`("F4", "ー", 4.5)` let the last word ring into the outro).
- **っ (small tsu):** write it as a short rest (`("r", "", .25)`). Rests under `tail_gap`
  (0.2 s) end the phrase *without* the breathy "a R" tail - that is a glottal stop, as
  sung. Rests over 0.2 s get the tail sample; over `breath_gap` (0.45 s) a breath is laid
  before the next phrase.
- **Spellings a bank lacks** fall back through `KANA_ALT` (づ->ず, ぢ->じ, を->お, ふぁ->は,
  てぃ->ち ...). Milk has no づ, for example. `KeyError: no alias` means add a fallback.
- **Range:** stay inside the recorded pitches (Kumi A3-D5, comfortable C4-E5). WORLD
  shifts are formant-preserving and fine for +/-5 semitones; beyond that the voice thins.
  The final chorus a half step up topped at F5 - fine. Harmony above F5 was swapped for
  the chord tone below (`Arranger.sing(..., harmony=True)` in `songs/neon-night/song.py`).
- **Per-note options** in `note.x`: `{"vib": 0}` (no vibrato), `{"style": "S"}` (Kumi
  strong voice), `{"consonant": 1.3}`, `{"scoop": 0}`, `{"fall": 0}`, `{"gain_db": 2}`.
- **Track options** (`track.opts`, see `voice.DEFAULTS`): `formant` (+ younger/brighter),
  `breathy`, vibrato depth/rate/onset, portamento timing, overshoot, scoop, fall, jitter,
  `breath_db` (None = no breaths, used on harmony tracks).
- Lyrics and options are part of the stem cache signature: changing a word re-renders
  only the vocal track.

## Composition craft that worked

- **Prosody first.** Count morae per line and give the important ones the long or high
  notes; Japanese pop packs 16ths, but leave 8th-note air between lines - the engine
  needs the rests for breaths and the listener needs them to parse the words.
- **Lines and gaps.** Verses sang about 1.5-2 bars per line and left the rest of the bar
  to the riff. Choruses are denser, with the hook motif repeated over changing chords.
- **Never let the vocal vanish mid-section.** The user flagged a post-chorus that sang
  one "ロンリーナイト" and then stayed silent for 3.5 bars: it sounded broken. Either
  continue as a sung post-chorus hook (4 bars over the riff: ロンリーナイト ひとりでダンス /
  ロンリーナイト ねえ 気づいてよ) or make it clearly instrumental from bar 1.
- **Clash check against the chord timeline** before rendering: list vocal notes that sit a
  semitone from a voiced chord tone, on the beat or longer than an 8th. 9ths over m7
  chords were kept on purpose; an A4 over C7sus4 (rubbing its Bb) was fixed.
- **Harmony:** a diatonic third above if it is a chord tone, else the nearest chord tone
  3-5 semitones up; capped at F5 (below that, take the chord tone under the melody). Two
  takes, 12 ms apart, the second with `formant` 0.4 and more `breathy`, panned -0.45 /
  +0.45, -10 dB, compressed, heavy plate. Chorus and tag only.
- **Key change for the peak:** bridge ii-V into the new key (Abm7 Db7 -> Gb), last chorus
  +1 semitone via the FORM transpose; vocal and harmony follow `tr` automatically.
- **Write the lyric story, not just sounds:** city night, 2 AM convenience store,
  unread messages, endless scrolling. The cover used the same lines.

## Mixing a synthesised lead

- WORLD output is mid-heavy (400 Hz-1 kHz) with a soft top: vocal EQ `hpf 150`,
  `bell 280 -2.5`, `bell 750 -2.5`, `bell 3200 +2.5`, `hshelf 9000 +2.5`; comp 3.5:1 fast.
- Sends: plate (-11 dB) and a dotted-8th delay (-18 dB). Harmonies wetter.
- Level: the lead ended 5-6 dB over the loudest other track in every section (report.json
  `sections`). In the first groove sketch the kick sat above the vocal - check this on
  every render.
- Electronic kit: sidechain the pads/bass to the kick (`duck`) - the "pump" chorus the
  user chose.

## Checking it without ears

- `voice._plan(notes, bank, DEFAULTS, light=True)` prints which alias each note uses -
  run it first for every new bank / lyric (catches missing aliases and wrong pitch
  suffixes before a long render).
- Plot spectrogram + harvest f0 of the rendered stem against the target notes (pitch
  lines should sit on the notes; vibrato only on long ones).
- Click check: sample-to-sample jumps over 2.5x the local RMS. Hits inside "sh"/"ch"
  fricatives are noise, not clicks.
- First render of a bank is slow (harvest analysis, 1-3 min per new set of samples on
  4 cores); later renders take seconds.

## Checkpoints with a voice

1. Palette: every bank sings **the same chorus** over the same groove (levels within
   +/-1 dB). Explain each voice in plain words, including its weakness.
2. Groove sketch: each version 8 bars alone, then 8 bars with the sung hook on top -
   the riff has to leave room for the voice.
3. Rough mix: send the full lyrics with a translation and the section table.

Talking to the user: AskUserQuestion allows only 4 options. When there are more
candidates, do not hide them behind "type it in Other" - the user did not know what the
letters meant. Repeat the timestamp and a plain description inside each option, or split
the choice into two questions.

## Album art lesson (from the same song)

The user asked for a homage to the reference sleeve (a drawing inside an old desktop
window) as classic Mac OS. What happened:
1. A grey-skinned, dark-red-haired girl in flat style: rejected as too close to the
   reference drawing ("plagiarism"). Do not reuse a reference's character palette,
   hairstyle or pose.
2. A cute original anime girl in a cat-ear hoodie: the UI was praised but the character
   felt out of place inside the window.
3. A one-colour stencil silhouette of her: still rejected - no character at all.
4. Final: a notepad with the first lyric lines and a waiting caret, plus one Platinum
   alert centred on the screen ("まだ起きてる？" [寝る] [もう少しだけ]), a 32x32 pixel
   moon icon, menu bar clock at 2:00 AM, scroll thumb near the bottom.
Lessons: for a UI homage keep every element UI-native (documents, dialogs, icons, cursor);
place a modal exactly where the OS would (screen centre); draw icons as small-grid pixel
art, not modern rounded app icons; never use real system icons or logos.
See `songs/neon-night/art/make_art.py` (DotGothic16 font for Japanese bitmap UI type).
