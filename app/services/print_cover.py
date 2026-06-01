"""Print-ready cover PDF generation using Pillow.

Generates a full wrap cover (back + spine + front) at 300 DPI with 0.125" bleed.
Matches lightpaper brand: dark background (#0F141F), white text, Inter Bold.
"""

from __future__ import annotations

import asyncio
import os
import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")

# Brand colors
BG_COLOR = (15, 20, 31)      # #0F141F
TEXT_COLOR = (255, 255, 255)  # white
MUTED_COLOR = (156, 163, 175)  # #9CA3AF
ACCENT_COLOR = (200, 180, 120)  # warm gold for accent line

DPI = 300

# Trim dimensions (inches)
FRONT_W_IN = 6.0
FRONT_H_IN = 9.0
BLEED_IN = 0.125

# Full page with bleed
PAGE_W_IN = FRONT_W_IN + BLEED_IN  # 6.125"
PAGE_H_IN = FRONT_H_IN + 2 * BLEED_IN  # 9.25"


def _in_to_px(inches: float) -> int:
    return int(round(inches * DPI))


def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _load_bold_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
    except OSError:
        return _load_font("Inter-Regular.ttf", size)


def compute_spine_width_in(page_count: int) -> float:
    """Spine width = page_count × 0.0025" (cream/white paper)."""
    return page_count * 0.0025


