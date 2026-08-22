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

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

import config
from library.scanner import scan_library_dirs
from web.security import require_same_origin_header

router = APIRouter(prefix="/api/library")


def _track_sort_key(track):
    return (track.artist.lower(), track.album.lower(), track.title.lower())


@router.get("/tracks")
async def list_tracks(request: Request):
    tracks = sorted(request.app.state.tracks.values(), key=_track_sort_key)
    return [
        {
            "id": t.id,
            "title": t.title,
            "artist": t.artist,
            "album": t.album,
            "duration_seconds": t.duration_seconds,
        }
        for t in tracks
    ]


@router.get("/tracks/{track_id}/stream")
async def stream_track(track_id: str, request: Request):
    track = request.app.state.tracks.get(track_id)
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    media_type = mimetypes.guess_type(track.path)[0] or "audio/mpeg"
    return FileResponse(track.path, media_type=media_type)


@router.post("/rescan", dependencies=[Depends(require_same_origin_header)])
async def rescan_library(request: Request):
    tracks = scan_library_dirs(config.MUSIC_LIBRARY_DIRS)
    request.app.state.tracks = {t.id: t for t in tracks}
    return {"track_count": len(tracks)}
