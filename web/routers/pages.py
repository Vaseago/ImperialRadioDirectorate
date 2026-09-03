"""
web/routers/pages.py

Server-rendered pages. Exactly one route for now (the jukebox itself) -
same "one route, query-param-driven views" convention as the sibling
apps, kept from the start even though V1 only has one view.
"""

import os
import sys

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

import config

router = APIRouter()

# __file__-relative resolution breaks once frozen (PyInstaller unpacks
# this module into an internal path, not next to the real install) -
# templates/static ship as loose files next to the packaged IRDWebApp.exe
# so an edit takes effect on restart with no rebuild. Same fix the
# sibling apps' own pages.py already has (see CROSS_APP_ISSUES.md).
if getattr(sys, "frozen", False):
    _WEB_DIR = os.path.join(os.path.dirname(sys.executable), "web")
else:
    _WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(_WEB_DIR, "templates"))


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {
        # Small raspberry next to the device's name label when running on
        # a Raspberry Pi (config._detect_raspberry_pi) - lets any Pi
        # user, and the owner running many desktop test windows, tell a
        # production window from a test one at a glance.
        "on_raspberry_pi": config.ON_RASPBERRY_PI,
    })
