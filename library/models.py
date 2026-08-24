"""
library/models.py

Pure data model, no web/ or filesystem dependency of its own - mirrors
the sibling apps' sde/planner/logistics separation-of-concerns
principle.
"""

from dataclasses import dataclass


@dataclass
class Track:
    id: str
    title: str
    artist: str
    album: str
    duration_seconds: float
    path: str
    library_dir: str
    mtime: float
    station: str
