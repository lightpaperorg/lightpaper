"""OG image generation: 1200x630 branded card PNG using Pillow.

Design philosophy: the platform renders og:title as the bait — the image
is a clean branded card that signals quality and format. No title in the
image avoids repetition with the card metadata every platform shows.
Recognisable at LinkedIn thumbnail size, elegant at full size.
"""

from __future__ import annotations

import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

BG_COLOR = (255, 255, 255)
BRAND_COLOR = (17, 24, 39)  # #111827
FORMAT_COLOR = (107, 114, 128)  # #6B7280

FORMAT_ACCENTS = {
    "post": (59, 130, 246),  # blue
    "paper": (99, 102, 241),  # indigo
    "essay": (220, 38, 38),  # literary red
}
DEFAULT_ACCENT = (59, 130, 246)

WIDTH = 1200
HEIGHT = 630


def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def generate_og_image(
    title: str,
    subtitle: str | None = None,
    quality_score: int | None = None,
    author_name: str | None = None,
    gravity_badges: list[str] | None = None,
    reading_time: int | None = None,
    format: str | None = None,
) -> bytes:
    """Generate a 1200x630 branded OG card as PNG bytes.

    Params beyond format are accepted for API compatibility but ignored.
    The image is brand + format only — og:title handles the hook.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    accent = FORMAT_ACCENTS.get(format, DEFAULT_ACCENT) if format else DEFAULT_ACCENT

    font_brand = _load_font("Inter-Bold.ttf", 28)
    font_format = _load_font("Inter-Regular.ttf", 20)

    # --- Accent mark: short colored rule, vertically centred ---
    cx = WIDTH // 2
    cy = HEIGHT // 2 - 30
    mark_w = 60
    draw.rectangle([cx - mark_w // 2, cy - 3, cx + mark_w // 2, cy + 3], fill=accent)

    # --- Brand wordmark, centred below mark ---
    brand = "lightpaper.org"
    bb = draw.textbbox((0, 0), brand, font=font_brand)
    bw = bb[2] - bb[0]
    draw.text((cx - bw // 2, cy + 24), brand, fill=BRAND_COLOR, font=font_brand)

    # --- Format label below brand ---
    if format:
        fmt = format.lower()
        fb = draw.textbbox((0, 0), fmt, font=font_format)
        fw = fb[2] - fb[0]
        draw.text((cx - fw // 2, cy + 64), fmt, fill=FORMAT_COLOR, font=font_format)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
