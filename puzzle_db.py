"""Puzzle database loading, selection, and FEN parsing."""
import csv
import json
import random
from pathlib import Path

import chess

import config


def load_used_puzzles(path: Path) -> dict:
    """Load puzzle tracking data from JSON file.

    Returns dict with keys: 'used' (set of IDs), 'next_number' (int).
    """
    if not path.exists():
        return {"used": set(), "next_number": 1}
    with open(path, "r") as f:
        data = json.load(f)
    return {
        "used": set(data.get("used", [])),
        "next_number": data.get("next_number", len(data.get("used", [])) + 1),
    }


def save_used_puzzles(path: Path, tracking: dict) -> None:
    """Save updated puzzle tracking data to JSON."""
    from datetime import date
    data = {
        "used": sorted(tracking["used"]),
        "total_used": len(tracking["used"]),
        "next_number": tracking["next_number"],
        "last_updated": date.today().isoformat(),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def select_random_puzzle(csv_path: Path, used_ids: set,
                         rating_min: int = 0, rating_max: int = 9999) -> dict:
    """Select a random unused mateIn1 puzzle from the filtered CSV.

    Returns a dict with keys: puzzle_id, fen, moves, rating, themes, game_url
    """
    candidates = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["PuzzleId"]
            if pid in used_ids:
                continue
            rating = int(row["Rating"])
            if rating < rating_min or rating > rating_max:
                continue
            candidates.append(row)

    if not candidates:
        raise RuntimeError(
            "No unused puzzles available! Either all puzzles have been used "
            "or the rating filter is too restrictive."
        )

    chosen = random.choice(candidates)
    return {
        "puzzle_id": chosen["PuzzleId"],
        "fen": chosen["FEN"],
        "moves": chosen["Moves"].split(),
        "rating": int(chosen["Rating"]),
        "themes": chosen["Themes"].split(),
        "game_url": chosen["GameUrl"],
    }


def get_puzzle_position(fen: str, moves: list) -> tuple:
    """Convert raw puzzle data into the board position shown to the solver.

    Lichess FEN is the position BEFORE the opponent's last move.
    We push the first move (opponent's) to get the puzzle position.
    The solution is the second move.

    Returns:
        board: chess.Board in the puzzle position
        solution_san: str (e.g., "Qxf7#")
        side_to_move: str ("White" or "Black")
        last_move: chess.Move (the opponent's move, for highlighting)
    """
    board = chess.Board(fen)

    # Push opponent's move to reach the puzzle position
    opponent_move = chess.Move.from_uci(moves[0])
    board.push(opponent_move)

    # Now it's the solver's turn
    side_to_move = "White" if board.turn == chess.WHITE else "Black"

    # Solution is the next move
    solution_move = board.parse_uci(moves[1])
    solution_san = board.san(solution_move)

    return board, solution_san, side_to_move, opponent_move


def get_difficulty_label(rating: int) -> str:
    """Convert numeric rating to human-readable difficulty."""
    if rating < 1000:
        return "Beginner"
    elif rating < 1500:
        return "Intermediate"
    elif rating < 2000:
        return "Advanced"
    else:
        return "Expert"
