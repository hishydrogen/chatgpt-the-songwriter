# ラムネ (feat. 筆墨クミ) - credits

Claude the Songwriter, 2026. Early-2010s vocaloid rock, 170 BPM, D major (last chorus in
E), 3:58. Lyrics: `LYRICS.txt` (Japanese). Written, arranged, sung (synthesised),
programmed, mixed and mastered in code in this repository (`songs/ramune/song.py`, voice
engine `songwriter/voice.py`, guitar rigs through `scripts/lv2host.c`). Style reference:
椎名もた (siinamota), 「少女A」 feat. 鏡音リン (2013) - style, harmony vocabulary, groove and
sound only; no melody, riff, hook, lyric or audio from it is used.

The listener chose every sound at four listening checkpoints: palette
(`songs/summer-palette`), groove sketch (`songs/summer-groove`), samples
(`songs/ramune-samples`) and two rough mixes.

## Vocal

> Vocal: **筆墨クミ (Hitsuboku Kumi)** Japanese VCV Act4 UTAU voicebank by **Cubialpha**
> (https://cubialpha.wixsite.com/koomstar/character), via the unchanged mirror by
> oxygen-dioxide (https://github.com/oxygen-dioxide/hitsuboku-kumi-ja-act4).
> Terms of use: commercial use of the voicebank allowed without permission; samples
> imported into other synthesis software allowed while the name "Hitsuboku Kumi" is kept.
> Sung through this repository's own WORLD-based concatenative engine (no edits to the
> voicebank's wav or oto.ini files). No official 筆墨クミ illustration is used.

## Required attribution (CC BY 4.0)

> Drums: DRSKit by the DrumGizmo team (Lars Muldjord, Bent Bisballe Nyeng) and Jes Eiler of
> DRSDrums, SFZ mapping by kinwie, licensed under CC BY 4.0
> (https://creativecommons.org/licenses/by/4.0/).

## Other sound sources (no attribution required)

| Part | Source | License |
|---|---|---|
| Rhythm, lead and arpeggio guitars | Karoryfer "Emily" guitar, recorded direct (`guitar.emily_di`), played into guitarix amp models (Mesa-style high gain, AC30-style crunch) | CC0 / royalty-free |
| Bass | Karoryfer Black and Blue Basses (dark black, bright), through a guitarix Ampeg-style amp blended with the DI | CC0 |
| Upright piano, strings, glockenspiel | VSCO 2 Community Edition | CC0 |

Amp models: guitarix LV2 plugins (GPL), run offline by `lv2host`. Mixing: LSP Plugins (EQ,
compressors, limiter), Dragonfly Reverb, studio code in `songwriter/`.

Album art: rendered in Blender (Cycles) from `art/bottle_scene.py` - a Codd-neck ramune
bottle modelled from a revolved profile, its marble, soda and bubbles - in front of a
painted sky drawn in SVG (`art/make_art.py`). No photographs, no character art, no logos.
Font Shippori Mincho (SIL OFL 1.1, `art/fonts/OFL-ShipporiMincho.txt`).
