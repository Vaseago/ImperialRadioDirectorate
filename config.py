"""
config.py

Central settings. Unlike Imperial Industry/Skill/Logistic Directorate's
own config.py, this app has ZERO EVE ESI dependency and ZERO SDE
dependency - no SDE_PATH, no WEB_ESI_CLIENT_ID/WEB_ESI_CALLBACK_URL/
WEB_ACCOUNTS_DIR, no ESI_SCOPES. It's a local media player, themed
around EVE, with no EVE Online API dependency at all - deliberately
smaller than its siblings' config.py, not an oversight.
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DATA_DIR is where writable, per-machine local state lives - a much
# smaller surface than the sibling apps' own DATA_DIR, since the only
# thing that actually lives here is config_overrides.json (no ESI
# tokens, no SDE, no saved plans). IRD_DATA_DIR overrides for the
# desktop shell, same override-precedence pattern as every sibling
# app's DATA_DIR.
if "IRD_DATA_DIR" in os.environ:
    DATA_DIR = os.environ["IRD_DATA_DIR"]
elif getattr(sys, "frozen", False):
    DATA_DIR = os.path.join(os.environ["PROGRAMDATA"], "Imperial Radio Directorate")
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")

# ---- Music library ----
# Deliberately NOT DATA_DIR-derived - read-only, shared identically by
# the always-on web service and any desktop shell instance, same
# reasoning as the sibling apps' own SHARED_SDE_DIR: nothing here ever
# WRITES to the library, so there's no whole-file-save race and no
# per-client-id credential to isolate - the two real reasons the
# sibling apps isolate DATA_DIR per-instance at all. A desktop shell
# instance sees the exact SAME music folder as the web service, by
# design, not a duplicate.
MUSIC_LIBRARY_DIR = os.environ.get("IRD_MUSIC_DIR", os.path.join(BASE_DIR, "music_library"))
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".ogg", ".oga", ".flac", ".wav", ".m4a", ".mp4", ".aac"}
# .mp4 added 2026-08-23 - several AI music generators (the user's own
# real case) export audio-only tracks in a plain .mp4 container rather
# than .m4a, even though it's the exact same underlying MP4 container
# format mutagen already reads via the same EasyMP4 class .m4a uses -
# verified directly against a real generated file (tags/duration read
# back correctly). See web/routers/library.py's own comment for the one
# other place this needed a matching fix (the stream endpoint's MIME
# type guess).

# ---- web/ (browser-based companion, also the UI the desktop shell wraps) ----
WEB_HOST = "0.0.0.0"  # bind all interfaces - matches sibling apps, reachable from LAN if ever wanted later

# Next unused slot after IID (8000/8010), ILD (8020/8030), ISD
# (8040/8050) - verified unused against the whole Imperial Apps tree.
WEB_PORT = int(os.environ.get("IRD_WEB_PORT", 8060))


def _load_config_overrides(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


# Additional music folders (e.g. a future folder of legitimately-
# purchased EVE soundtrack files) are added here, not by editing this
# git-tracked file - same config_overrides.json mechanism the sibling
# apps use for their own per-machine local overrides. Example contents:
#   {"extra_music_dirs": ["D:/EVE Bandcamp Purchases"]}
_CONFIG_OVERRIDES_PATH = os.path.join(DATA_DIR, "config_overrides.json")
_config_overrides = _load_config_overrides(_CONFIG_OVERRIDES_PATH)
MUSIC_LIBRARY_DIRS = [MUSIC_LIBRARY_DIR] + list(_config_overrides.get("extra_music_dirs", []))
