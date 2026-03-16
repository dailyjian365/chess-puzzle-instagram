"""Chess board rendering with custom pieces and coordinates."""
from io import BytesIO

import cairosvg
import chess
from PIL import Image, ImageDraw, ImageFont

import config

# Piece SVG filename mapping
_PIECE_FILES = {
    (chess.KING, chess.WHITE): "wK.svg",
    (chess.QUEEN, chess.WHITE): "wQ.svg",
    (chess.ROOK, chess.WHITE): "wR.svg",
    (chess.BISHOP, chess.WHITE): "wB.svg",
    (chess.KNIGHT, chess.WHITE): "wN.svg",
    (chess.PAWN, chess.WHITE): "wP.svg",
    (chess.KING, chess.BLACK): "bK.svg",
    (chess.QUEEN, chess.BLACK): "bQ.svg",
    (chess.ROOK, chess.BLACK): "bR.svg",
    (chess.BISHOP, chess.BLACK): "bB.svg",
    (chess.KNIGHT, chess.BLACK): "bN.svg",
    (chess.PAWN, chess.BLACK): "bP.svg",
}

_piece_cache: dict[tuple, Image.Image] = {}

COORD_PAD = 22  # Space for coordinate labels within the frame


def _load_piece_image(piece_type: int, color: bool, square_size: int) -> Image.Image:
    """Load and render a piece SVG as a PNG at the given size."""
    cache_key = (piece_type, color, square_size)
    if cache_key in _piece_cache:
        return _piece_cache[cache_key]

    filename = _PIECE_FILES[(piece_type, color)]
    svg_path = config.PIECES_DIR / filename

    with open(svg_path, "rb") as f:
        svg_data = f.read()

    png_bytes = cairosvg.svg2png(
        bytestring=svg_data,
        output_width=square_size,
        output_height=square_size,
    )

    img = Image.open(BytesIO(png_bytes)).convert("RGBA")
    _piece_cache[cache_key] = img
    return img


def render_board_png(
    board: chess.Board,
    size: int = config.BOARD_SIZE,
    orientation: bool = chess.WHITE,
    last_move: chess.Move = None,
) -> Image.Image:
    """Render a chess board with pieces and coordinate labels."""
    # Board squares fit inside size, with coord padding on left and bottom
    board_area = size - COORD_PAD
    square_size = board_area // 8
    board_area = square_size * 8

    total = board_area + COORD_PAD
    canvas = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    light = config.BOARD_LIGHT_SQUARE
    dark = config.BOARD_DARK_SQUARE

    # Coord font
    try:
        coord_font = ImageFont.truetype(config.FONT_REGULAR, 14)
    except (OSError, IOError):
        coord_font = ImageFont.load_default()
    coord_color = "#999999"

    ox = COORD_PAD  # squares start after left margin
    oy = 0          # squares start at top

    # Draw squares and pieces
    for rank in range(8):
        for file in range(8):
            if orientation == chess.WHITE:
                sq = chess.square(file, 7 - rank)
            else:
                sq = chess.square(7 - file, rank)

            x = ox + file * square_size
            y = oy + rank * square_size

            is_light = (chess.square_rank(sq) + chess.square_file(sq)) % 2 == 1
            color = light if is_light else dark

            draw.rectangle([x, y, x + square_size - 1, y + square_size - 1],
                           fill=color)

            piece = board.piece_at(sq)
            if piece:
                piece_img = _load_piece_image(piece.piece_type, piece.color,
                                              square_size)
                canvas.paste(piece_img, (x, y), mask=piece_img)

    # Rank numbers (1-8) on the left
    for rank in range(8):
        label = str(8 - rank) if orientation == chess.WHITE else str(rank + 1)
        cy = oy + rank * square_size + square_size // 2
        bbox = draw.textbbox((0, 0), label, font=coord_font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        draw.text((COORD_PAD // 2 - lw // 2, cy - lh // 2),
                  label, font=coord_font, fill=coord_color)

    # File letters (a-h) on the bottom
    for file in range(8):
        label = chr(ord('a') + file) if orientation == chess.WHITE else chr(ord('h') - file)
        cx = ox + file * square_size + square_size // 2
        by = oy + board_area + 3
        bbox = draw.textbbox((0, 0), label, font=coord_font)
        lw = bbox[2] - bbox[0]
        draw.text((cx - lw // 2, by), label, font=coord_font, fill=coord_color)

    return canvas
