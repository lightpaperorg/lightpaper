"""OG image generation: 1200x630 dark-mode PNG using Pillow."""

from __future__ import annotations

import math
import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

# Dark mode palette
BG_COLOR = (17, 24, 39)  # #111827
TITLE_COLOR = (255, 255, 255)
SUBTITLE_COLOR = (156, 163, 175)  # #9CA3AF
MUTED_COLOR = (107, 114, 128)  # #6B7280
DIVIDER_COLOR = (55, 65, 81)  # #374151
ACCENT_GREEN = (34, 197, 94)  # #22C55E
ACCENT_AMBER = (245, 158, 11)  # #F59E0B
ACCENT_RED = (239, 68, 68)  # #EF4444
ACCENT_BLUE = (59, 130, 246)  # #3B82F6
BADGE_BG = (31, 41, 55)  # #1F2937
BADGE_TEXT = (209, 213, 219)  # #D1D5DB
BRAND_COLOR = (107, 114, 128)  # #6B7280

FORMAT_COLORS = {
    "post": (59, 130, 246),  # blue
    "paper": (168, 85, 247),  # purple
    "essay": (236, 72, 153),  # pink
}

WIDTH = 1200
HEIGHT = 630


def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TTF font, falling back to default if not found."""
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _score_color(score: int) -> tuple[int, int, int]:
    """Return color based on quality score."""
    if score >= 70:
        return ACCENT_GREEN
    if score >= 40:
        return ACCENT_AMBER
    return ACCENT_RED


def _draw_score_arc(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int,
                    score: int, font_lg: ImageFont.FreeTypeFont,
                    font_sm: ImageFont.FreeTypeFont):
    """Draw a quality score with a circular arc indicator."""
    color = _score_color(score)

    # Background track (full circle)
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.arc(bbox, start=0, end=360, fill=DIVIDER_COLOR, width=6)

    # Score arc (proportional to score, starting from top = -90 degrees)
    sweep = int(360 * score / 100)
    if sweep > 0:
        draw.arc(bbox, start=-90, end=-90 + sweep, fill=color, width=6)

    # Score number centered
    score_text = str(score)
    sb = draw.textbbox((0, 0), score_text, font=font_lg)
    sw = sb[2] - sb[0]
    sh = sb[3] - sb[1]
    draw.text((cx - sw // 2, cy - sh // 2 - 4), score_text, fill=color, font=font_lg)

    # "/100" below
    label = "/100"
    lb = draw.textbbox((0, 0), label, font=font_sm)
    lw = lb[2] - lb[0]
    draw.text((cx - lw // 2, cy + sh // 2 + 2), label, fill=MUTED_COLOR, font=font_sm)


def _draw_badge(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
                font: ImageFont.FreeTypeFont,
                bg: tuple = BADGE_BG, fg: tuple = BADGE_TEXT) -> int:
    """Draw a rounded badge chip. Returns the width consumed (badge + gap)."""
    tb = draw.textbbox((0, 0), text, font=font)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    pad_x = 12
    pad_y = 6
    badge_w = tw + pad_x * 2
    badge_h = th + pad_y * 2

    draw.rounded_rectangle(
        [x, y, x + badge_w, y + badge_h],
        radius=badge_h // 2,
        fill=bg,
    )
    draw.text((x + pad_x, y + pad_y), text, fill=fg, font=font)
    return badge_w + 8  # 8px gap between badges


def generate_og_image(
    title: str,
    subtitle: str | None = None,
    quality_score: int | None = None,
    author_name: str | None = None,
    gravity_badges: list[str] | None = None,
    reading_time: int | None = None,
    format: str | None = None,
) -> bytes:
    """Generate a 1200x630 dark-mode OG image as PNG bytes."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = _load_font("Inter-Bold.ttf", 44)
    font_subtitle = _load_font("Inter-Regular.ttf", 22)
    font_meta = _load_font("Inter-Regular.ttf", 18)
    font_badge = _load_font("Inter-Regular.ttf", 16)
    font_score_lg = _load_font("Inter-Bold.ttf", 36)
    font_score_sm = _load_font("Inter-Regular.ttf", 14)
    font_brand = _load_font("Inter-Regular.ttf", 16)

    # Layout constants
    left = 60
    right_margin = 60
    score_area_width = 140 if quality_score is not None else 0
    text_right = WIDTH - right_margin - score_area_width - 20

    y = 50

    # Top bar: brand + format tag + reading time
    draw.text((left, y), "lightpaper.org", fill=BRAND_COLOR, font=font_brand)

    top_right_x = WIDTH - right_margin
    if reading_time:
        rt_text = f"{reading_time} min read"
        rtb = draw.textbbox((0, 0), rt_text, font=font_meta)
        rtw = rtb[2] - rtb[0]
        draw.text((top_right_x - rtw, y), rt_text, fill=MUTED_COLOR, font=font_meta)
        top_right_x -= rtw + 20

    if format:
        fmt_text = format.upper()
        fmt_color = FORMAT_COLORS.get(format, ACCENT_BLUE)
        fb = draw.textbbox((0, 0), fmt_text, font=font_badge)
        fw = fb[2] - fb[0]
        fh = fb[3] - fb[1]
        pad_x = 10
        pad_y = 4
        chip_w = fw + pad_x * 2
        chip_x = top_right_x - chip_w
        draw.rounded_rectangle(
            [chip_x, y - 2, chip_x + chip_w, y + fh + pad_y * 2],
            radius=(fh + pad_y * 2) // 2,
            fill=(*fmt_color, ),
        )
        draw.text((chip_x + pad_x, y + pad_y - 2), fmt_text, fill=(255, 255, 255), font=font_badge)

    y += 50

    # Thin divider below top bar
    draw.line([(left, y), (WIDTH - right_margin, y)], fill=DIVIDER_COLOR, width=1)
    y += 30

    # Title (word-wrapped, constrained to leave room for score arc)
    chars_per_line = 30 if score_area_width else 35
    wrapped = textwrap.wrap(title, width=chars_per_line)
    for i, line in enumerate(wrapped[:3]):
        if i == 2 and len(wrapped) > 3:
            line = line[:38] + "..."
        draw.text((left, y), line, fill=TITLE_COLOR, font=font_title)
        y += 56
    y += 8

    # Subtitle
    if subtitle:
        sub_chars = 52 if score_area_width else 60
        sub_wrapped = textwrap.wrap(subtitle, width=sub_chars)
        for line in sub_wrapped[:2]:
            draw.text((left, y), line, fill=SUBTITLE_COLOR, font=font_subtitle)
            y += 30
        y += 8

    # Quality score arc (right side, vertically centered in content area)
    if quality_score is not None:
        score_cx = WIDTH - right_margin - 60
        score_cy = 250
        _draw_score_arc(draw, score_cx, score_cy, 50, quality_score,
                        font_score_lg, font_score_sm)

    # Bottom section: divider + author + badges
    bottom_y = 470
    draw.line([(left, bottom_y), (WIDTH - right_margin, bottom_y)], fill=DIVIDER_COLOR, width=1)
    bottom_y += 20

    # Author name
    if author_name:
        draw.text((left, bottom_y), author_name, fill=SUBTITLE_COLOR, font=font_meta)
        bottom_y += 30

    # Credential/verification badges as chips (wrapping)
    if gravity_badges:
        badge_x = left
        badge_y = bottom_y
        max_x = WIDTH - right_margin
        for badge_text in gravity_badges:
            # Measure to see if it fits
            tb = draw.textbbox((0, 0), badge_text, font=font_badge)
            tw = tb[2] - tb[0]
            needed = tw + 24 + 8  # pad + gap
            if badge_x + needed > max_x and badge_x > left:
                # Wrap to next line
                badge_x = left
                badge_y += 34
                if badge_y > HEIGHT - 30:
                    break  # Don't overflow image
            badge_x += _draw_badge(draw, badge_x, badge_y, badge_text, font_badge)

    # Subtle bottom accent line
    accent = FORMAT_COLORS.get(format, ACCENT_BLUE) if format else ACCENT_BLUE
    draw.rectangle([0, HEIGHT - 4, WIDTH, HEIGHT], fill=accent)

    # Output
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
