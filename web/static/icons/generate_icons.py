"""
web/static/icons/generate_icons.py

One-off generator for this project's icon set. Run with
`python3 web/static/icons/generate_icons.py` from the repo root any time
the design needs to change (colors below match web/static/css/style.css's
--page/--gold/--gold-dim) - re-run and commit the resulting PNGs/.ico,
don't hand-edit them.

Ported from the sibling Imperial apps' own icon generators (see e.g.
ImperialSkillDirectorate/web/static/icons/generate_icons.py) - same
plain-monogram approach, no CCP/EVE artwork or trademark, just a
Windows system font (Georgia Bold) on the app's own dark background.
IRD has no icon assets of its own until this script was added
(2026-08-31, alongside the first desktop shortcut needing one) - unlike
the sibling apps, IRD had genuinely never had any icon at all before
this.

Also writes ird_app.ico directly (a plain, un-badged multi-resolution
icon from icon-512.png) - the sibling apps generate this same file by
hand rather than via a script; scripting it here instead so it's
reproducible.
"""

import os

from PIL import Image, ImageDraw, ImageFont

BG = "#0b0906"        # matches --page
FG = "#e8c878"        # matches --gold
BORDER = "#a8874f"    # matches --gold-dim

_ICONS_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_PREFIX = "ird"
_FONT_PATH = r"C:\Windows\Fonts\georgiab.ttf"

SIZES = [512, 192, 180, 32]


def _draw_icon(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), BG)
    draw = ImageDraw.Draw(img)

    border_w = max(1, size // 32)
    inset = border_w * 2
    draw.rectangle(
        [inset, inset, size - inset - 1, size - inset - 1],
        outline=BORDER,
        width=border_w,
    )

    text = "IRD"
    font_size = int(size * 0.42)
    font = ImageFont.truetype(_FONT_PATH, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - text_w) / 2 - bbox[0], (size - text_h) / 2 - bbox[1]),
        text,
        fill=FG,
        font=font,
    )
    return img


def main():
    largest = None
    for size in SIZES:
        icon = _draw_icon(size)
        if size == 512:
            largest = icon
        out_path = os.path.join(_ICONS_DIR, f"icon-{size}.png")
        icon.save(out_path)
        print(f"wrote {out_path}")

    ico_path = os.path.join(_ICONS_DIR, f"{_APP_PREFIX}_app.ico")
    largest.save(
        ico_path,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    print(f"wrote {ico_path}")


if __name__ == "__main__":
    main()