async def generate_cover_pdf(
    title: str,
    subtitle: str | None,
    author_name: str | None,
    description: str | None,
    page_count: int,
) -> bytes:
    """Generate a full wrap cover (back + spine + front) as PDF at 300 DPI."""

    def _render():
        spine_w_in = compute_spine_width_in(page_count)

        total_w_in = PAGE_W_IN + spine_w_in + PAGE_W_IN
        total_h_in = PAGE_H_IN

        w_px = _in_to_px(total_w_in)
        h_px = _in_to_px(total_h_in)

        img = Image.new("RGB", (w_px, h_px), BG_COLOR)
        draw = ImageDraw.Draw(img)

        bleed_px = _in_to_px(BLEED_IN)
        page_w_px = _in_to_px(PAGE_W_IN)
        spine_w_px = _in_to_px(spine_w_in)

        # Region boundaries
        back_left = 0
        back_right = page_w_px
        spine_left = back_right
        spine_right = spine_left + spine_w_px
        front_left = spine_right
        front_right = w_px

        # Fonts
        font_title = _load_bold_font("Inter-Bold.ttf", 72)
        font_subtitle = _load_font("Inter-Regular.ttf", 36)
        font_author = _load_font("Inter-Regular.ttf", 30)
        font_spine = _load_bold_font("Inter-Bold.ttf", max(14, int(spine_w_px * 0.55)))
        font_back = _load_font("Inter-Regular.ttf", 24)
        font_back_small = _load_font("Inter-Regular.ttf", 18)

        # --- FRONT COVER ---
        safe_left = front_left + bleed_px + _in_to_px(0.5)
        safe_right = front_right - bleed_px - _in_to_px(0.5)
        safe_top = bleed_px + _in_to_px(1.5)
        safe_w = safe_right - safe_left

        # Accent line
        accent_y = safe_top - _in_to_px(0.3)
        accent_w = _in_to_px(1.0)
        center_x = (front_left + front_right) // 2
        draw.rectangle(
            [center_x - accent_w // 2, accent_y, center_x + accent_w // 2, accent_y + 4],
            fill=ACCENT_COLOR,
        )

        # Title — centered, wrapped
        title_lines = textwrap.wrap(title, width=20)
        title_y = safe_top
        for line in title_lines[:4]:
            tb = draw.textbbox((0, 0), line, font=font_title)
            tw = tb[2] - tb[0]
            th = tb[3] - tb[1]
            draw.text((center_x - tw // 2, title_y), line, fill=TEXT_COLOR, font=font_title)
            title_y += th + 16

        # Subtitle
        if subtitle:
            sub_y = title_y + 24
            sub_lines = textwrap.wrap(subtitle, width=35)
            for line in sub_lines[:3]:
                sb = draw.textbbox((0, 0), line, font=font_subtitle)
                sw = sb[2] - sb[0]
                draw.text((center_x - sw // 2, sub_y), line, fill=MUTED_COLOR, font=font_subtitle)
                sub_y += sb[3] - sb[1] + 8

        # Author — bottom of front
        if author_name:
            author_y = h_px - bleed_px - _in_to_px(1.2)
            ab = draw.textbbox((0, 0), author_name, font=font_author)
            aw = ab[2] - ab[0]
            draw.text((center_x - aw // 2, author_y), author_name, fill=MUTED_COLOR, font=font_author)

        # --- SPINE ---
        if spine_w_px > _in_to_px(0.3):
            # Only render spine text if spine is wide enough
            spine_cx = spine_left + spine_w_px // 2
            # Rotated text: title · author
            spine_text = title
            if author_name:
                spine_text = f"{title}  \u00b7  {author_name}"

            # Create rotated text
            stb = draw.textbbox((0, 0), spine_text, font=font_spine)
            st_w = stb[2] - stb[0]
            st_h = stb[3] - stb[1]

            txt_img = Image.new("RGBA", (st_w + 20, st_h + 10), (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((10, 5), spine_text, fill=TEXT_COLOR, font=font_spine)

            rotated = txt_img.rotate(90, expand=True)
            # Center on spine
            paste_x = spine_cx - rotated.width // 2
            paste_y = h_px // 2 - rotated.height // 2
            img.paste(rotated, (paste_x, paste_y), rotated)

        # --- BACK COVER ---
        back_safe_left = back_left + bleed_px + _in_to_px(0.5)
        back_safe_right = back_right - bleed_px - _in_to_px(0.5)
        back_safe_w = back_safe_right - back_safe_left
        back_center = (back_left + back_right) // 2

        if description:
            desc_y = bleed_px + _in_to_px(1.5)
            desc_lines = textwrap.wrap(description[:500], width=40)
            for line in desc_lines[:15]:
                db = draw.textbbox((0, 0), line, font=font_back)
                dw = db[2] - db[0]
                draw.text((back_center - dw // 2, desc_y), line, fill=MUTED_COLOR, font=font_back)
                desc_y += db[3] - db[1] + 8

        # Barcode placeholder area (bottom of back)
        barcode_w = _in_to_px(2.0)
        barcode_h = _in_to_px(1.2)
        barcode_x = back_center - barcode_w // 2
        barcode_y = h_px - bleed_px - _in_to_px(1.5) - barcode_h
        draw.rectangle(
            [barcode_x, barcode_y, barcode_x + barcode_w, barcode_y + barcode_h],
            outline=MUTED_COLOR,
            width=2,
        )
        placeholder_text = "ISBN BARCODE"
        ptb = draw.textbbox((0, 0), placeholder_text, font=font_back_small)
        ptw = ptb[2] - ptb[0]
        draw.text(
            (back_center - ptw // 2, barcode_y + barcode_h // 2 - 10),
            placeholder_text,
            fill=MUTED_COLOR,
            font=font_back_small,
        )

        # "lightpaper.org" at very bottom of back
        lp_text = "lightpaper.org"
        lptb = draw.textbbox((0, 0), lp_text, font=font_back_small)
        lpw = lptb[2] - lptb[0]
        draw.text(
            (back_center - lpw // 2, h_px - bleed_px - _in_to_px(0.5)),
            lp_text,
            fill=MUTED_COLOR,
            font=font_back_small,
        )

        buf = BytesIO()
        img.save(buf, format="PDF", dpi=(DPI, DPI))
        return buf.getvalue()

    return await asyncio.to_thread(_render)
