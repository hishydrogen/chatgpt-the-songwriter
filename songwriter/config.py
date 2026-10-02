"""Paths and global settings. Override any path with an environment variable."""
import os
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent

# Sample libraries fetched by scripts/fetch_libraries.sh (kept out of git).
LIB_DIR = Path(os.environ.get("SFZ_LIB_DIR", REPO_DIR / "libs"))

# Surge XT resources (factory + 3rd party patches, wavetables).
SURGE_DATA_DIR = Path(os.environ.get("SURGE_DATA_DIR", "/usr/local/share/surge-xt"))

VST3_DIRS = [Path("/usr/lib/vst3"), Path("/usr/local/lib/vst3"), Path.home() / ".vst3"]
LSP_VST3 = Path("/usr/lib/vst3/lsp-plugins.vst3")

SFIZZ_RENDER = os.environ.get("SFIZZ_RENDER", "sfizz_render")

# Internal processing format. Everything is float32 stereo at this rate.
SAMPLE_RATE = 48000

# Default delivery targets (streaming-friendly).
TARGET_LUFS = -14.0
TRUE_PEAK_CEILING_DB = -1.0
