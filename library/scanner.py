"""
library/scanner.py

Scans configured music-library folders for audio files, no database -
app.state.tracks is populated fresh at server startup (and on an
explicit "Rescan Library" action), matching the sibling apps' own "no
over-engineered persistence" posture. A personal music library trivially
fits in memory; the filesystem itself is the source of truth.
"""

import hashlib
import os

import mutagen

import config
from library.models import Track


def _fallback_title(filename: str) -> str:
    """Filenames become a passable title when tags are missing/unreadable -
    the app's own "reconstructed audio, fragmentary records" framing
    paying off functionally, not just cosmetically."""
    name = os.path.splitext(filename)[0]
    return name.replace("_", " ").replace("-", " ").strip()


def _track_id(relative_path: str) -> str:
    # Stable across rescans of an unchanged file (so /stream URLs don't
    # break on every rescan); changes only if the file is renamed/moved -
    # an accepted, documented simplification, not a bug.
    return hashlib.sha1(relative_path.encode("utf-8")).hexdigest()[:16]


def _station_name(relative_path: str) -> str:
    # "Station" is folder-per-station: a track's top-level subfolder
    # (relative to its library dir) is its station, however deep the
    # file actually sits within it. A track with no subfolder (sitting
    # loose at the library root - the common case today, before any
    # real curation) falls into a shared "General" catch-all rather
    # than being silently invisible.
    parts = relative_path.split(os.sep)
    if len(parts) <= 1:
        return "General"
    return parts[0].replace("_", " ").replace("-", " ").strip().title()


def _read_track(path: str, library_dir: str) -> Track | None:
    try:
        stat = os.stat(path)
        relative_path = os.path.relpath(path, library_dir)
        track_id = _track_id(relative_path)
        filename = os.path.basename(path)

        title = None
        artist = ""
        album = ""
        duration_seconds = 0.0

        audio = mutagen.File(path, easy=True)
        if audio is not None:
            if audio.tags:
                title = (audio.tags.get("title") or [None])[0]
                artist = (audio.tags.get("artist") or [""])[0]
                album = (audio.tags.get("album") or [""])[0]
            if audio.info is not None and hasattr(audio.info, "length"):
                duration_seconds = float(audio.info.length)

        if not title:
            title = _fallback_title(filename)

        return Track(
            id=track_id,
            title=title,
            artist=artist,
            album=album,
            duration_seconds=duration_seconds,
            path=path,
            library_dir=library_dir,
            mtime=stat.st_mtime,
            station=_station_name(relative_path),
        )
    except Exception:
        # One corrupt/unreadable file must never abort the whole scan -
        # matches character_data.py's per-section try/except philosophy
        # in the sibling apps.
        return None


def scan_library_dirs(dirs: list[str]) -> list[Track]:
    tracks: list[Track] = []
    for library_dir in dirs:
        if not os.path.isdir(library_dir):
            continue
        for root, _dirnames, filenames in os.walk(library_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in config.SUPPORTED_AUDIO_EXTENSIONS:
                    continue
                path = os.path.join(root, filename)
                track = _read_track(path, library_dir)
                if track is not None:
                    tracks.append(track)
    return tracks
