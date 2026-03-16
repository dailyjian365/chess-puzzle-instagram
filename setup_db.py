#!/usr/bin/env python3
"""One-time setup: download Lichess puzzle DB and filter to mate-in-1 puzzles."""
import csv
import io
import sys
import urllib.request
from pathlib import Path

import zstandard as zstd

import config


def download_puzzle_db(url: str, dest: Path) -> None:
    """Download the Lichess puzzle .zst file with progress reporting."""
    if dest.exists():
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"Database file already exists ({size_mb:.0f} MB): {dest}")
        print("Delete it and re-run if you want to re-download.")
        return

    print(f"Downloading Lichess puzzle database...")
    print(f"URL: {url}")
    print("This is ~300 MB and may take a few minutes.\n")

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            pct = min(100, downloaded * 100 / total_size)
            mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            print(f"\r  {pct:5.1f}% ({mb:.0f} / {total_mb:.0f} MB)", end="", flush=True)
        else:
            mb = downloaded / (1024 * 1024)
            print(f"\r  {mb:.0f} MB downloaded", end="", flush=True)

    urllib.request.urlretrieve(url, str(dest), reporthook=progress_hook)
    print(f"\n  Download complete: {dest}\n")


def filter_mate_in_1(zst_path: Path, output_csv_path: Path) -> int:
    """Stream-decompress .zst and extract only quality mateIn1 puzzles.

    Returns the count of puzzles written.
    """
    print("Filtering for mate-in-1 puzzles...")
    print(f"  Quality filters: popularity >= {config.MIN_POPULARITY}, "
          f"plays >= {config.MIN_NB_PLAYS}, "
          f"rating deviation <= {config.MAX_RATING_DEVIATION}")

    # CSV fields (no header row in Lichess file):
    # PuzzleId, FEN, Moves, Rating, RatingDeviation, Popularity, NbPlays,
    # Themes, GameUrl, OpeningTags
    HEADER = ["PuzzleId", "FEN", "Moves", "Rating", "RatingDeviation",
              "Popularity", "NbPlays", "Themes", "GameUrl", "OpeningTags"]

    dctx = zstd.ZstdDecompressor()
    count = 0
    total_rows = 0

    with open(zst_path, "rb") as zst_file:
        reader = dctx.stream_reader(zst_file)
        text_reader = io.TextIOWrapper(reader, encoding="utf-8")
        csv_reader = csv.reader(text_reader)

        # Check if first row is a header
        first_row = next(csv_reader)
        has_header = first_row[0] == "PuzzleId"

        with open(output_csv_path, "w", newline="") as out_file:
            writer = csv.writer(out_file)
            writer.writerow(HEADER)

            # Process first row as data if it's not a header
            rows_to_process = [] if has_header else [first_row]

            def process_row(row):
                nonlocal count, total_rows
                total_rows += 1
                if total_rows % 500000 == 0:
                    print(f"  Processed {total_rows:,} puzzles, found {count:,} mate-in-1...")

                try:
                    themes = row[7]
                    if config.THEME_FILTER not in themes:
                        return
                    popularity = int(row[5])
                    nb_plays = int(row[6])
                    rating_deviation = int(row[4])
                    if (popularity >= config.MIN_POPULARITY
                            and nb_plays >= config.MIN_NB_PLAYS
                            and rating_deviation <= config.MAX_RATING_DEVIATION):
                        writer.writerow(row)
                        count += 1
                except (IndexError, ValueError):
                    pass  # Skip malformed rows

            for row in rows_to_process:
                process_row(row)

            for row in csv_reader:
                process_row(row)

    print(f"\n  Total puzzles scanned: {total_rows:,}")
    print(f"  Mate-in-1 puzzles found: {count:,}")
    print(f"  Saved to: {output_csv_path}\n")
    return count


def main():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.LATEST_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("  Chess Puzzle Instagram — Database Setup")
    print("=" * 50 + "\n")

    # Step 1: Download
    download_puzzle_db(config.PUZZLE_DB_URL, config.PUZZLE_DB_ZST_PATH)

    # Step 2: Filter
    if config.PUZZLE_DB_FILTERED_PATH.exists():
        print(f"Filtered file already exists: {config.PUZZLE_DB_FILTERED_PATH}")
        print("Delete it and re-run if you want to re-filter.\n")
    else:
        count = filter_mate_in_1(config.PUZZLE_DB_ZST_PATH, config.PUZZLE_DB_FILTERED_PATH)
        if count == 0:
            print("ERROR: No mate-in-1 puzzles found! Check the database file.")
            sys.exit(1)

    # Step 3: Summary
    print("=" * 50)
    print("  Setup complete!")
    print(f"  Filtered puzzles: {config.PUZZLE_DB_FILTERED_PATH}")
    print(f"  You can now run: python generate.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
