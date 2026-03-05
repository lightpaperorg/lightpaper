"""OG image generation: 1200x630 glowing paper card PNG using Pillow.

Design: dark background with a glowing white card (matching the app icon).
The subtitle lives inside the card as body text. Platforms render og:title
alongside, so the reading order is: subtitle (image) → title (card metadata).
Authors craft subtitle as setup, title as payoff.
"""

from __future__ import annotations

import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

# Dark surround — matches app icon background
BG_COLOR = (15, 20, 31)  # deep navy, slightly warmer than pure black

# Card (the glowing "paper")
CARD_COLOR = (255, 255, 255)
CARD_RADIUS = 18

# Text on card
TEXT_COLOR = (17, 24, 39)  # #111827
BRAND_COLOR = (156, 163, 175)  # #9CA3AF
FORMAT_LABEL_COLOR = (107, 114, 128)  # #6B7280

# Format accent — the colored mark on the card
FORMAT_ACCENTS = {
    "post": (59, 130, 246),  # blue
    "paper": (99, 102, 241),  # indigo
    "essay": (220, 38, 38),  # literary red
}
DEFAULT_ACCENT = (59, 130, 246)

WIDTH = 1200
HEIGHT = 630

# Card geometry — centred, with room for glow
CARD_W = 960
CARD_H = 410
CARD_X = (WIDTH - CARD_W) // 2
CARD_Y = (HEIGHT - CARD_H) // 2


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
    """Generate a 1200x630 glowing-paper OG card as PNG bytes."""
    accent = FORMAT_ACCENTS.get(format, DEFAULT_ACCENT) if format else DEFAULT_ACCENT

    # --- Step 1: dark bg + white shape → blur → glow ---
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    glow_draw = ImageDraw.Draw(img)

    # Draw white rect slightly larger than card, then blur for glow halo
    pad = 12
    glow_draw.rounded_rectangle(
        [CARD_X - pad, CARD_Y - pad, CARD_X + CARD_W + pad, CARD_Y + CARD_H + pad],
        radius=CARD_RADIUS + pad,
        fill=CARD_COLOR,
    )
    img = img.filter(ImageFilter.GaussianBlur(radius=28))

    # --- Step 2: sharp card on top ---
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [CARD_X, CARD_Y, CARD_X + CARD_W, CARD_Y + CARD_H],
        radius=CARD_RADIUS,
        fill=CARD_COLOR,
    )

    # --- Step 3: content inside the card ---
    font_body = _load_font("Inter-Regular.ttf", 26)
    font_brand = _load_font("Inter-Bold.ttf", 17)
    font_format = _load_font("Inter-Regular.ttf", 17)

    inner_left = CARD_X + 56
    inner_right = CARD_X + CARD_W - 56
    inner_top = CARD_Y + 48

    # Accent mark
    draw.rectangle(
        [inner_left, inner_top, inner_left + 50, inner_top + 4],
        fill=accent,
    )

    # Subtitle as body text
    if subtitle:
        body_y = inner_top + 28
        wrapped = textwrap.wrap(subtitle, width=52)
        for line in wrapped[:4]:
            draw.text((inner_left, body_y), line, fill=TEXT_COLOR, font=font_body)
            body_y += 38

    # Bottom of card: brand left, format right
    bottom_y = CARD_Y + CARD_H - 50
    draw.text((inner_left, bottom_y), "lightpaper.org", fill=BRAND_COLOR, font=font_brand)

    if format:
        fmt = format.lower()
        fb = draw.textbbox((0, 0), fmt, font=font_format)
        fw = fb[2] - fb[0]
        draw.text((inner_right - fw, bottom_y), fmt, fill=accent, font=font_format)

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
