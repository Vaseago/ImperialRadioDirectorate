"""
web/state/app_update.py

Git-pull-based self-update: this app runs from a live git checkout, not
a packaged installer, so "update" means pulling the latest commits from
GitHub - same "check and ask" two-step flow ported from the sibling
Imperial apps' own identical modules (checking never pulls anything on
its own). Backend (.py) changes need a process restart to actually take
effect after pulling (frontend HTML/JS/CSS already applies on the next
request, no restart needed) - this module itself never restarts
anything (stays a pure git-pull function, no process-lifecycle
knowledge). Whether a restart happens automatically after a pull is
entirely the CALLER's decision - see web/routers/app_update.py's own
docstring: on the Pi specifically (gated by SUPERVISED_RESTART_OK,
already set unconditionally by _supervisor/supervisor.py for every app
it spawns, IRD included since 2026-08-30), the router schedules a real
self-restart after a successful pull; everywhere else (desktop shell, a
bare python run) it still just reports that a restart is recommended
and leaves the actual restart to the user.
"""

import subprocess

import config

_GIT_TIMEOUT_SECONDS = 30


def _run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=config.BASE_DIR, capture_output=True, text=True, timeout=_GIT_TIMEOUT_SECONDS
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def check_for_update() -> dict | None:
    """Fetches from origin (makes no local changes) and compares HEAD
    against origin/master. Returns None if already up to date, otherwise
    a dict describing what's pending."""
    _run_git("fetch", "origin")
    local = _run_git("rev-parse", "HEAD")
    remote = _run_git("rev-parse", "origin/master")
    if local == remote:
        return None
    commits_behind = int(_run_git("rev-list", "--count", f"{local}..{remote}"))
    log = _run_git("log", "--oneline", f"{local}..{remote}")
    return {
        "current_commit": local[:8],
        "latest_commit": remote[:8],
        "commits_behind": commits_behind,
        "log": log,
    }


def pull_update() -> dict:
    """Fast-forward-only pull - refuses (raises) rather than creating a
    merge commit if local history has diverged from origin. That
    shouldn't happen in normal use (nothing here ever commits locally on
    its own), but a hard stop is safer than an automatic merge on
    someone's real working directory."""
    output = _run_git("pull", "--ff-only", "origin", "master")
    new_commit = _run_git("rev-parse", "HEAD")
    return {"output": output, "new_commit": new_commit[:8]}
