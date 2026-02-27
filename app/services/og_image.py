"""OG image generation: 1200x630 monochrome PNG using Pillow."""

import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

# Colors (light mode for OG images)
BG_COLOR = (255, 255, 255)
HEADING_COLOR = (17, 24, 39)      # #111827
BODY_COLOR = (55, 65, 81)         # #374151
SECONDARY_COLOR = (107, 114, 128) # #6B7280
BORDER_COLOR = (229, 231, 235)    # #E5E7EB

WIDTH = 1200
HEIGHT = 630


def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TTF font, falling back to default if not found."""
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    # Fallback to default
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except (OSError, IOError):
        return ImageFont.load_default()


def generate_og_image(
    title: str,
    subtitle: str | None = None,
    quality_score: int | None = None,
    author_name: str | None = None,
    gravity_badges: list[str] | None = None,
    reading_time: int | None = None,
) -> bytes:
    """Generate a 1200x630 monochrome OG image as PNG bytes."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_bold_lg = _load_font("Inter-Bold.ttf", 48)
    font_regular = _load_font("Inter-Regular.ttf", 24)
    font_mono = _load_font("JetBrainsMono-Regular.ttf", 20)
    font_small = _load_font("Inter-Regular.ttf", 18)

    y = 60

    # Brand
    draw.text((60, y), "lightpaper.org", fill=SECONDARY_COLOR, font=font_small)
    y += 50

    # Quality score badge (top right)
    if quality_score is not None:
        score_text = f"{quality_score}/100"
        bbox = draw.textbbox((0, 0), score_text, font=font_regular)
        sw = bbox[2] - bbox[0]
        draw.rounded_rectangle(
            [WIDTH - 60 - sw - 20, 55, WIDTH - 60 + 10, 95],
            radius=6,
            outline=BORDER_COLOR,
            width=2,
        )
        draw.text((WIDTH - 60 - sw - 10, 60), score_text, fill=BODY_COLOR, font=font_regular)

    # Title (word-wrapped)
    wrapped = textwrap.wrap(title, width=35)
    for i, line in enumerate(wrapped[:3]):  # max 3 lines
        if i == 2 and len(wrapped) > 3:
            line = line[:40] + "..."
        draw.text((60, y), line, fill=HEADING_COLOR, font=font_bold_lg)
        y += 60
    y += 10

    # Subtitle
    if subtitle:
        sub_wrapped = textwrap.wrap(subtitle, width=55)
        for line in sub_wrapped[:2]:
            draw.text((60, y), line, fill=SECONDARY_COLOR, font=font_regular)
            y += 32
        y += 10

    # Divider line
    y = max(y, 400)
    draw.line([(60, y), (WIDTH - 60, y)], fill=BORDER_COLOR, width=1)
    y += 25

    # Author + badges + reading time
    meta_parts = []
    if author_name:
        meta_parts.append(author_name)
    if gravity_badges:
        meta_parts.extend(gravity_badges)
    if reading_time:
        meta_parts.append(f"{reading_time} min read")

    if meta_parts:
        meta_text = "  \u00b7  ".join(meta_parts)
        draw.text((60, y), meta_text, fill=SECONDARY_COLOR, font=font_small)

    # Output
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
