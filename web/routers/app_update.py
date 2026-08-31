"""
web/routers/app_update.py

"Check for App Update" - git-pull-based self-update for this app's own
source, since it runs from a live checkout rather than a packaged
installer. Ported from the sibling Imperial apps' identical routers
(2026-08-30, once IRD joined the Pi's always-on supervisor setup
alongside IID/ISD/ILD - user's own request: "lets get an update button
on it that auto restarts the app [server]").

Self-restart after pulling is conditional - see _SUPERVISED below. On
the Pi (this app spawned as a child of _supervisor/supervisor.py) a
pull is followed by a real, graceful self-exit, and supervisor.py's own
restart-on-exit poll loop relaunches this app fresh from the now-updated
code within a couple seconds - no SSH/manual restart needed. Everywhere
else (the desktop shell, a bare `python3 ird_web_main.py`) nothing about
this changes: backend (.py) changes still need a real restart to load
(Python modules import once at process startup), and there's no safety
net to catch a self-exit, so the frontend just tells the user a restart
is needed instead.
"""

import asyncio
import os
import signal
import sys

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from web.security import require_same_origin_header
from web.state.app_update import check_for_update, pull_update

router = APIRouter(prefix="/api/app-update")

# check_for_update()/pull_update() both run `git` against config.BASE_DIR -
# meaningless in a packaged build, where BASE_DIR is wherever PyInstaller
# unpacked this exe, not a git checkout with an "origin" remote. Without
# this gate a packaged tester clicking the button just gets a confusing
# 502 ("git fetch" failing) instead of a clear "not available here"
# message. Frozen-ness can't change at runtime, so this is computed once.
_AVAILABLE = not getattr(sys, "frozen", False)

# Set ONLY by _supervisor/supervisor.py's own _start(), on every child it
# spawns (IRD included, since it's cloned/run there like any other
# Imperial app) - nowhere else in this codebase (or any sibling app's)
# ever sets this. This is the single condition gating self-restart:
# present only for a Pi-hosted, supervisor-managed process, which is the
# only deployment with an existing auto-restart-on-exit safety net (see
# supervisor.py's own poll loop). Computed once at import time, same
# posture as _AVAILABLE above - the env var can't change during this
# process's own lifetime.
_SUPERVISED = os.environ.get("SUPERVISED_RESTART_OK") == "1"


async def _self_restart_after_delay() -> None:
    """Scheduled via BackgroundTasks, which Starlette only runs AFTER the
    response has been handed to the ASGI transport - guarantees the
    client already has its response before this process starts exiting.
    A real SIGTERM (not os._exit()) so uvicorn's own already-correct
    graceful-shutdown path runs - the same path an operator's Ctrl+C
    already takes today - reusing proven behavior, not reimplementing
    it. The short sleep is just breathing room for the response to
    actually flush over the socket before the process starts tearing
    down."""
    await asyncio.sleep(1.0)
    os.kill(os.getpid(), signal.SIGTERM)


@router.get("/status")
async def get_status(request: Request):
    """Lets a freshly (re)loaded page find out immediately whether an
    update is already pending, without re-running the check. `available`
    lets the frontend hide the whole control for a packaged build rather
    than showing a button that can only ever fail."""
    return {"pending": request.app.state.pending_app_update, "available": _AVAILABLE}


@router.post("/check", dependencies=[Depends(require_same_origin_header)])
async def check(request: Request):
    if not _AVAILABLE:
        raise HTTPException(status_code=404, detail="App update via git pull is not available in a packaged build.")
    app = request.app
    loop = asyncio.get_event_loop()
    try:
        pending = await loop.run_in_executor(None, check_for_update)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Update check failed: {e}")
    app.state.pending_app_update = pending
    return {"pending": pending}


@router.post("/pull", dependencies=[Depends(require_same_origin_header)])
async def pull(request: Request, background_tasks: BackgroundTasks):
    """Only allowed once a check has actually flagged something pending -
    never a standalone "just pull whatever's newest" action."""
    if not _AVAILABLE:
        raise HTTPException(status_code=404, detail="App update via git pull is not available in a packaged build.")
    app = request.app
    if app.state.pending_app_update is None:
        raise HTTPException(status_code=400, detail="No pending update - check first.")
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, pull_update)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Update failed: {e}")
    app.state.pending_app_update = None
    if _SUPERVISED:
        background_tasks.add_task(_self_restart_after_delay)
    return {"ok": True, "restart_required": True, "self_restarting": _SUPERVISED, **result}
