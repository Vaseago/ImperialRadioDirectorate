"""
web/routers/library.py

The music library REST surface. GET /api/library/tracks/{id}/stream
uses plain FileResponse for Range-request support (seeking) - verified
directly against the installed Starlette version's real source
(starlette/responses.py), not assumed: FileResponse natively handles
single-range Range requests (206 Partial Content, Content-Range,
MalformedRangeHeader/RangeNotSatisfiable), so no hand-rolled Range
parsing is needed here.
"""

import mimetypes
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

import config
from library.scanner import scan_library_dirs
from web.security import require_same_origin_header

router = APIRouter(prefix="/api/library")

# .mp4 override, added 2026-08-23 alongside config.SUPPORTED_AUDIO_EXTENSIONS
# gaining .mp4 - Python's stdlib mimetypes module guesses "video/mp4" for
# this extension (verified directly), which is wrong for the real files
# this needs to serve: AI-generated tracks (the user's own real case)
# that are audio-only in intent but actually carry BOTH an H.264 video
# track and an AAC audio track in the container (confirmed by scanning
# the raw file for 'vide'/'soun' handler atoms - not just a cover-art
# image). An <audio> element still plays these fine either way (it
# decodes whichever track it needs, ignoring video), but the Content-Type
# header should still honestly say "audio", not "video".
_MIME_TYPE_OVERRIDES = {".mp4": "audio/mp4"}


def _track_sort_key(track):
    return (track.station.lower(), track.artist.lower(), track.album.lower(), track.title.lower())


def _serialize(t):
    return {
        "id": t.id,
        "title": t.title,
        "artist": t.artist,
        "album": t.album,
        "duration_seconds": t.duration_seconds,
        "station": t.station,
    }


@router.get("/tracks")
async def list_tracks(request: Request):
    tracks = sorted(request.app.state.tracks.values(), key=_track_sort_key)
    return [_serialize(t) for t in tracks]


@router.get("/commercials")
async def list_commercials(request: Request):
    # Same Track shape as /tracks (station is meaningless here and
    # ignored by the frontend) - a separate pool so ad-break selection
    # never has to filter station tracks out by name/convention.
    commercials = sorted(request.app.state.commercials.values(), key=_track_sort_key)
    return [_serialize(t) for t in commercials]


@router.get("/tracks/{track_id}/stream")
async def stream_track(track_id: str, request: Request):
    track = request.app.state.tracks.get(track_id) or request.app.state.commercials.get(track_id)
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    ext = os.path.splitext(track.path)[1].lower()
    media_type = _MIME_TYPE_OVERRIDES.get(ext) or mimetypes.guess_type(track.path)[0] or "audio/mpeg"
    return FileResponse(track.path, media_type=media_type)


@router.post("/rescan", dependencies=[Depends(require_same_origin_header)])
async def rescan_library(request: Request):
    tracks = scan_library_dirs(config.MUSIC_LIBRARY_DIRS)
    request.app.state.tracks = {t.id: t for t in tracks}
    commercials = scan_library_dirs(config.COMMERCIAL_DIRS)
    request.app.state.commercials = {t.id: t for t in commercials}
    return {"track_count": len(tracks), "commercial_count": len(commercials)}
