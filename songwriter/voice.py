"""Singing voice: a small UTAU-style concatenative synthesiser built on the WORLD vocoder.

UTAU voicebanks (wav + oto.ini [+ prefix.map]) are cut into aliases ("a か" for VCV,
"か" / "- か" for CV, "a k" for CVVC tails). Every sample used is analysed once with WORLD
(f0, spectral envelope, aperiodicity; cached in libs/voice/_cache). A phrase is then built
frame by frame: each note's sample is placed so its preutterance lands on the note start,
its vowel is stretched to the note length, neighbours crossfade over the oto overlap, and
the whole phrase is resynthesised with a drawn pitch curve (scoop, portamento, overshoot,
vibrato) - so pitch is exact and formants stay natural.

    t = song.track("vox", "voice.kumi")
    t.sing("C5 D5 E5", "よ る の", beat=0, dur=0.5)       # or t.note(..., lyric="よ")
    t.opts.update(vibrato_cents=35, formant=0.5)            # engine options, see DEFAULTS

Lyrics are one mora per note in hiragana or katakana ("きゃ", "ン"). "ー" or "-" holds the
previous vowel on a new pitch. A note may carry per-note options in `note.x`
(e.g. {"vib": 0} to switch vibrato off, {"style": "S"} for a strong-voice suffix).
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from . import config

FP = 5.0             # WORLD frame period, ms
CACHE = config.LIB_DIR / "voice" / "_cache"

DEFAULTS = dict(
    gain_db=0.0,
    formant=0.0,          # semitones; + brighter / younger, - darker
    breathy=0.0,          # 0..1 adds aperiodicity
    vibrato_cents=30.0,   # depth (+/-) on long notes
    vibrato_rate=5.8,     # Hz
    vibrato_after=0.32,   # s into a note before vibrato starts
    vibrato_fade=0.25,    # s fade-in
    port_pre=0.030,       # s before the next note where the glide starts
    port_post=0.050,      # s after the note start where it settles
    overshoot=18.0,       # cents past the target on upward leaps
    scoop=-90.0,          # cents at phrase starts, rising into the note
    scoop_time=0.07,
    fall=-60.0,           # cents drop on phrase ends
    fall_time=0.10,
    jitter=0.6,           # how much of the sample's own pitch wobble to keep (0..1)
    release=0.08,         # s fade at phrase ends
    consonant=1.0,        # >1 lengthens consonants, <1 shortens
    gap=0.04,             # s of silence between notes that starts a new phrase
    tail_alias=True,      # use "a R" / "a -" ending samples when the bank has them
    breath_db=-4.0,       # breath before phrases that follow a rest (None = off)
    breath_gap=0.45,      # s of rest needed for a breath
    tail_gap=0.2,         # ... only before rests longer than this (s); shorter = a glottal stop
)

# -- kana -------------------------------------------------------------------

_ROWS = {
    "a": "あかさたなはまやらわがざだばぱぁゃゎ",
    "i": "いきしちにひみりぎじぢびぴぃ",
    "u": "うくすつぬふむゆるぐずづぶぷぅゅゔ",
    "e": "えけせてねへめれげぜでべぺぇ",
    "o": "おこそとのほもよろをごぞどぼぽぉょ",
}
VOWEL_OF = {k: v for v, ks in _ROWS.items() for k in ks}
VOWEL_OF["ん"] = "n"
VOWEL_KANA = {"a": "あ", "i": "い", "u": "う", "e": "え", "o": "お", "n": "ん"}

_CONS_ROWS = {
    "k": "かきくけこ", "g": "がぎぐげご", "s": "さすせそ", "sh": "し", "z": "ざずぜぞづ",
    "j": "じぢ", "t": "たてと", "ch": "ち", "ts": "つ", "d": "だでど", "n": "なにぬねの",
    "h": "はひへほ", "f": "ふ", "b": "ばびぶべぼ", "p": "ぱぴぷぺぽ", "m": "まみむめも",
    "y": "やゆよ", "r": "らりるれろ", "w": "わを", "v": "ゔ",
}
CONS_OF = {k: c for c, ks in _CONS_ROWS.items() for k in ks}
# same sound, other spelling: tried when a bank lacks the first
KANA_ALT = {"づ": "ず", "ぢ": "じ", "を": "お", "ゔ": "ぶ", "ゐ": "い", "ゑ": "え",
            "でぃ": "ぢ", "てぃ": "ち", "とぅ": "つ", "どぅ": "ず", "ふぁ": "は", "うぃ": "い"}


def consonants(lyric: str) -> list[str]:
    """Consonant names a CVVC bank may use for the VC part before this mora, best first."""
    lyric = hira(lyric).strip()
    if not lyric or lyric[0] not in CONS_OF:
        return []
    c = CONS_OF[lyric[0]]
    if len(lyric) > 1 and lyric[1] in "ゃゅょ" and c not in ("sh", "ch", "j"):
        return [c + "y", c]
    return [c, c[0]] if len(c) > 1 else [c]


def hira(s: str) -> str:
    """Katakana -> hiragana (ー and punctuation pass through)."""
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def vowel(lyric: str, prev: str = "-") -> str:
    lyric = hira(lyric).strip()
    if not lyric or lyric in ("ー", "-"):
        return prev
    for c in reversed(lyric):
        if c in VOWEL_OF:
            return VOWEL_OF[c]
    return prev


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_name(m: int) -> str:
    return f"{NOTE_NAMES[m % 12]}{m // 12 - 1}"


# -- voicebank ------------------------------------------------------------

@dataclass
class Oto:
    wav: Path
    alias: str
    offset: float
    consonant: float
    cutoff: float
    preutter: float
    overlap: float


def _read_text(p: Path) -> str:
    raw = p.read_bytes()
    for enc in ("utf-8-sig", "cp932"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("cp932", errors="replace")


class Voicebank:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.oto: dict[str, Oto] = {}
        for ini in sorted(self.root.rglob("oto.ini")):
            for line in _read_text(ini).splitlines():
                if "=" not in line:
                    continue
                fname, _, rest = line.partition("=")
                parts = rest.split(",")
                if len(parts) < 6:
                    continue
                wav = ini.parent / fname.strip()
                if not wav.exists():
                    continue
                alias = parts[0].strip() or Path(fname).stem
                try:
                    vals = [float(x) if x.strip() else 0.0 for x in parts[1:6]]
                except ValueError:
                    continue
                self.oto.setdefault(alias, Oto(wav, alias, *vals))
        self.prefix: dict[str, tuple[str, str]] = {}
        pm = self.root / "prefix.map"
        if pm.exists():
            for line in _read_text(pm).splitlines():
                cols = line.split("\t")
                if len(cols) >= 3:
                    self.prefix[cols[0].strip()] = (cols[1].strip(), cols[2].strip())
        self.suffixes = sorted({s for _, s in self.prefix.values()}, key=len, reverse=True)

    def lookup(self, base: str, midi: int, style: str = "") -> Oto | None:
        """Alias for `base` at this pitch: prefix.map suffix first, then any pitch variant."""
        pre, suf = self.prefix.get(note_name(midi), ("", ""))
        for cand in (f"{pre}{base}{style}{suf}", f"{pre}{base}{suf}", f"{base}{style}{suf}",
                     f"{base}{suf}", f"{base}{style}", base):
            if cand in self.oto:
                return self.oto[cand]
        # nearest other pitch suffix
        tried = []
        for note, (p, s) in sorted(self.prefix.items(), key=lambda kv: abs(_midi(kv[0]) - midi)):
            if s in tried:
                continue
            tried.append(s)
            if f"{p}{base}{s}" in self.oto:
                return self.oto[f"{p}{base}{s}"]
        return None


def _midi(name: str) -> int:
    n = name.rstrip("0123456789-")
    return NOTE_NAMES.index(n) + 12 * (int(name[len(n):]) + 1)


_BANKS: dict[str, Voicebank] = {}


def bank(root: Path) -> Voicebank:
    key = str(root)
    if key not in _BANKS:
        _BANKS[key] = Voicebank(root)
    return _BANKS[key]


# -- WORLD analysis -------------------------------------------------------

_ANA: dict[str, tuple] = {}


def analyse(wav: Path):
    """(f0, sp, ap, fs) of a sample, cached on disk (float32 npz)."""
    key = str(wav)
    if key in _ANA:
        return _ANA[key]
    import pyworld as pw
    h = hashlib.sha1(f"{wav}|{wav.stat().st_size}|{wav.stat().st_mtime_ns}".encode()).hexdigest()[:16]
    cf = CACHE / f"{h}.npz"
    if cf.exists():
        z = np.load(cf)
        res = (z["f0"].astype(np.float64), z["sp"].astype(np.float64), z["ap"].astype(np.float64), int(z["fs"]))
    else:
        x, fs = sf.read(wav, dtype="float64", always_2d=True)
        x = x[:, 0]
        f0, t = pw.harvest(x, fs, f0_floor=70.0, f0_ceil=1100.0, frame_period=FP)
        sp = pw.cheaptrick(x, f0, t, fs)
        ap = pw.d4c(x, f0, t, fs)
        CACHE.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cf, f0=f0.astype(np.float32), sp=sp.astype(np.float32),
                            ap=ap.astype(np.float32), fs=fs)
        res = (f0, sp, ap, fs)
    _ANA[key] = res
    return res


def prefetch(wavs: list[Path], workers: int = 8):
    """Analyse many samples in parallel (first render of a bank)."""
    from concurrent.futures import ProcessPoolExecutor
    todo = []
    for w in dict.fromkeys(wavs):
        h = hashlib.sha1(f"{w}|{w.stat().st_size}|{w.stat().st_mtime_ns}".encode()).hexdigest()[:16]
        if not (CACHE / f"{h}.npz").exists():
            todo.append(w)
    if todo:
        with ProcessPoolExecutor(workers) as ex:
            list(ex.map(_analyse_only, todo))


def _analyse_only(w):
    analyse(w)
    return True


# -- phrase building ------------------------------------------------------

@dataclass
class VNote:
    t0: float       # s
    t1: float       # s
    midi: int
    lyric: str
    vel: int = 100
    x: dict | None = None


@dataclass
class Piece:
    oto: Oto
    s0: float       # output time where the sample segment starts (s)
    s1: float = 0.0  # output time where it ends
    pre: float = 0.0   # (possibly compressed) preutterance, s
    ov: float = 0.0    # overlap with the previous piece, s
    scale: float = 1.0  # time compression of the head (fast notes)
    gain: float = 1.0
    vowel_hold: bool = True  # stretch the vowel to fill (False for VC tails)


def _plan(notes: list[VNote], vb: Voicebank, o: dict, light: bool = False,
          tail: bool = True) -> list[Piece]:
    """Pieces (samples placed in time) for one phrase. light=True skips sample analysis."""
    pieces: list[Piece] = []
    prev_v = "-"
    for i, n in enumerate(notes):
        x = n.x or {}
        lyr = hira(n.lyric).strip()
        style = x.get("style", "")
        if lyr in ("", "ー", "-"):
            lyr = VOWEL_KANA.get(prev_v, "あ")
            hold = True
        else:
            hold = False
        cands = []
        for ly in (lyr, KANA_ALT.get(lyr)) if lyr in KANA_ALT else (lyr,):
            cands += [f"{prev_v} {ly}"] if prev_v != "-" else [f"- {ly}"]
            cands += [ly, f"- {ly}"] if not hold or prev_v == "-" else [ly]
        oto = None
        for c in cands:
            oto = vb.lookup(c, n.midi, style)
            if oto:
                break
        if oto is None:
            raise KeyError(f"voicebank {vb.root.name} has no alias for {lyr!r} (tried {cands})")
        vc = None
        if pieces and not oto.alias.startswith(f"{prev_v} ") and prev_v != "-":
            for c in consonants(lyr):
                vc = vb.lookup(f"{prev_v} {c}", notes[i - 1].midi)
                if vc:
                    break
        cons = o["consonant"] * x.get("consonant", 1.0)
        pre = max(0.0, oto.preutter / 1000 * cons)
        ov = oto.overlap / 1000 * cons
        gain = 10 ** ((n.vel - 100) / 100 * 6 / 20) * 10 ** (x.get("gain_db", 0) / 20)
        p = Piece(oto, n.t0 - pre, pre=pre, ov=ov, scale=cons, gain=gain)
        if pieces:
            prev = pieces[-1]
            room = n.t0 - notes[i - 1].t0
            if pre - min(ov, 0) > 0.6 * room:     # fast notes: squeeze this head
                k = 0.6 * room / max(1e-6, pre - min(ov, 0))
                p.pre, p.ov, p.scale = pre * k, ov * k, cons * k
                p.s0 = n.t0 - p.pre
            if vc is not None:
                vpre = vc.preutter / 1000 * min(1.0, p.scale / max(cons, 1e-6))
                q = Piece(vc, p.s0 - vpre, pre=vpre, ov=vc.overlap / 1000 * min(1.0, p.scale / max(cons, 1e-6)),
                          gain=prev.gain, vowel_hold=False)
                q.s0 = max(q.s0, notes[i - 1].t0 + 0.4 * (p.s0 - notes[i - 1].t0))
                q.s1 = p.s0 + max(p.ov, 0.012)
                prev.s1 = q.s0 + max(q.ov, 0.012)
                pieces.append(q)
            else:
                prev.s1 = p.s0 + max(p.ov, 0.012)
        pieces.append(p)
        prev_v = vowel(lyr, prev_v)
    last = notes[-1]
    pieces[-1].s1 = last.t1
    if tail and o["tail_alias"] and prev_v in VOWEL_KANA:
        for c in (f"{prev_v} R", f"{prev_v} -", f"{prev_v}R", f"{prev_v} 息"):
            oto = vb.lookup(c, last.midi)
            if oto:
                pre = oto.preutter / 1000
                tail = Piece(oto, last.t1 - pre, pre=pre, ov=oto.overlap / 1000, vowel_hold=False,
                             gain=pieces[-1].gain)
                pieces[-1].s1 = tail.s0 + max(tail.ov, 0.012)
                cut = 0.3 if light else _seg_len(oto)
                tail.s1 = tail.s0 + cut
                pieces.append(tail)
                break
    return pieces


def _seg_len(oto: Oto) -> float:
    f0, sp, ap, fs = analyse(oto.wav)
    total = len(f0) * FP / 1000
    end = (oto.offset - oto.cutoff) / 1000 if oto.cutoff < 0 else total - oto.cutoff / 1000
    return max(0.02, end - oto.offset / 1000)


def _sample_times(p: Piece, tau: np.ndarray, total: float) -> np.ndarray:
    """Map output time since p.s0 -> sample time (s) inside the wav."""
    o = p.oto
    off = o.offset / 1000
    cons = max(o.consonant / 1000, o.preutter / 1000)
    end = (off - o.cutoff / 1000) if o.cutoff < 0 else total - o.cutoff / 1000
    end = max(end, off + cons + 0.03)
    k = p.scale if p.scale > 0 else 1.0
    head_out = cons * k                # output length of the fixed (consonant) part
    L_out = max(1e-3, (p.s1 - p.s0) - head_out)
    L_in = end - (off + cons)
    out = np.empty_like(tau)
    head = tau < head_out
    out[head] = off + tau[head] / k
    r = tau[~head] - head_out
    if not p.vowel_hold or L_out <= L_in:
        out[~head] = off + cons + r
    else:
        keep = min(0.06, 0.4 * L_in)  # play the vowel onset 1:1, stretch the rest
        rate = (L_in - keep) / max(1e-6, L_out - keep)
        out[~head] = off + cons + np.where(r < keep, r, keep + (r - keep) * rate)
    return np.clip(out, 0, total - FP / 1000)


def _interp_frames(arr: np.ndarray, idx: np.ndarray) -> np.ndarray:
    i0 = np.floor(idx).astype(int)
    i1 = np.minimum(i0 + 1, len(arr) - 1)
    w = (idx - i0)[:, None]
    return arr[i0] * (1 - w) + arr[i1] * w


def _pitch_curve(notes: list[VNote], times: np.ndarray, o: dict) -> np.ndarray:
    """Target pitch (midi, float) per output frame."""
    cur = np.full(len(times), float(notes[0].midi))
    for i, n in enumerate(notes):
        cur[times >= n.t0 - (o["port_pre"] if i else 0)] = n.midi
    # smooth transitions between consecutive notes
    for i in range(1, len(notes)):
        a, b = notes[i - 1].midi, notes[i].midi
        if a == b:
            continue
        x = notes[i].x or {}
        pre = x.get("port_pre", o["port_pre"])
        post = x.get("port_post", o["port_post"])
        t0, t1 = notes[i].t0 - pre, notes[i].t0 + post
        m = (times >= t0) & (times < t1 + 0.12)
        u = np.clip((times[m] - t0) / (t1 - t0), 0, 1)
        s = 0.5 - 0.5 * np.cos(np.pi * u)
        val = a + (b - a) * s
        if b > a and o["overshoot"]:
            v = np.clip((times[m] - t1) / 0.12, 0, 1)
            val = val + np.sign(b - a) * o["overshoot"] / 100 * np.sin(np.pi * v) * (u >= 1)
        nxt = notes[i + 1].t0 - o["port_pre"] if i + 1 < len(notes) else 1e9
        mm = times[m] < nxt
        idx = np.where(m)[0][mm]
        cur[idx] = val[mm]
    # scoop at the phrase start, fall at the end
    n0, nl = notes[0], notes[-1]
    m = (times >= n0.t0 - 0.05) & (times < n0.t0 + o["scoop_time"])
    u = np.clip((times[m] - (n0.t0 - 0.05)) / (o["scoop_time"] + 0.05), 0, 1)
    cur[m] += o["scoop"] / 100 * (1 - u) ** 2 * ((n0.x or {}).get("scoop", 1.0))
    m = times > nl.t1 - o["fall_time"]
    u = np.clip((times[m] - (nl.t1 - o["fall_time"])) / o["fall_time"], 0, 1.5)
    cur[m] += o["fall"] / 100 * u ** 2 * ((nl.x or {}).get("fall", 1.0))
    # vibrato on long notes
    for i, n in enumerate(notes):
        x = n.x or {}
        depth = x.get("vib", 1.0) * o["vibrato_cents"]
        end = notes[i + 1].t0 - o["port_pre"] if i + 1 < len(notes) else n.t1
        start = n.t0 + x.get("vib_after", o["vibrato_after"])
        if depth <= 0 or end - start < 0.12:
            continue
        m = (times >= start) & (times < end)
        tt = times[m] - start
        env = np.clip(tt / o["vibrato_fade"], 0, 1) * np.clip((end - times[m]) / 0.06, 0, 1)
        rate = x.get("vib_rate", o["vibrato_rate"]) * (1 + 0.04 * np.sin(2 * np.pi * 0.7 * tt))
        cur[m] += depth / 100 * env * np.sin(2 * np.pi * np.cumsum(rate) * FP / 1000)
    return cur


def render_phrase(notes: list[VNote], vb: Voicebank, o: dict, fs_out: int, tail: bool = True):
    """Synthesise one phrase; returns (start_time_s, mono float32 at fs_out)."""
    import pyworld as pw
    pieces = _plan(notes, vb, o, tail=tail)
    t_start = min(p.s0 for p in pieces) - 0.01
    t_end = max(p.s1 for p in pieces) + 0.02
    nfr = int(math.ceil((t_end - t_start) / (FP / 1000)))
    times = t_start + np.arange(nfr) * FP / 1000
    fs = analyse(pieces[0].oto.wav)[3]
    nbin = analyse(pieces[0].oto.wav)[1].shape[1]
    SP = np.zeros((nfr, nbin))
    AP = np.zeros((nfr, nbin))
    VO = np.zeros(nfr)            # voiced weight
    JIT = np.zeros(nfr)           # sample's own pitch wobble (cents)
    W = np.zeros(nfr)
    for k, p in enumerate(pieces):
        f0, sp, ap, _ = analyse(p.oto.wav)
        total = len(f0) * FP / 1000
        m = (times >= p.s0) & (times < p.s1)
        if not m.any():
            continue
        st = _sample_times(p, times[m] - p.s0, total)
        idx = st / (FP / 1000)
        s_sp = _interp_frames(np.log(np.maximum(sp, 1e-16)), idx)
        s_ap = _interp_frames(ap, idx)
        s_f0 = f0[np.clip(np.round(idx).astype(int), 0, len(f0) - 1)]
        # crossfade weights: rise over this piece's overlap, fall over the next one's
        w = np.ones(m.sum())
        tt = times[m]
        if k > 0 and p.ov > 0:
            w *= np.clip((tt - p.s0) / max(p.ov, 0.012), 0, 1)
        if k + 1 < len(pieces):
            q = pieces[k + 1]
            w *= np.clip((p.s1 - tt) / max(p.s1 - q.s0, 0.012), 0, 1)
        w = np.maximum(w, 1e-4) * p.gain
        SP[m] += w[:, None] * s_sp
        AP[m] += w[:, None] * s_ap
        VO[m] += w * (s_f0 > 0)
        voiced = s_f0 > 0
        if voiced.sum() > 8:
            c = 1200 * np.log2(np.where(voiced, s_f0, 1) / np.median(s_f0[voiced]))
            c = np.where(voiced, c, 0)
            from scipy.ndimage import uniform_filter1d
            wob = c - uniform_filter1d(c, 20)
            JIT[m] += w * np.clip(wob, -25, 25)
        W[m] += w
    live = W > 1e-6
    SP[live] /= W[live, None]
    AP[live] /= W[live, None]
    VO[live] /= W[live]
    JIT[live] /= W[live]
    amp = np.clip(W, 0, None)  # piece gains, with fades at the phrase edges
    # formant shift: read the envelope at f / factor
    if o["formant"]:
        fac = 2 ** (o["formant"] / 12)
        bins = np.arange(nbin)
        src = np.clip(bins / fac, 0, nbin - 1)
        SP = np.stack([np.interp(src, bins, row) for row in SP])
    sp_lin = np.exp(SP)
    sp_lin[~live] = 1e-12
    AP = np.clip(AP + o["breathy"] * (1 - AP) * 0.5, 0.0, 1.0)
    AP[~live] = 1.0
    midi = _pitch_curve(notes, times, o) + o["jitter"] * JIT / 100
    f0 = 440.0 * 2 ** ((midi - 69) / 12)
    f0[(VO < 0.5) | ~live] = 0.0
    y = pw.synthesize(np.ascontiguousarray(f0), np.ascontiguousarray(sp_lin),
                      np.ascontiguousarray(AP), fs, FP)
    # amplitude envelope: per-frame piece gain, release at the end
    env = np.interp(np.arange(len(y)) / fs, np.arange(nfr) * FP / 1000, np.minimum(amp, 4))
    rel = o["release"]
    tail_t = (np.arange(len(y)) / fs + t_start) - (max(p.s1 for p in pieces) - rel)
    env *= np.clip(1 - tail_t / max(rel, 1e-3), 0, 1)
    y = y * env
    if fs != fs_out:
        from scipy.signal import resample_poly
        g = math.gcd(fs, fs_out)
        y = resample_poly(y, fs_out // g, fs // g)
    return t_start, y.astype(np.float32)


def phrases(notes: list[VNote], gap: float) -> list[list[VNote]]:
    out: list[list[VNote]] = []
    for n in sorted(notes, key=lambda n: n.t0):
        if out and n.t0 - out[-1][-1].t1 < gap:
            prev = out[-1][-1]
            prev.t1 = min(prev.t1, n.t0) if n.t0 > prev.t0 else prev.t1
            out[-1].append(n)
        else:
            out.append([n])
    return out


def render(notes: list[VNote], root: Path, opts: dict, n_samples: int, fs_out: int) -> np.ndarray:
    o = {**DEFAULTS, **(opts or {})}
    vb = bank(root)
    ph = phrases(notes, o["gap"])
    # analyse every sample the song needs up front, in parallel
    wavs = []
    tails = [i + 1 == len(ph) or ph[i + 1][0].t0 - p[-1].t1 > o["tail_gap"] for i, p in enumerate(ph)]
    for p, tl in zip(ph, tails):
        try:
            wavs += [pc.oto.wav for pc in _plan(p, vb, o, light=True, tail=tl)]
        except KeyError:
            pass
    prefetch(wavs)
    out = np.zeros(n_samples, dtype=np.float32)
    for p, tl in zip(ph, tails):
        t0, y = render_phrase(p, vb, o, fs_out, tail=tl)
        a = int(round(t0 * fs_out))
        if a < 0:
            y, a = y[-a:], 0
        b = min(n_samples, a + len(y))
        if b > a:
            out[a:b] += y[: b - a]
    if o["breath_db"] is not None:
        _breaths(ph, vb, o, out, fs_out)
    out *= 10 ** (o["gain_db"] / 20)
    return out


BREATH_ALIASES = ("breath1", "breath", "- br1", "br1", "br", "息")


def _breaths(ph: list[list[VNote]], vb: Voicebank, o: dict, out: np.ndarray, fs_out: int):
    """Raw breath samples (no resynthesis) ending where each phrase's first sample starts."""
    oto = next((vb.oto[a] for a in BREATH_ALIASES if a in vb.oto), None)
    if oto is None:
        return
    x, fs = sf.read(oto.wav, dtype="float32", always_2d=True)
    x = x[:, 0]
    a = int(oto.offset / 1000 * fs)
    b = int((oto.offset - oto.cutoff) / 1000 * fs) if oto.cutoff < 0 else len(x) - int(oto.cutoff / 1000 * fs)
    br = x[a:max(b, a + int(0.1 * fs))]
    br = br[: int(0.45 * fs)]
    if fs != fs_out:
        from scipy.signal import resample_poly
        g = math.gcd(fs, fs_out)
        br = resample_poly(br, fs_out // g, fs // g).astype(np.float32)
    n = len(br)
    br *= np.minimum(1, np.minimum(np.arange(n) / (0.04 * fs_out), (n - np.arange(n)) / (0.03 * fs_out)))
    br *= 10 ** (o["breath_db"] / 20)
    prev_end = -1e9
    for p in ph:
        first = _plan(p[:1], vb, o, light=True, tail=False)[0]
        start = first.s0 - n / fs_out + 0.02
        if p[0].t0 - prev_end > o["breath_gap"] and start > prev_end + 0.05:
            i = int(round(start * fs_out))
            if i >= 0 and i + n <= len(out):
                out[i:i + n] += br
        prev_end = p[-1].t1
