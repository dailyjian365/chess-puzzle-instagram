"""Compose the final 1080x1080 branded Instagram image."""
from PIL import Image, ImageDraw, ImageFont

import config


def compose_puzzle_image(
    board_image: Image.Image,
    side_to_move: str,
    rating: int,
    brand_name: str,
    puzzle_number: int = 1,
) -> Image.Image:
    """Compose an elegant 1080x1080 Instagram-ready image.

    Layout matching reference style:
      ── DAILY CHESS PUZZLE ──    (muted, flanked by lines)
      MATE IN 1                   (large bold white)
      ── WHITE TO MOVE ──         (gold, flanked by lines)
      [board with dark frame]
      CAN YOU FIND THE MATE?      (white caps)
      ──────                      (gold line)
      COMMENT THE WINNING MOVE!   (gold caps)
      brand + puzzle #
    """
    canvas = _create_gradient_bg(config.IMAGE_SIZE,
                                 config.BG_GRADIENT_TOP,
                                 config.BG_GRADIENT_BOTTOM)
    draw = ImageDraw.Draw(canvas)

    W = config.TEXT_WHITE
    G = config.TEXT_GOLD
    M = config.TEXT_MUTED

    # Load fonts
    header_font = _load_font(config.FONT_BOLD, config.HEADER_FONT_SIZE)
    title_font = _load_font(config.FONT_BLACK, config.TITLE_FONT_SIZE)
    turn_font = _load_font(config.FONT_BOLD, config.TURN_FONT_SIZE)
    cta_font = _load_font(config.FONT_BOLD, config.CTA_FONT_SIZE)
    comment_font = _load_font(config.FONT_BOLD, config.COMMENT_FONT_SIZE)
    brand_font = _load_font(config.FONT_REGULAR, config.BRAND_FONT_SIZE)
    num_font = _load_font(config.FONT_REGULAR, config.PUZZLE_NUM_FONT_SIZE)

    # --- ── DAILY CHESS PUZZLE ── (flanked lines, muted) ---
    _draw_flanked_text(draw, "DAILY CHESS PUZZLE", y=30, font=header_font,
                       fill=M, line_color=M, gap=16, line_len=80)

    # --- M A T E  I N  1 (large, bold, white, letter-spaced) ---
    _draw_spaced_text(draw, "MATE IN 1", y=62, font=title_font,
                      fill=W, spacing=12)

    # --- ── WHITE TO MOVE ── (flanked lines, muted matching header) ---
    turn_text = f"{side_to_move.upper()} TO MOVE"
    _draw_flanked_text(draw, turn_text, y=185, font=turn_font,
                       fill=G, line_color=M, gap=16, line_len=80)

    # --- Chess Board with dark frame ---
    board_w = board_image.size[0]
    board_h = board_image.size[1]
    board_left = (config.IMAGE_SIZE - board_w) // 2
    board_top = 232

    # Dark frame around board
    frame_pad = 8
    frame_color = config.BOARD_FRAME_COLOR
    # Outer frame
    draw.rectangle(
        [board_left - frame_pad - 2, board_top - frame_pad - 2,
         board_left + board_w + frame_pad + 1, board_top + board_h + frame_pad + 1],
        fill=frame_color,
    )
    # Inner dark border
    draw.rectangle(
        [board_left - 1, board_top - 1,
         board_left + board_w, board_top + board_h],
        outline="#2a2a2a", width=1,
    )

    canvas.paste(board_image,
                 (board_left, board_top),
                 mask=board_image)

    # --- CAN YOU FIND THE MATE? (white caps) ---
    bottom_start = board_top + board_h + frame_pad + 25
    _draw_centered_text(draw, "CAN YOU FIND THE MATE?",
                        y=bottom_start, font=cta_font, fill=W)

    # --- gold line (spans width of both text lines) ---
    # Measure wider of the two texts to set line length
    cta_text = "CAN YOU FIND THE MATE?"
    comment_text = "COMMENT THE WINNING MOVE!"
    cta_w = draw.textbbox((0, 0), cta_text, font=cta_font)[2]
    comment_w = draw.textbbox((0, 0), comment_text, font=comment_font)[2]
    line_width = max(cta_w, comment_w)

    line_y = bottom_start + 46
    _draw_line(draw, y=line_y, color=G, length=line_width)

    # --- COMMENT THE WINNING MOVE! (gold caps) ---
    _draw_centered_text(draw, comment_text,
                        y=line_y + 14, font=comment_font, fill=G)

    # --- Bottom: brand (muted) left, puzzle # (gold) right ---
    bar_y = config.IMAGE_SIZE - 38
    margin = 50
    draw.text((margin, bar_y), brand_name, font=brand_font, fill=M)

    puzzle_text = f"Puzzle #{puzzle_number:03d}"
    bbox = draw.textbbox((0, 0), puzzle_text, font=num_font)
    text_width = bbox[2] - bbox[0]
    draw.text((config.IMAGE_SIZE - margin - text_width, bar_y),
              puzzle_text, font=num_font, fill=G)

    return canvas.convert("RGB")


def _draw_centered_text(draw, text, y, font, fill, canvas_width=config.IMAGE_SIZE):
    """Draw text horizontally centered."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (canvas_width - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_spaced_text(draw, text, y, font, fill, spacing=10,
                      canvas_width=config.IMAGE_SIZE):
    """Draw text with extra letter spacing, centered."""
    # Measure total width with spacing
    chars = list(text)
    total_w = 0
    char_widths = []
    for ch in chars:
        bbox = draw.textbbox((0, 0), ch, font=font)
        w = bbox[2] - bbox[0]
        char_widths.append(w)
        total_w += w
    total_w += spacing * (len(chars) - 1)

    x = (canvas_width - total_w) // 2
    for i, ch in enumerate(chars):
        draw.text((x, y), ch, font=font, fill=fill)
        x += char_widths[i] + spacing


def _draw_flanked_text(draw, text, y, font, fill, line_color,
                       gap=16, line_len=80):
    """Draw text centered with short lines on both sides: ── TEXT ──"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    center_x = config.IMAGE_SIZE // 2
    text_x = center_x - text_w // 2
    line_y = y + text_h // 2

    # Left line
    draw.line([(text_x - gap - line_len, line_y), (text_x - gap, line_y)],
              fill=line_color, width=1)
    # Text
    draw.text((text_x, y), text, font=font, fill=fill)
    # Right line
    draw.line([(text_x + text_w + gap, line_y),
               (text_x + text_w + gap + line_len, line_y)],
              fill=line_color, width=1)


def _draw_line(draw, y, color, length=180, width=1):
    """Draw a short centered accent line."""
    center = config.IMAGE_SIZE // 2
    draw.line([(center - length // 2, y), (center + length // 2, y)],
              fill=color, width=width)


def _create_gradient_bg(size, color_top, color_bottom):
    """Create a vertical gradient background."""
    column = Image.new("RGBA", (1, size))
    for y in range(size):
        t = y / (size - 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        column.putpixel((0, y), (r, g, b, 255))
    return column.resize((size, size), Image.NEAREST)


def _load_font(font_path, size):
    """Load a TrueType font with fallback to default."""
    try:
        return ImageFont.truetype(font_path, size)
    except (OSError, IOError):
        print(f"  Warning: Font not found: {font_path}, using default")
        return ImageFont.load_default()
