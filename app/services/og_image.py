"""OG image generation: 1200x630 glowing paper card PNG using Pillow.

Dark background with a glowing white card (matching the app icon).
Title centred inside the card as the hero, with the subtitle smaller and muted
beneath it. Format bottom left, author bottom right.
"""

from __future__ import annotations

import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

BG_COLOR = (15, 20, 31)  # deep navy — matches app icon
CARD_COLOR = (245, 246, 248)  # #F5F6F8
CARD_RADIUS = 18

TEXT_COLOR = (17, 24, 39)  # #111827
MUTED_COLOR = (107, 114, 128)  # #6B7280
ACCENT_COLOR = (156, 163, 175)  # #9CA3AF

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
    # --- Step 1: dark bg + card shape → blur → glow ---
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

    # --- Step 3: content (title-forward) ---
    font_title = _load_font("Inter-Regular.ttf", 52)
    font_sub = _load_font("Inter-Regular.ttf", 24)
    font_meta = _load_font("Inter-Regular.ttf", 17)

    card_cx = CARD_X + CARD_W // 2
    inner_left = CARD_X + 56
    inner_right = CARD_X + CARD_W - 56

    # Title is the hero; subtitle is smaller, muted context beneath it.
    title_lines = textwrap.wrap(title, width=26)[:3]
    sub_lines = textwrap.wrap(subtitle, width=58)[:2] if subtitle else []
    TITLE_LH, SUB_LH = 60, 34
    block_h = len(title_lines) * TITLE_LH + (18 + len(sub_lines) * SUB_LH if sub_lines else 0)

    # Vertically centre the title+subtitle block (nudged up to clear the bottom bar).
    top = CARD_Y + (CARD_H - block_h) // 2 - 12

    # Accent mark — centred, just above the block
    mark_w = 50
    mark_y = top - 34
    draw.rectangle(
        [card_cx - mark_w // 2, mark_y, card_cx + mark_w // 2, mark_y + 4],
        fill=ACCENT_COLOR,
    )

    y = top
    for line in title_lines:
        lb = draw.textbbox((0, 0), line, font=font_title)
        draw.text((card_cx - (lb[2] - lb[0]) // 2, y), line, fill=TEXT_COLOR, font=font_title)
        y += TITLE_LH

    if sub_lines:
        y += 18
        for line in sub_lines:
            lb = draw.textbbox((0, 0), line, font=font_sub)
            draw.text((card_cx - (lb[2] - lb[0]) // 2, y), line, fill=MUTED_COLOR, font=font_sub)
            y += SUB_LH

    # Bottom: format left, author right
    bottom_y = CARD_Y + CARD_H - 50
    if format:
        draw.text((inner_left, bottom_y), format.lower(), fill=MUTED_COLOR, font=font_meta)
    if author_name:
        ab = draw.textbbox((0, 0), author_name, font=font_meta)
        aw = ab[2] - ab[0]
        draw.text((inner_right - aw, bottom_y), author_name, fill=MUTED_COLOR, font=font_meta)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def generate_book_og_image(
    title: str,
    subtitle: str | None = None,
    chapter_count: int = 0,
    author_name: str | None = None,
    format: str | None = None,
) -> bytes:
    """Generate a 1200x630 OG card for a book: title centred in the glowing card."""
    # Must be 1200x630 — iMessage and most platforms reject non-standard sizes
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    glow_draw = ImageDraw.Draw(img)

    pad = 10
    glow_draw.rounded_rectangle(
        [CARD_X - pad, CARD_Y - pad, CARD_X + CARD_W + pad, CARD_Y + CARD_H + pad],
        radius=CARD_RADIUS + pad,
        fill=CARD_COLOR,
    )
    img = img.filter(ImageFilter.GaussianBlur(radius=28))

    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [CARD_X, CARD_Y, CARD_X + CARD_W, CARD_Y + CARD_H],
        radius=CARD_RADIUS,
        fill=CARD_COLOR,
    )

    font_title = _load_font("Inter-Regular.ttf", 52)
    font_subtitle = _load_font("Inter-Regular.ttf", 24)
    font_meta = _load_font("Inter-Regular.ttf", 17)

    card_cx = CARD_X + CARD_W // 2
    inner_left = CARD_X + 56
    inner_right = CARD_X + CARD_W - 56

    # Accent mark — centred
    mark_w = 50
    mark_y = CARD_Y + 48
    draw.rectangle(
        [card_cx - mark_w // 2, mark_y, card_cx + mark_w // 2, mark_y + 4],
        fill=ACCENT_COLOR,
    )

    # Title — large, centred
    tb = draw.textbbox((0, 0), title, font=font_title)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    title_y = CARD_Y + CARD_H // 2 - th // 2 - 20
    draw.text((card_cx - tw // 2, title_y), title, fill=TEXT_COLOR, font=font_title)

    # Subtitle — centred below title
    if subtitle:
        sub_y = title_y + th + 16
        sb = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        sw = sb[2] - sb[0]
        draw.text((card_cx - sw // 2, sub_y), subtitle, fill=MUTED_COLOR, font=font_subtitle)

    # Bottom bar: title left, author right
    bottom_y = CARD_Y + CARD_H - 50
    draw.text((inner_left, bottom_y), title.lower(), fill=MUTED_COLOR, font=font_meta)

    if author_name:
        ab = draw.textbbox((0, 0), author_name, font=font_meta)
        aw = ab[2] - ab[0]
        draw.text((inner_right - aw, bottom_y), author_name, fill=MUTED_COLOR, font=font_meta)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
