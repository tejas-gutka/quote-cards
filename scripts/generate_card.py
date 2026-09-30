#!/usr/bin/env python3
"""
generate_card.py

Generate a PNG image card for a long X/Twitter quote post.

Design spec:
  - Background: very light grey (#F8F8F8)
  - Card: rounded rectangle, solid blue (#29A9E1)
  - Quote text: white, italic serif, auto-sized to fit
  - Author: white, regular serif, preceded by em dash
  - No take, no hashtag inside the image -- caption only
  - Aspect ratio: 16:9 (1200 x 675 px)
  - Output: PNG

Usage:
  python generate_card.py --quote "Full quote text" --author "Author Name" --output output/card_q1.png

Requirements:
  pip install Pillow --break-system-packages
"""

import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip install Pillow --break-system-packages")
    sys.exit(1)

# -- Dimensions ----------------------------------------------------------------
CARD_W = 1200
CARD_H = 675
BG_COLOR    = (248, 248, 248)   # #F8F8F8
CARD_COLOR  = (41, 169, 225)    # #29A9E1
TEXT_COLOR  = (255, 255, 255)
CARD_MARGIN = 48                # gap between image edge and blue card
CORNER_R    = 22                # rounded corner radius
PAD         = 64                # padding inside the blue card

# Font size range for auto-sizing
QUOTE_FONT_MAX = 36
QUOTE_FONT_MIN = 14

# -- Font paths (tried in order; first found wins) ----------------------------
_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

ITALIC_FONTS = [
    os.path.join(_FONT_DIR, "DejaVuSerifCondensed-Italic.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf",
    "C:/Windows/Fonts/timesi.ttf",
]
REGULAR_FONTS = [
    os.path.join(_FONT_DIR, "DejaVuSerif-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
    "C:/Windows/Fonts/timesbd.ttf",
]


def load_font(paths: list, size: int) -> ImageFont.FreeTypeFont:
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int,
              draw: ImageDraw.ImageDraw) -> list:
    """Wrap text so each line fits within max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def line_height(font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw, leading: int) -> int:
    bbox = draw.textbbox((0, 0), "Ag", font=font)
    return (bbox[3] - bbox[1]) + leading


def generate_card(quote_text: str, author_name: str, output_path: str) -> None:
    img  = Image.new("RGB", (CARD_W, CARD_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Blue card
    cx1, cy1 = CARD_MARGIN, CARD_MARGIN
    cx2, cy2 = CARD_W - CARD_MARGIN, CARD_H - CARD_MARGIN
    draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=CORNER_R, fill=CARD_COLOR)

    text_x       = cx1 + PAD
    max_text_w   = (cx2 - cx1) - 2 * PAD
    card_inner_h = cy2 - cy1
    available_h  = card_inner_h - 2 * PAD
    GAP          = 18

    quote_display = f"“{quote_text}”"

    # Auto-size: step down from max font size until the full quote + author fits
    quote_font = author_font = q_lines = q_line_h = a_line_h = None

    for q_size in range(QUOTE_FONT_MAX, QUOTE_FONT_MIN - 1, -1):
        a_size = max(QUOTE_FONT_MIN, int(q_size * 0.72))
        _qf    = load_font(ITALIC_FONTS,  q_size)
        _af    = load_font(REGULAR_FONTS, a_size)
        _lines = wrap_text(quote_display, _qf, max_text_w, draw)
        _qlh   = line_height(_qf, draw, 10)
        _alh   = line_height(_af, draw, 8)
        if len(_lines) * _qlh + GAP + _alh <= available_h:
            quote_font, author_font = _qf, _af
            q_lines, q_line_h, a_line_h = _lines, _qlh, _alh
            break

    if quote_font is None:  # overflows even at minimum size -- use min anyway
        q_size      = QUOTE_FONT_MIN
        quote_font  = load_font(ITALIC_FONTS,  q_size)
        author_font = load_font(REGULAR_FONTS, q_size)
        q_lines     = wrap_text(quote_display, quote_font, max_text_w, draw)
        q_line_h    = line_height(quote_font,  draw, 10)
        a_line_h    = line_height(author_font, draw, 8)

    total_h = len(q_lines) * q_line_h + GAP + a_line_h

    # Centre vertically within the card
    start_y = cy1 + (card_inner_h - total_h) // 2
    if start_y < cy1 + PAD:
        start_y = cy1 + PAD

    cur_y = start_y
    for line in q_lines:
        draw.text((text_x, cur_y), line, font=quote_font, fill=TEXT_COLOR)
        cur_y += q_line_h

    cur_y += GAP
    draw.text((text_x, cur_y), f"— {author_name}", font=author_font, fill=TEXT_COLOR)

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Card saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a 1200x675 PNG image card for an X quote post."
    )
    parser.add_argument("--quote",  required=True, help="Full quote text (no surrounding quotation marks)")
    parser.add_argument("--author", required=True, help="Author name")
    parser.add_argument("--output", default="card.png", help="Output file path (PNG)")
    args = parser.parse_args()

    generate_card(args.quote, args.author, args.output)
