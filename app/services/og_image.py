"""OG image generation: 1200x630 glowing paper card PNG using Pillow.

Design: soft gray background with a glowing white card. Subtitle centred
inside the card as body text. Author name at bottom left. Platforms
render og:title alongside, giving a subtitle-then-title reading order.
"""

from __future__ import annotations

import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

# Background — dark surround matches app icon, makes the card glow
BG_COLOR = (15, 20, 31)  # deep navy

# Card — very light gray to match platform title bar backgrounds
CARD_COLOR = (245, 246, 248)  # #F5F6F8
CARD_RADIUS = 18

# Text
TEXT_COLOR = (17, 24, 39)  # #111827
MUTED_COLOR = (107, 114, 128)  # #6B7280
ACCENT_COLOR = (156, 163, 175)  # #9CA3AF — neutral, no format colours

WIDTH = 1200
HEIGHT = 630

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
    # --- Step 1: gray bg + white shape → blur → soft glow ---
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    glow_draw = ImageDraw.Draw(img)

    pad = 10
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
    font_body = _load_font("Inter-Regular.ttf", 30)
    font_meta = _load_font("Inter-Regular.ttf", 17)

    card_cx = CARD_X + CARD_W // 2  # horizontal centre of card
    inner_left = CARD_X + 56
    inner_right = CARD_X + CARD_W - 56

    # Accent mark — centred, neutral
    mark_w = 50
    mark_y = CARD_Y + 48
    draw.rectangle(
        [card_cx - mark_w // 2, mark_y, card_cx + mark_w // 2, mark_y + 4],
        fill=ACCENT_COLOR,
    )

    # Subtitle — centred, bigger
    if subtitle:
        body_y = mark_y + 32
        wrapped = textwrap.wrap(subtitle, width=44)
        for line in wrapped[:4]:
            lb = draw.textbbox((0, 0), line, font=font_body)
            lw = lb[2] - lb[0]
            draw.text((card_cx - lw // 2, body_y), line, fill=TEXT_COLOR, font=font_body)
            body_y += 44

    # Bottom of card: format left, author right
    bottom_y = CARD_Y + CARD_H - 50

    if format:
        draw.text((inner_left, bottom_y), format.lower(), fill=MUTED_COLOR, font=font_meta)

    if author_name:
        ab = draw.textbbox((0, 0), author_name, font=font_meta)
        aw = ab[2] - ab[0]
        draw.text((inner_right - aw, bottom_y), author_name, fill=MUTED_COLOR, font=font_meta)

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
