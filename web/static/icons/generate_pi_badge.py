"""
web/static/icons/generate_pi_badge.py

One-off generator for a "points at the Pi, not a local instance" badge
variant of this app's icon, for the desktop shortcut created via
--remote-url (see desktop_shell/app.py). Draws a small raspberry (a
plain geometric cluster of shaded circles + a leaf, not any real
artwork or trademarked logo - matches generate_icons.py's own "no CCP/
EVE trademarked assets" rule, and avoids the actual Raspberry Pi Ltd.
logo for the same reason) in the top-right corner of the existing
icon-512.png, then exports a multi-resolution .ico from it.

Ported verbatim (badge geometry/colors) from the sibling Imperial
apps' own generate_pi_badge.py (e.g. ImperialSkillDirectorate's) -
only BG/BORDER re-matched to IRD's own theme, and badge_size uses the
same 0.330 fraction the sibling apps settled on (2026-08-21) after
testing a smaller badge first.

Run with `python3 web/static/icons/generate_pi_badge.py` any time the
badge design needs to change - re-run and commit the resulting
ird_app_pi.ico, don't hand-edit it. Requires icon-512.png to already
exist (run generate_icons.py first if it doesn't).
"""

import os

from PIL import Image, ImageDraw

_ICONS_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_PREFIX = "ird"

_BADGE_BG = (11, 9, 6, 255)      # matches --page
_BADGE_BORDER = "#a8874f"        # matches --gold-dim

_DRUPELET_COLORS = ["#d81159", "#a30b48", "#7a0934"]
_HIGHLIGHT_COLOR = "#ff6f91"
_LEAF_COLOR = "#3f7d3f"

# (dx, dy) as a fraction of badge size, relative to center - a rough
# raspberry silhouette (wider top, tapered bottom)
_DRUPELET_POSITIONS = [
    (0, -0.30), (-0.28, -0.15), (0.28, -0.15), (0, -0.05),
    (-0.30, 0.10), (0.30, 0.10), (-0.12, 0.20), (0.12, 0.20),
    (0, 0.35),
]


def _draw_raspberry(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    drupelet_r = size * 0.14

    for i, (dx, dy) in enumerate(_DRUPELET_POSITIONS):
        r = drupelet_r * (0.9 + 0.15 * (i % 3))
        x, y = cx + dx * size, cy + dy * size
        draw.ellipse([x - r, y - r, x + r, y + r], fill=_DRUPELET_COLORS[i % len(_DRUPELET_COLORS)])
        hl_r = r * 0.35
        hx, hy = x - r * 0.3, y - r * 0.3
        draw.ellipse([hx - hl_r, hy - hl_r, hx + hl_r, hy + hl_r], fill=_HIGHLIGHT_COLOR)

    leaf_pts = [
        (cx - size * 0.12, cy - size * 0.38),
        (cx, cy - size * 0.52),
        (cx + size * 0.12, cy - size * 0.38),
        (cx, cy - size * 0.30),
    ]
    draw.polygon(leaf_pts, fill=_LEAF_COLOR)
    return img


def _add_pi_badge(base: Image.Image) -> Image.Image:
    base = base.convert("RGBA")
    size = base.size[0]

    badge_size = int(size * 0.330)
    pad = int(badge_size * 0.10)
    circle_size = badge_size + pad * 2

    circle = Image.new("RGBA", (circle_size, circle_size), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(circle)
    cdraw.ellipse(
        [0, 0, circle_size - 1, circle_size - 1],
        fill=_BADGE_BG,
        outline=_BADGE_BORDER,
        width=max(1, circle_size // 24),
    )
    raspberry = _draw_raspberry(badge_size)
    circle.alpha_composite(raspberry, (pad, pad))

    offset = int(size * 0.02)
    x = size - circle_size + offset
    y = -offset
    base.alpha_composite(circle, (x, y))
    return base


def main():
    src_path = os.path.join(_ICONS_DIR, "icon-512.png")
    base = Image.open(src_path)
    badged = _add_pi_badge(base)

    preview_path = os.path.join(_ICONS_DIR, f"{_APP_PREFIX}_app_pi_preview.png")
    badged.save(preview_path)
    print(f"wrote {preview_path}")

    ico_path = os.path.join(_ICONS_DIR, f"{_APP_PREFIX}_app_pi.ico")
    badged.save(
        ico_path,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    print(f"wrote {ico_path}")


if __name__ == "__main__":
    main()
