"""Instrument catalog: friendly ids -> rendering engine + notes on how to play them.

Engines
  sfz    rendered offline with sfizz_render (sample libraries in config.LIB_DIR)
  surge  Surge XT via its python bindings, any factory / 3rd-party patch
  vst3   any VST3 instrument via pedalboard

Ids are "<family>.<name>". Use `python -m songwriter instruments` to list them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import config


@dataclass
class Instrument:
    id: str
    engine: str                    # "sfz" | "surge" | "vst3"
    source: str                    # sfz path (relative to LIB_DIR) / surge patch / vst3 path
    desc: str = ""
    range: tuple[int, int] = (0, 127)
    drum_map: dict = field(default_factory=dict)
    setup_cc: dict = field(default_factory=dict)  # CCs sent at time 0 (e.g. mic mix)
    tail: float = 3.0              # seconds of release to keep after the last note
    params: dict = field(default_factory=dict)    # engine specific

    @property
    def path(self) -> Path:
        if self.engine == "sfz":
            return config.LIB_DIR / self.source
        if self.engine == "surge":
            p = Path(self.source)
            return p if p.is_absolute() else config.SURGE_DATA_DIR / self.source
        return Path(self.source)

    @property
    def available(self) -> bool:
        return self.path.exists()


# -- drum maps -------------------------------------------------------------
# Values are MIDI keys, or (key, {cc: value}) when articulation needs a CC first.

VIRTUOSITY_MAP = {
    "kick": 36, "kick_alt": 35,
    "snare": 38, "snare_off": 39, "snare_rim": 40, "sidestick": 37,
    "tom_low": 41, "tom_low_off": 43, "tom_low_rim": 45, "tom_high": 48, "tom_high_off": 50,
    "hh_closed": (42, {4: 127}), "hh_half": (42, {4: 80}), "hh_34": (42, {4: 45}),
    "hh_open": (42, {4: 10}), "hh_pedal": 44,
    "crash": 49, "crash_sizzle": 57, "ride": 51, "ride_bell": 53,
    "ride_flat": 59, "splash": 55,
    "tambourine": 54, "cowbell": 56, "shaker": 82, "cabasa": 69, "claves": 75,
    "bongo_hi": 60, "bongo_lo": 61, "conga_mute": 62, "conga_hi": 63, "conga_lo": 64,
    "triangle_mute": 80, "triangle": 81,
}

DRSKIT_MAP = {
    "kick": 36, "kick_alt": 35,
    "snare": 38, "snare_rim": 40, "sidestick": 37,
    "tom_high": 47, "tom_mid": 43, "tom_low": 41,
    "hh_closed": 42, "hh_closed_edge": 56, "hh_half": 46, "hh_open": 58, "hh_pedal": 44,
    "ride": 51, "ride_bell": 53, "ride_edge": 63,
    "crash": 57, "crash_tip": 55, "crash2": 49, "crash2_tip": 54,
    "choke_crash": 50, "choke_crash2": 48, "choke_ride": 52,
}

SMDRUMS_MAP = {
    "kick": 36, "sidestick": 37,
    "snare": 38, "snare_rim": 39, "snare2": 40, "snare3": 41,
    "hh_closed": 42, "hh_half": 44, "hh_open": 46, "hh_pedal": 50, "hh_pedal_open": 49,
    "hh_closed_open": 51,
    "tom_floor": 43, "tom_low": 45, "tom_mid": 47, "tom_high": 48,
    "crash_small": 54, "crash": 55, "crash2": 56, "crash3": 57, "china": 58,
    "ride": 62, "ride_bell": 63, "ride2": 60, "ride2_bell": 61,
}

GM_DRUM_MAP = {
    "kick": 36, "kick_alt": 35, "sidestick": 37, "snare": 38, "clap": 39, "snare_alt": 40,
    "tom_floor": 41, "hh_closed": 42, "tom_low": 45, "hh_pedal": 44, "tom_mid": 47,
    "hh_open": 46, "tom_high": 50, "crash": 49, "ride": 51, "china": 52, "ride_bell": 53,
    "tambourine": 54, "splash": 55, "cowbell": 56, "crash2": 57, "shaker": 70,
}

# -- catalog ---------------------------------------------------------------

_CATALOG: list[Instrument] = [
    # Grand pianos
    Instrument("piano.salamander", "sfz", "SalamanderGrandPiano/Salamander Grand Piano V3.sfz",
               "Yamaha C5, 16 velocity layers. Bright, detailed; pop/rock/jazz all-rounder.", (21, 108), tail=4),
    Instrument("piano.maestro", "sfz", "MaestroConcertGrand/Maestro Concert Grand.sfz",
               "Yamaha CF-3 concert grand. Warm, wide; ballads, classical, cinematic.", (21, 108), tail=4),
    Instrument("piano.splendid", "sfz", "SplendidGrandPiano/Splendid Grand Piano.sfz",
               "Steinway (AKAI-derived). Mellow, compact; good for dense mixes.", (21, 108), tail=4),
    # Electric pianos / keys
    Instrument("epiano.rhodes", "sfz", "jRhodes3d/jRhodes3d-st-no-xfade.sfz",
               "1977 Rhodes Mark I Stage 73, full-length stereo samples. Neo-soul, lo-fi, R&B.", (28, 100), tail=3),
    Instrument("epiano.wurlitzer", "sfz", "GregSullivan-EPianos/Wurlitzer EP200/Wurlitzer EP200.sfz",
               "Wurlitzer EP200. Barky, gritty; soul, indie, 70s pop.", (33, 96)),
    Instrument("epiano.cp80", "sfz", "GregSullivan-EPianos/CP80/CP80.sfz",
               "Yamaha CP80 electric grand. 80s ballads, city pop.", (28, 103)),
    Instrument("epiano.pianet", "sfz", "GregSullivan-EPianos/Pianet T/Pianet T.sfz",
               "Hohner Pianet T. Soft, reedy; indie pop.", (36, 96)),
    # Drums
    Instrument("drums.virtuosity", "sfz", "VirtuosityDrums/Programs/02-full-kit.sfz",
               "Versilian/Karoryfer multi-mic kit, deep round-robins. Natural, musical; pop/rock/funk.",
               drum_map=VIRTUOSITY_MAP, tail=3),
    Instrument("drums.drskit", "sfz", "DRSKit/DrumGizmo/DRSKit/Stereo/DrumGizmo DRSKit.sfz",
               "DrumGizmo DRSKit, huge multi-velocity rock kit. Punchy rock/indie.",
               drum_map=DRSKIT_MAP, tail=3),
    Instrument("drums.smdrums", "sfz", "SMDrums/Programs/SM_Drums_kit.sfz",
               "SM Drums deeply sampled kit. Tight modern pop/rock.",
               drum_map=SMDRUMS_MAP, tail=3),
    # Bass
    Instrument("bass.darkblack", "sfz", "BlackAndBlueBasses/Programs/06-darkblack_pluck_warm.sfz",
               "Electric bass (fingers), warm. Pop, R&B, funk.", (28, 67), tail=1.5),
    Instrument("bass.darkblack_bright", "sfz", "BlackAndBlueBasses/Programs/05-darkblack_pluck.sfz",
               "Electric bass (fingers), more bite. Rock, funk.", (28, 67), tail=1.5),
    Instrument("bass.babyblue", "sfz", "BlackAndBlueBasses/Programs/04-babyblue_warm.sfz",
               "Short-scale electric bass, warm and round. Indie, Motown.", (28, 67), tail=1.5),
    Instrument("bass.upright_pizz", "sfz", "DoubleBass/d_smolken_rubner_bass_pizz.sfz",
               "Upright double bass pizzicato. Jazz, acoustic.", (28, 67), tail=2),
    Instrument("bass.upright_arco", "sfz", "DoubleBass/d_smolken_rubner_bass_arco.sfz",
               "Upright double bass bowed.", (28, 67), tail=2),
    # Guitars
    Instrument("guitar.green_twang", "sfz", "BlackAndGreenGuitars/Programs/04-green_twang.sfz",
               "Electric guitar (clean, single coil). Indie, funk, pop.", (40, 88), tail=2),
    Instrument("guitar.black_twang", "sfz", "BlackAndGreenGuitars/Programs/07-black_twang.sfz",
               "Electric guitar (humbucker, clean). Warmer; amp sim it for rock.", (40, 88), tail=2),
    Instrument("guitar.green_stac", "sfz", "BlackAndGreenGuitars/Programs/05-green_staccato.sfz",
               "Electric guitar staccato/muted. Funk chops.", (40, 88), tail=1),
    Instrument("guitar.emily", "sfz", "Emilyguitar/emily_clean.sfz",
               "Electric guitar (Emily), clean.", (40, 88), tail=2),
    Instrument("guitar.funky_mute", "sfz", "DamiensFunkyGuitar/Damiens funky guitar.sfz",
               "Muted funk guitar.", (40, 88), tail=1),
    # Solo strings / winds
    Instrument("cello.arco", "sfz", "BigcatCello/Programs/vc_arco_sus_map.sfz",
               "Solo cello sustain (Karoryfer x Bigcat).", (36, 76), tail=3),
    Instrument("cello.pizz", "sfz", "BigcatCello/Programs/03- Plucked.sfz",
               "Solo cello pizzicato.", (36, 76), tail=2),
    Instrument("sax.alto", "sfz", "SoloSax/MTG Solo Saxophones/MTG Alto Sax.sfz",
               "MTG alto sax.", (49, 81), tail=1.5),
    Instrument("sax.tenor", "sfz", "SoloSax/MTG Solo Saxophones/MTG Tenor Sax.sfz",
               "MTG tenor sax.", (44, 76), tail=1.5),
    Instrument("sax.soprano", "sfz", "SoloSax/MTG Solo Saxophones/MTG Soprano Sax.sfz",
               "MTG soprano sax.", (56, 88), tail=1.5),
    Instrument("sax.baritone", "sfz", "SoloSax/MTG Solo Saxophones/MTG Baritone Sax.sfz",
               "MTG baritone sax.", (36, 69), tail=1.5),
]

_BY_ID = {i.id: i for i in _CATALOG}


def register(inst: Instrument) -> Instrument:
    _BY_ID[inst.id] = inst
    return inst


def surge(patch: str, **params) -> str:
    """Instrument id for a Surge XT patch, e.g. surge('Pads/Pad - Silky Strings').

    `patch` is relative to the Surge data dir (patches_factory / patches_3rdparty are
    searched) and may omit the .fxp extension.
    """
    iid = f"surge.{patch}"
    if iid not in _BY_ID:
        p = patch if patch.endswith(".fxp") else patch + ".fxp"
        for base in ("patches_factory", "patches_3rdparty", ""):
            cand = config.SURGE_DATA_DIR / base / p
            if cand.exists():
                p = str(cand)
                break
        register(Instrument(iid, "surge", p, f"Surge XT patch {patch}", tail=params.pop("tail", 4.0), params=params))
    return iid


def get_instrument(iid: str) -> Instrument:
    if iid.startswith("surge.") and iid not in _BY_ID:
        surge(iid[len("surge."):])
    try:
        return _BY_ID[iid]
    except KeyError:
        raise KeyError(f"unknown instrument {iid!r}; see `python -m songwriter instruments`") from None


def catalog() -> list[Instrument]:
    return list(_BY_ID.values())


def _register_generated():
    """Pick up SFZ files generated by scripts/ (VSCO mappings, baked vintage instruments).

    An optional "<id>.json" sidecar may carry desc, drum_map, tail and range.
    """
    import json
    gen = config.LIB_DIR / "_generated"
    if not gen.is_dir():
        return
    for sfz in sorted(gen.glob("*.sfz")):
        iid = sfz.stem  # files are named "<family>.<name>.sfz"
        if iid in _BY_ID:
            continue
        meta = {}
        side = sfz.with_suffix(".json")
        if side.exists():
            meta = json.loads(side.read_text())
        else:
            first = sfz.read_text().splitlines()[0]
            meta["desc"] = first[2:].strip() if first.startswith("//") else ""
        register(Instrument(iid, "sfz", str(sfz.relative_to(config.LIB_DIR)), meta.get("desc", ""),
                            range=tuple(meta.get("range", (0, 127))), drum_map=meta.get("drum_map", {}),
                            tail=meta.get("tail", 3.0)))


_register_generated()
