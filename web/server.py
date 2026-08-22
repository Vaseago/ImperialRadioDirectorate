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


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracks = scan_library_dirs(config.MUSIC_LIBRARY_DIRS)
    app.state.tracks = {t.id: t for t in tracks}
    yield


app = FastAPI(title="Imperial Radio Directorate (web)", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=os.path.join(_WEB_DIR, "static")), name="static")
app.include_router(pages.router)
app.include_router(library.router)
