"""Project-wide configuration constants."""
from pathlib import Path

# === Paths ===
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LATEST_DIR = OUTPUT_DIR / "latest"
FONTS_DIR = PROJECT_ROOT / "fonts"

PUZZLE_DB_URL = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
PUZZLE_DB_ZST_PATH = DATA_DIR / "lichess_db_puzzle.csv.zst"
PUZZLE_DB_FILTERED_PATH = DATA_DIR / "mate_in_1_puzzles.csv"
USED_PUZZLES_PATH = PROJECT_ROOT / "used_puzzles.json"

# === Image Dimensions ===
IMAGE_SIZE = 1080
BOARD_SIZE = 720
BOARD_TOP_OFFSET = 180
BOARD_LEFT_OFFSET = (IMAGE_SIZE - BOARD_SIZE) // 2  # 180

# === Color Palette ===
BG_GRADIENT_TOP = (35, 38, 45)       # Dark slate
BG_GRADIENT_BOTTOM = (28, 30, 36)    # Slightly darker at bottom
BOARD_LIGHT_SQUARE = "#d9cfc0"
BOARD_DARK_SQUARE = "#8a8585"
BOARD_FRAME_COLOR = "#444850"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#b0a898"
TEXT_GOLD = "#c4a35a"

# === Piece Set ===
PIECES_DIR = PROJECT_ROOT / "pieces" / "cburnett"

# === Fonts (bundled in fonts/ directory) ===
FONT_BOLD = str(FONTS_DIR / "Inter-Bold.ttf")
FONT_REGULAR = str(FONTS_DIR / "Inter-Regular.ttf")
FONT_BLACK = str(FONTS_DIR / "Anton-Regular.ttf")

# Font sizes
HEADER_FONT_SIZE = 24
TITLE_FONT_SIZE = 90
TURN_FONT_SIZE = 26
CTA_FONT_SIZE = 28
COMMENT_FONT_SIZE = 24
BRAND_FONT_SIZE = 22
PUZZLE_NUM_FONT_SIZE = 20

# === Puzzle Quality Filters ===
THEME_FILTER = "mateIn1"
MIN_POPULARITY = 0
MIN_NB_PLAYS = 500
MAX_RATING_DEVIATION = 100

# === Branding (customize these!) ===
BRAND_NAME = "DailyMateIn1"
BRAND_HANDLE = "@dailymatein1"
