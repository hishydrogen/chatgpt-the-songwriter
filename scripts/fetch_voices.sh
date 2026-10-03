#!/usr/bin/env bash
# Download the UTAU voicebanks sung by songwriter/voice.py into $LIB_DIR/voice.
# Japanese banks only (the official sites and Hugging Face are blocked from the container;
# these GitHub mirrors are not). Usage: scripts/fetch_voices.sh [name ...]
# Terms differ per bank - read docs/vocal-songwriting.md ("Voicebanks") before releasing.
set -uo pipefail
LIB_DIR="${SFZ_LIB_DIR:-$(cd "$(dirname "$0")/.." && pwd)/libs}"
VOICE="$LIB_DIR/voice"
mkdir -p "$VOICE"

# name|git url  (unchanged mirrors by oxygen-dioxide; each repo carries its license.md)
BANKS=(
  "hitsuboku-kumi-ja-act4|https://github.com/oxygen-dioxide/hitsuboku-kumi-ja-act4"
  "milk-ja|https://github.com/oxygen-dioxide/milk-ja"
  "hikari-one-crystal-ja|https://github.com/oxygen-dioxide/hikari-one-crystal-ja"
  "viki-hopper-ja|https://github.com/oxygen-dioxide/viki-hopper-ja"
)

want=("$@")
pick() { ((${#want[@]} == 0)) || [[ " ${want[*]} " == *" $1 "* ]]; }

for entry in "${BANKS[@]}"; do
  name="${entry%%|*}"; url="${entry#*|}"
  pick "$name" || continue
  dest="$VOICE/$name"
  if [[ -f "$dest/.fetched" ]]; then echo "skip $name"; continue; fi
  rm -rf "$dest"
  echo "fetch $name"
  if git clone -q --depth 1 "$url" "$dest"; then
    (cd "$dest" && git rev-parse HEAD > .fetched)
    rm -rf "$dest/.git"
    echo "  ok $(du -sh "$dest" | cut -f1)"
  else
    echo "  FAILED $name"
  fi
done

# 足立レイ (Adachi Rei): the official zip ships inside onjmin/koe (sparse checkout of one
# file), file names in the zip are Shift-JIS.
if pick adachi-rei; then
  dest="$VOICE/adachi-rei"
  if [[ -f "$dest/.fetched" ]]; then echo "skip adachi-rei"; else
    echo "fetch adachi-rei"
    tmp="$(mktemp -d)"
    if git clone -q --depth 1 --filter=blob:none --sparse https://github.com/onjmin/koe "$tmp/koe" \
       && git -C "$tmp/koe" sparse-checkout set --no-cone 'src/utautts/go-src/UtauTTS/voice/*'; then
      rm -rf "$dest"; mkdir -p "$dest"
      python3 - "$tmp/koe/src/utautts/go-src/UtauTTS/voice" "$dest" <<'EOF'
import sys, zipfile
from pathlib import Path
src, dest = Path(sys.argv[1]), Path(sys.argv[2])
z = zipfile.ZipFile(next(src.glob("*.zip")))
for i in z.infolist():
    if i.is_dir():
        continue
    name = i.filename if i.flag_bits & 0x800 else i.filename.encode("cp437").decode("cp932")
    out = dest / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(z.read(i))
EOF
      echo "onjmin/koe $(git -C "$tmp/koe" rev-parse HEAD)" > "$dest/.fetched"
      echo "  ok $(du -sh "$dest" | cut -f1)"
    else
      echo "  FAILED adachi-rei"
    fi
    rm -rf "$tmp"
  fi
fi
