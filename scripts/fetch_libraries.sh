#!/usr/bin/env bash
# Download the curated free/open-source SFZ sample libraries into $LIB_DIR.
# Samples are big, so they live outside git. Usage: scripts/fetch_libraries.sh [name ...]
set -uo pipefail
LIB_DIR="${SFZ_LIB_DIR:-$(cd "$(dirname "$0")/.." && pwd)/libs}"
mkdir -p "$LIB_DIR"
exec 9>"$LIB_DIR/.fetch.lock"
flock 9

# name|git url
LIBS=(
  # Pianos
  "SalamanderGrandPiano|https://github.com/sfzinstruments/SalamanderGrandPiano"
  "MaestroConcertGrand|https://github.com/sfzinstruments/MatsHelgesson.MaestroConcertGrandPiano"
  "SplendidGrandPiano|https://github.com/sfzinstruments/SplendidGrandPiano"
  # Electric pianos
  "jRhodes3d|https://github.com/sfzinstruments/jlearman.jRhodes3d"
  "GregSullivan-EPianos|https://github.com/sfzinstruments/GregSullivan.E-Pianos"
  # Drums
  "VirtuosityDrums|https://github.com/sfzinstruments/virtuosity_drums"
  "DRSKit|https://github.com/sfzinstruments/DrumGizmo.DRSKit"
  "SMDrums|https://github.com/sfzinstruments/SMDrums"
  # Bass
  "BlackAndBlueBasses|https://github.com/sfzinstruments/karoryfer.black-and-blue-basses"
  "Meatbass|https://github.com/sfzinstruments/karoryfer.meatbass"
  "DoubleBass|https://github.com/sfzinstruments/dsmolken.double-bass"
  # Guitars
  "BlackAndGreenGuitars|https://github.com/sfzinstruments/karoryfer.black-and-green-guitars"
  "Emilyguitar|https://github.com/sfzinstruments/karoryfer.emilyguitar"
  "DamiensFunkyGuitar|https://github.com/sfzinstruments/DamiensFunkyGuitar"
  # Orchestral / solo
  "VSCO2CE|https://github.com/sgossner/VSCO-2-CE"
  "BigcatCello|https://github.com/sfzinstruments/karoryfer-bigcat.cello"
  "SoloSax|https://github.com/sfzinstruments/MTG.SoloSax"
  # General MIDI fallback in SFZ
  "SFZ-GM-Bank|https://github.com/sfzinstruments/Discord-SFZ-GM-Bank"
)

want=("$@")
failed=0
for entry in "${LIBS[@]}"; do
  name="${entry%%|*}"; url="${entry#*|}"
  if ((${#want[@]})) && [[ ! " ${want[*]} " == *" $name "* ]]; then continue; fi
  dest="$LIB_DIR/$name"
  if [[ -f "$dest/.fetched" ]]; then echo "skip $name"; continue; fi
  rm -rf "$dest"
  echo "fetch $name"
  if GIT_LFS_SKIP_SMUDGE=0 git clone -q --depth 1 "$url" "$dest"; then
    if (cd "$dest" && git lfs pull && git lfs fsck && git rev-parse HEAD > .fetched); then
      rm -rf "$dest/.git"   # halve disk usage; commit hash kept in .fetched
      echo "  ok $(du -sh "$dest" | cut -f1)"
    else
      echo "  FAILED $name (sample checkout incomplete)" >&2
      failed=1
    fi
  else
    echo "  FAILED $name"
    failed=1
  fi
done
exit "$failed"
