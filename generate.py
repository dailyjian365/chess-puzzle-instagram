#!/usr/bin/env python3
"""Daily chess puzzle generator — main entry point."""
import argparse
import shutil
import sys
from datetime import date

import chess

import config
from board_renderer import render_board_png
from caption_generator import generate_caption, generate_solution_text
from image_composer import compose_puzzle_image
from puzzle_db import (
    get_difficulty_label,
    get_puzzle_position,
    load_used_puzzles,
    save_used_puzzles,
    select_random_puzzle,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a daily Instagram chess puzzle post."
    )
    parser.add_argument("--rating-min", type=int, default=0,
                        help="Minimum puzzle rating (default: no filter)")
    parser.add_argument("--rating-max", type=int, default=9999,
                        help="Maximum puzzle rating (default: no filter)")
    parser.add_argument("--brand-name", type=str, default=None,
                        help="Override brand name from config")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Override output directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview puzzle selection without saving files")
    return parser.parse_args()


def main():
    args = parse_args()

    # Verify setup
    if not config.PUZZLE_DB_FILTERED_PATH.exists():
        print("ERROR: Filtered puzzle database not found.")
        print(f"Expected: {config.PUZZLE_DB_FILTERED_PATH}")
        print("Run 'python setup_db.py' first to download and prepare the database.")
        sys.exit(1)

    output_dir = config.OUTPUT_DIR
    if args.output_dir:
        from pathlib import Path
        output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config.LATEST_DIR.mkdir(parents=True, exist_ok=True)

    # Load puzzle tracking data
    tracking = load_used_puzzles(config.USED_PUZZLES_PATH)
    puzzle_number = tracking["next_number"]

    # Select random puzzle
    puzzle = select_random_puzzle(
        config.PUZZLE_DB_FILTERED_PATH,
        tracking["used"],
        rating_min=args.rating_min,
        rating_max=args.rating_max,
    )

    # Parse puzzle position
    board, solution_san, side_to_move, last_move = get_puzzle_position(
        puzzle["fen"], puzzle["moves"]
    )

    # Render board PNG
    orientation = chess.WHITE if side_to_move == "White" else chess.BLACK
    board_img = render_board_png(
        board,
        size=config.BOARD_SIZE,
        orientation=orientation,
        last_move=last_move,
    )

    # Compose final branded image
    brand = args.brand_name or config.BRAND_NAME
    final_image = compose_puzzle_image(
        board_img, side_to_move, puzzle["rating"], brand,
        puzzle_number=puzzle_number,
    )

    # Generate caption and solution
    difficulty = get_difficulty_label(puzzle["rating"])
    caption = generate_caption(
        side_to_move=side_to_move,
        rating=puzzle["rating"],
        difficulty=difficulty,
        puzzle_id=puzzle["puzzle_id"],
        game_url=puzzle["game_url"],
        brand_handle=config.BRAND_HANDLE,
    )
    solution_text = generate_solution_text(
        solution_san, puzzle["puzzle_id"], puzzle["game_url"]
    )

    # File paths
    today = date.today().isoformat()
    num = f"{puzzle_number:03d}"
    image_path = output_dir / f"puzzle_{num}_{today}.png"
    caption_path = output_dir / f"puzzle_{num}_{today}_caption.txt"
    solution_path = output_dir / f"puzzle_{num}_{today}_solution.txt"

    if not args.dry_run:
        # Save to output/
        final_image.save(str(image_path), "PNG")
        caption_path.write_text(caption, encoding="utf-8")
        solution_path.write_text(solution_text, encoding="utf-8")

        # Copy to output/latest/ for easy access
        latest_image = config.LATEST_DIR / "puzzle_latest.png"
        latest_caption = config.LATEST_DIR / "puzzle_latest_caption.txt"
        latest_solution = config.LATEST_DIR / "puzzle_latest_solution.txt"
        shutil.copy2(str(image_path), str(latest_image))
        shutil.copy2(str(caption_path), str(latest_caption))
        shutil.copy2(str(solution_path), str(latest_solution))

        # Mark puzzle as used and increment number
        tracking["used"].add(puzzle["puzzle_id"])
        tracking["next_number"] = puzzle_number + 1
        save_used_puzzles(config.USED_PUZZLES_PATH, tracking)

    # Print summary
    print(f"\n{'=' * 55}")
    print(f"  Chess Puzzle #{num} Generated!")
    print(f"{'=' * 55}")
    print(f"  Puzzle #  : {num}")
    print(f"  Rating    : {puzzle['rating']} ({difficulty})")
    print(f"  Side      : {side_to_move} to move")
    print(f"  Solution  : {solution_san}")
    print(f"{'=' * 55}")
    if not args.dry_run:
        print(f"  Image     : {image_path}")
        print(f"  Caption   : {caption_path}")
        print(f"  Solution  : {solution_path}")
        print(f"  Latest    : {config.LATEST_DIR}/")
    else:
        print("  (dry run — no files saved)")
    print(f"\n{'—' * 55}")
    print("CAPTION:")
    print(f"{'—' * 55}")
    print(caption)
    print(f"{'—' * 55}")
    print(f"\nSOLUTION (pin as comment): {solution_san}")
    print()


if __name__ == "__main__":
    main()
