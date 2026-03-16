"""Generate Instagram captions with hashtags and engagement prompts."""
import random


# Core hashtags (always included)
CORE_HASHTAGS = [
    "#chess", "#chesspuzzle", "#matein1", "#checkmate", "#dailypuzzle",
]

# Rotating pool (random subset selected each time)
EXTRA_HASHTAGS = [
    "#chessboard", "#chesslover", "#chesslife", "#chessplayer",
    "#chessproblem", "#chesschallenge", "#chesscommunity",
    "#chessisfun", "#learnchess", "#chessnotcheckers",
    "#braingame", "#puzzle", "#brainteaser", "#thinkingcap",
    "#logic", "#strategy", "#chessmoves", "#chessmaster",
    "#chesstactics", "#chessgame",
]

# Engagement prompts (rotated for variety)
PROMPTS = [
    "Comment your answer below!",
    "Drop your move in the comments!",
    "Can you solve it? Comment below!",
    "Type your answer in the comments!",
    "What's your move? Tell us below!",
]

CHALLENGE_LINES = [
    "30-second challenge — how fast can you solve it?",
    "Set a timer — can you beat 30 seconds?",
    "Quick puzzle — try to solve in under 30 seconds!",
    "Time yourself — 30 seconds on the clock!",
]


def generate_caption(
    side_to_move: str,
    rating: int,
    difficulty: str,
    puzzle_id: str,
    game_url: str,
    brand_handle: str,
) -> str:
    """Generate a ready-to-post Instagram caption."""
    prompt = random.choice(PROMPTS)
    challenge = random.choice(CHALLENGE_LINES)
    hashtags = _select_hashtags(count=22)

    caption = (
        f"MATE IN 1 — {difficulty} Puzzle\n"
        f"\n"
        f"{side_to_move} to move. Can you spot the checkmate?\n"
        f"\n"
        f"{challenge}\n"
        f"\n"
        f"{prompt} Tag a friend who loves chess.\n"
        f"Solution will be pinned in the comments!\n"
        f"\n"
        f".\n.\n.\n"
        f"\n"
        f"{hashtags}\n"
        f"\n"
        f"Puzzle from lichess.org (CC0) | {brand_handle}"
    )
    return caption


def generate_solution_text(solution_san: str, puzzle_id: str, game_url: str) -> str:
    """Generate the solution text for pinning as a comment."""
    return (
        f"Solution: {solution_san}\n"
        f"\n"
        f"Did you get it right? Like this comment if you solved it!\n"
        f"\n"
        f"Puzzle ID: {puzzle_id}\n"
        f"Full game: {game_url}"
    )


def _select_hashtags(count: int = 22) -> str:
    """Select a varied set of hashtags from the pool."""
    extra_count = min(count - len(CORE_HASHTAGS), len(EXTRA_HASHTAGS))
    selected = CORE_HASHTAGS + random.sample(EXTRA_HASHTAGS, extra_count)
    random.shuffle(selected)
    # Split into two lines for readability
    mid = len(selected) // 2
    line1 = " ".join(selected[:mid])
    line2 = " ".join(selected[mid:])
    return f"{line1}\n{line2}"
