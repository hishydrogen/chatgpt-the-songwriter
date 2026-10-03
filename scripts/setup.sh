#!/usr/bin/env bash
# Rebuild the whole studio in a fresh Ubuntu 24.04 container (~20-30 min, mostly Surge XT).
# Idempotent: finished steps are skipped. Usage: scripts/setup.sh [--no-libs]
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="${BUILD_DIR:-/tmp/songwriter-build}"
SURGE_REV=348cfb3d0bd081797cfd6505d5f8d3ffd6f34c49
SFIZZ_REV=f5c6e29f23b8057867c08e88f5f6ac6738baa30b
JOBS=$(nproc)
mkdir -p "$BUILD"
log() { printf '\n== %s\n' "$*"; }

log "apt: plugins, soundfonts, build deps"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq || true
apt-get install -y -q --no-install-recommends \
  lsp-plugins-vst3/noble-backports lsp-plugins-r3d-glx/noble-backports \
  dragonfly-reverb-vst3 zam-plugins dpf-plugins-vst3 guitarix-lv2 liblilv-dev lv2-dev \
  fluidsynth fluid-soundfont-gm musescore-general-soundfont sox ffmpeg \
  cmake ninja-build build-essential pkg-config git git-lfs \
  libsndfile1-dev libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxcomposite-dev \
  libxext-dev libcairo2-dev libxkbcommon-x11-dev libxcb-cursor-dev libxcb-keysyms1-dev \
  libxcb-util-dev libfreetype-dev libfontconfig1-dev libasound2-dev libjack-jackd2-dev \
  libcurl4-openssl-dev xvfb xdotool scrot >/dev/null

log "python packages"
python3 -m pip install -q -r "$REPO/requirements.txt"

if ! command -v lv2host >/dev/null; then
  log "build lv2host (offline LV2 host for the guitarix amp models)"
  gcc -O2 -o /usr/local/bin/lv2host "$REPO/scripts/lv2host.c" $(pkg-config --cflags --libs lilv-0 sndfile) -lm
fi

if ! command -v sfizz_render >/dev/null || ! sfizz_render --help 2>&1 | grep -q '32-bit float WAV'; then
  log "build sfizz_render with float output (no early PCM quantization or clipping)"
  [ -d "$BUILD/sfizz" ] || git clone -q --recurse-submodules https://github.com/sfztools/sfizz.git "$BUILD/sfizz"
  git -C "$BUILD/sfizz" checkout -q "$SFIZZ_REV" && git -C "$BUILD/sfizz" submodule update -q --init --recursive
  if git -C "$BUILD/sfizz" apply --check "$REPO/scripts/sfizz-float-output.patch" 2>/dev/null; then
    git -C "$BUILD/sfizz" apply "$REPO/scripts/sfizz-float-output.patch"
  else
    git -C "$BUILD/sfizz" apply --reverse --check "$REPO/scripts/sfizz-float-output.patch"
  fi
  cmake -S "$BUILD/sfizz" -B "$BUILD/sfizz/build" -G Ninja -DCMAKE_BUILD_TYPE=Release -DSFIZZ_JACK=OFF \
    -DSFIZZ_RENDER=ON -DSFIZZ_TESTS=OFF -DSFIZZ_DEMOS=OFF -DSFIZZ_BENCHMARKS=OFF -DSFIZZ_DEVTOOLS=OFF >/dev/null
  ninja -C "$BUILD/sfizz/build" -j"$JOBS" sfizz_render >/dev/null
  cp "$BUILD/sfizz/build/library/bin/sfizz_render" /usr/local/bin/
fi

if ! python3 -c "import surgepy; surgepy.createSurge(48000).setTempo" 2>/dev/null; then
  log "build Surge XT (python bindings + VST3)"
  [ -d "$BUILD/surge" ] || git clone -q https://github.com/surge-synthesizer/surge.git "$BUILD/surge"
  git -C "$BUILD/surge" checkout -q "$SURGE_REV"
  git -C "$BUILD/surge" submodule update -q --init --recursive --depth 1
  git -C "$BUILD/surge" apply --check "$REPO/scripts/surgepy-settempo.patch" 2>/dev/null \
    && git -C "$BUILD/surge" apply "$REPO/scripts/surgepy-settempo.patch"
  PY=$(command -v python3)
  cmake -S "$BUILD/surge" -B "$BUILD/surge/build" -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DSURGE_BUILD_LV2=OFF -DSURGE_SKIP_STANDALONE=TRUE -DSURGE_BUILD_TESTRUNNER=OFF \
    -DSURGE_BUILD_PYTHON_BINDINGS=ON -DPython_EXECUTABLE="$PY" -DPYTHON_EXECUTABLE="$PY" >/dev/null
  ninja -C "$BUILD/surge/build" -j"$JOBS" surgepy surge-xt_VST3 surge-fx_VST3 >/dev/null
  SITE=$("$PY" -c "import site; print(site.getsitepackages()[0])")
  cp "$BUILD"/surge/build/src/surge-python/surgepy*.so "$SITE/"
  mkdir -p /usr/local/share/surge-xt /usr/local/lib/vst3
  cp -r "$BUILD/surge/resources/data/." /usr/local/share/surge-xt/
  cp -r "$BUILD"/surge/build/surge_xt_products/*.vst3 /usr/local/lib/vst3/
fi

if [[ "${1:-}" != "--no-libs" ]]; then
  log "sample libraries"
  "$REPO/scripts/fetch_libraries.sh"
  python3 "$REPO/scripts/build_vsco_sfz.py"
  log "baked vintage instruments (LinnDrum-style kit, Mirage/Fairlight sounds)"
  python3 "$REPO/scripts/build_nasty_palette.py"
  log "self-made electronic kit (drums.club)"
  python3 "$REPO/scripts/build_club_kit.py"
  log "DI guitar for amp models (guitar.emily_di)"
  python3 "$REPO/scripts/build_guitar_sfz.py"
  log "UTAU voicebanks for songwriter/voice.py (~2.6 GB)"
  "$REPO/scripts/fetch_voices.sh"
fi

log "check"
cd "$REPO" && python3 -m songwriter instruments | grep -c "^ " | xargs echo "instruments available:"
