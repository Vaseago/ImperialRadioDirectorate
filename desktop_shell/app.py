"""The desktop shell: a thin native window wrapping a QWebEngineView
pointed at a locally-spawned ird_web_main.py instance.

Deliberately NOT a native Qt-widget reimplementation of web/'s UI -
there is only one UI codebase (web/), so every web/ change is
automatically on the desktop shell too, with no manual porting. Ported
from the sibling apps' own desktop shell pattern.

Simpler than ISD/ILD's own desktop shells - no ESI client ID/callback
to register or pass through at all, since this app has zero EVE Online
API dependency.

Confirmed with the user (2026-08-21): this app is desktop-only for now
- no NSSM/Pi-hosted always-on web service is being set up. That's a
DEPLOYMENT choice, not an architecture one; this shell still spawns the
same web/ FastAPI app any future web installer would use, so the door
stays open with zero rework if that's ever wanted later.

Update 2026-08-30: the Pi-hosted door mentioned above is now open - IRD
was added to the Pi's supervisor install (see ../_supervisor's own
CLAUDE.md-equivalent commit) alongside IID/ISD/ILD, running as an
always-on service on port 8060. `--remote-url` (ported from the sibling
apps' own desktop shells) lets this same native window wrap that
already-running instance instead of always spawning a local
ird_web_main.py, matching the "Imperial ___ Directorate (Pi)" desktop
shortcut convention the other 3 apps already have.
"""

import argparse
import os
import subprocess
import sys
import time

import requests
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A dedicated port so this never conflicts with ird_web_main.py's own
# default (8060, see config.py).
PORT = 8070

# The desktop shell gets its own data directory - deliberately NOT
# config.DATA_DIR (which ird_web_main.py also uses by default), same
# isolation reasoning as the sibling apps' own desktop shells, even
# though the ONLY thing that would ever live here is
# config_overrides.json (this app has no ESI tokens to isolate at all).
# MUSIC_LIBRARY_DIR is deliberately NOT overridden here - the spawned
# subprocess inherits the same default (or the same IRD_MUSIC_DIR env
# value) as the always-on service, so the desktop shell shows the
# identical library with zero duplication.
if getattr(sys, "frozen", False):
    DATA_DIR = os.path.join(os.environ["PROGRAMDATA"], "Imperial Radio Directorate Desktop")
else:
    DATA_DIR = os.path.join(REPO_ROOT, "data_desktop")

READY_TIMEOUT_SECONDS = 10


def _wait_until_ready(url, timeout_seconds):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            requests.get(url, timeout=1)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.2)
    return False


class DesktopWindow(QMainWindow):
    def __init__(self, server_process, url):
        super().__init__()
        self._server_process = server_process

        self.setWindowTitle("Imperial Radio Directorate")
        self.view = QWebEngineView(self)
        self.view.load(QUrl(url))
        self.setCentralWidget(self.view)
        self.resize(900, 700)

    def closeEvent(self, event):
        if self._server_process is not None:
            self._server_process.terminate()
            try:
                self._server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server_process.kill()
        super().closeEvent(event)


def main():
    parser = argparse.ArgumentParser(description="Imperial Radio Directorate desktop shell")
    parser.add_argument(
        "--remote-url",
        default=None,
        help=(
            "Point this window at an ALREADY-RUNNING instance (e.g. "
            "http://192.168.1.50:8060/ for the Pi on your home LAN) instead of "
            "spawning a local ird_web_main.py. No local process is "
            "managed/closed in this mode - closing the window just closes "
            "the window, the remote server keeps running."
        ),
    )
    args = parser.parse_args()

    if args.remote_url:
        server_process = None
        url = args.remote_url
    else:
        env = os.environ.copy()
        env["IRD_WEB_PORT"] = str(PORT)
        env["IRD_DATA_DIR"] = DATA_DIR

        if getattr(sys, "frozen", False):
            # sys.executable is THIS packaged exe once frozen, not a Python
            # interpreter - the web server is packaged as its own separate
            # sibling exe (IRDWebApp.exe, built from ird_web_main.py)
            # installed alongside this one.
            exe_dir = os.path.dirname(sys.executable)
            web_exe = os.path.join(exe_dir, "IRDWebApp.exe")
            server_process = subprocess.Popen([web_exe], cwd=exe_dir, env=env)
        else:
            server_process = subprocess.Popen(
                [sys.executable, "ird_web_main.py"], cwd=REPO_ROOT, env=env
            )

        url = f"http://localhost:{PORT}/"
        if not _wait_until_ready(url, READY_TIMEOUT_SECONDS):
            server_process.terminate()
            raise RuntimeError(
                f"ird_web_main.py did not respond on {url} within "
                f"{READY_TIMEOUT_SECONDS}s - check its console output for errors."
            )

    app = QApplication(sys.argv)
    window = DesktopWindow(server_process, url)
    window.show()
    sys.exit(app.exec())
