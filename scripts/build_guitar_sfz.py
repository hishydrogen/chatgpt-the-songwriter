#!/usr/bin/env python3
"""Rock guitar source for amp simulation: the Karoryfer "Emily" guitar (Epiphone, recorded
direct, royalty-free) as `guitar.emily_di`, with palm muting on CC70.

  python scripts/build_guitar_sfz.py   ->  libs/_generated/guitar.emily_di.sfz (+ .json)

The samples are a DI signal, so the song plays power chords and riffs into a real amp
model in the mix strip ("amp": guitarix gx_amp via scripts/lv2host, see songwriter.dsp.amp)
and the distortion sees the whole chord, as a real amp does.

CC70 = palm mute amount: 0 open, 127 fully muted (low-pass on the string, short release).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from songwriter import config  # noqa: E402

SRC = config.LIB_DIR / "Emilyguitar" / "emily_clean.sfz"
OUT = config.LIB_DIR / "_generated" / "guitar.emily_di.sfz"

HEADER = """// Emily guitar DI (Karoryfer Lecolds, royalty-free), for amp sims. CC70 = palm mute.
<control>
default_path=../Emilyguitar/
label_cc70=Palm mute
set_cc70=0

<global>
fil_type=lpf_2p
cutoff=9500
cutoff_oncc70=-4400
resonance=0
ampeg_release_oncc70=-0.17
volume_oncc70=-3
"""


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC} - run scripts/fetch_libraries.sh Emilyguitar")
    body = SRC.read_text()
    body = re.sub(r"sample=([^\n]+)", lambda m: "sample=" + m.group(1).strip().replace("\\", "/"), body)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HEADER + "\n" + body)
    OUT.with_suffix(".json").write_text(json.dumps({
        "desc": "Emily guitar recorded direct (Karoryfer, royalty-free): play it into an amp "
                "model with the strip's \"amp\" insert. CC70 = palm mute.",
        "range": [33, 89], "tail": 1.5}, indent=1))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
