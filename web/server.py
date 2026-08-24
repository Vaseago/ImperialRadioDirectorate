"""
web/server.py

FastAPI app for Imperial Radio Directorate's web companion (also the UI
the desktop shell wraps). Much smaller than the sibling apps' own
web/server.py - no SDE, no ESI, no sibling-notification wiring, since
this app has none of those dependencies.
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import config
from library.scanner import scan_library_dirs
from web.routers import library, pages

# See web/routers/pages.py's matching comment - same __file__-relative-
# breaks-once-frozen fix as the sibling apps.
if getattr(sys, "frozen", False):
    _WEB_DIR = os.path.join(os.path.dirname(sys.executable), "web")
else:
    _WEB_DIR = os.path.dirname(os.path.abspath(__file__))


class _NoCacheStaticFiles(StaticFiles):
    """Plain StaticFiles serves JS/CSS with normal browser caching, which
    silently bit this app for real during frontend development
    (2026-08-23): repeated `<script src="/static/js/app.js">` loads in
    the same browser tab kept serving a stale cached copy after the file
    on disk changed, so a real code fix appeared to do nothing - the
    exact class of bug the sibling apps' own content-hashed
    `static_version` mechanism exists to avoid (see
    ../SHARED_ARCHITECTURE.md and IID's web/static_version.py). IRD is a
    single-user desktop app, not a multi-device shared web service, so
    the sibling apps' more elaborate content-hash-and-URL-bust system
    would be disproportionate scope here - a flat `no-store` on every
    static response is the right-sized fix for a dev tool nobody else's
    browser needs to cache."""

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-store"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracks = scan_library_dirs(config.MUSIC_LIBRARY_DIRS)
    app.state.tracks = {t.id: t for t in tracks}
    commercials = scan_library_dirs(config.COMMERCIAL_DIRS)
    app.state.commercials = {t.id: t for t in commercials}
    yield


app = FastAPI(title="Imperial Radio Directorate (web)", lifespan=lifespan)
app.mount("/static", _NoCacheStaticFiles(directory=os.path.join(_WEB_DIR, "static")), name="static")
app.include_router(pages.router)
app.include_router(library.router)
