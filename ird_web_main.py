#!/usr/bin/env python3
"""Entry point: launches Imperial Radio Directorate's web app.

Runs as a single uvicorn worker process (same requirement as the
sibling apps: in-memory server state, app.state.tracks)."""

import uvicorn

import config

# Imported as a real object and passed directly to uvicorn.run() below,
# NOT the "web.server:app" string form - PyInstaller's static analysis
# can't see a module referenced solely by a runtime string, silently
# dropping the whole web/ package from a packaged build. This bit ISD
# and ILD for real once already (see CROSS_APP_ISSUES.md) - IRD uses
# the object form from day one.
from web.server import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.WEB_HOST,
        port=config.WEB_PORT,
        reload=False,
    )
