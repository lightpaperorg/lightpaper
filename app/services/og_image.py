"""OG image generation: 1200x630 minimal white PNG using Pillow.

Design philosophy: a title page. The title IS the image. Everything else
is subordinate — a short accent mark for format, brand at the bottom,
generous whitespace. Works at full size (WhatsApp, X, Slack) and as a
tiny LinkedIn thumbnail (white + color accent + bold text pattern).
"""

from __future__ import annotations

import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

# Palette — clean white with near-black type
BG_COLOR = (255, 255, 255)
TITLE_COLOR = (17, 24, 39)  # #111827
SUBTITLE_COLOR = (107, 114, 128)  # #6B7280
BRAND_COLOR = (156, 163, 175)  # #9CA3AF
RULE_COLOR = (229, 231, 235)  # #E5E7EB

# Format accent colors — the only color on the page
FORMAT_COLORS = {
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
    """Generate a 1200x630 white OG image as PNG bytes.

    Only title, subtitle, brand, and format are rendered. Other params
    are accepted for API compatibility but intentionally ignored — the
    image should be a clean title page, not a dashboard.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = _load_font("Inter-Bold.ttf", 52)
    font_subtitle = _load_font("Inter-Regular.ttf", 24)
    font_brand = _load_font("Inter-Regular.ttf", 17)
    font_format = _load_font("Inter-Regular.ttf", 17)

    accent = FORMAT_COLORS.get(format, DEFAULT_ACCENT) if format else DEFAULT_ACCENT
    left = 80

    # --- Accent mark: short colored rule ---
    mark_y = 130
    draw.rectangle([left, mark_y, left + 70, mark_y + 5], fill=accent)

    # --- Title ---
    title_y = mark_y + 32
    wrapped = textwrap.wrap(title, width=32)
    line_height = 64
    for i, line in enumerate(wrapped[:3]):
        if i == 2 and len(wrapped) > 3:
            line = line[:36] + "..."
        draw.text((left, title_y), line, fill=TITLE_COLOR, font=font_title)
        title_y += line_height

    # --- Subtitle ---
    if subtitle:
        sub_y = title_y + 12
        sub_wrapped = textwrap.wrap(subtitle, width=56)
        for line in sub_wrapped[:2]:
            draw.text((left, sub_y), line, fill=SUBTITLE_COLOR, font=font_subtitle)
            sub_y += 32

    # --- Bottom bar: thin rule + brand left, format right ---
    bar_y = HEIGHT - 70
    draw.line([(left, bar_y), (WIDTH - left, bar_y)], fill=RULE_COLOR, width=1)

    # Brand
    draw.text((left, bar_y + 18), "lightpaper.org", fill=BRAND_COLOR, font=font_brand)

    # Format label (lowercase, in accent color)
    if format:
        fmt_text = format.lower()
        fb = draw.textbbox((0, 0), fmt_text, font=font_format)
        fw = fb[2] - fb[0]
        draw.text((WIDTH - left - fw, bar_y + 18), fmt_text, fill=accent, font=font_format)

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
