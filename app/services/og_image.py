"""OG image generation: 1200x630 clean flat PNG using Pillow.

Subtitle centred as body text. Format bottom left, author bottom right.
No card shape, no glow — just content on a clean background. Platforms
render og:title alongside, giving a subtitle-then-title reading order.
"""

from __future__ import annotations

import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

BG_COLOR = (245, 246, 248)  # #F5F6F8 — soft off-white
TEXT_COLOR = (17, 24, 39)  # #111827
MUTED_COLOR = (107, 114, 128)  # #6B7280
ACCENT_COLOR = (156, 163, 175)  # #9CA3AF

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
    """Generate a 1200x630 flat OG image as PNG bytes."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_body = _load_font("Inter-Regular.ttf", 30)
    font_meta = _load_font("Inter-Regular.ttf", 17)

    cx = WIDTH // 2
    left = 80
    right = WIDTH - 80

    # Accent mark — centred
    mark_w = 50
    mark_y = 160
    draw.rectangle(
        [cx - mark_w // 2, mark_y, cx + mark_w // 2, mark_y + 4],
        fill=ACCENT_COLOR,
    )

    # Subtitle — centred
    if subtitle:
        body_y = mark_y + 32
        wrapped = textwrap.wrap(subtitle, width=44)
        for line in wrapped[:4]:
            lb = draw.textbbox((0, 0), line, font=font_body)
            lw = lb[2] - lb[0]
            draw.text((cx - lw // 2, body_y), line, fill=TEXT_COLOR, font=font_body)
            body_y += 44

    # Bottom: format left, author right
    bottom_y = HEIGHT - 70

    if format:
        draw.text((left, bottom_y), format.lower(), fill=MUTED_COLOR, font=font_meta)

    if author_name:
        ab = draw.textbbox((0, 0), author_name, font=font_meta)
        aw = ab[2] - ab[0]
        draw.text((right - aw, bottom_y), author_name, fill=MUTED_COLOR, font=font_meta)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
