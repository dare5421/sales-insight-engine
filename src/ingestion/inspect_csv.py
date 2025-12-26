#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def inspect(file_path: Path, max_examples: int = 5) -> int:
    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            print("ERROR: empty file (no header).")
            return 2

        expected = len(header)
        total = 0
        fixed_short = 0
        fixed_trailing_empty_extra = 0
        bad = 0
        examples = []

        for line_no, row in enumerate(reader, start=2):
            total += 1
            original_len = len(row)

            # Fix 1: if row has extra columns but they are ALL empty (common trailing commas)
            if original_len > expected:
                extras = row[expected:]
                if all((c is None) or (str(c).strip() == "") for c in extras):
                    row = row[:expected]
                    fixed_trailing_empty_extra += 1
                else:
                    bad += 1
                    if len(examples) < max_examples:
                        examples.append((line_no, original_len, expected, row[:expected], row[expected:]))
                    continue

            # Fix 2: if row is short, pad with empty strings
            if len(row) < expected:
                row = row + [""] * (expected - len(row))
                fixed_short += 1

            # Final check (should match)
            if len(row) != expected:
                bad += 1
                if len(examples) < max_examples:
                    examples.append((line_no, original_len, expected, row, []))

        print(f"File: {file_path.name}")
        print(f"Header columns: {expected}")
        print(f"Data rows: {total}")
        print(f"Fixed short rows (padded): {fixed_short}")
        print(f"Fixed trailing-empty extra cols (trimmed): {fixed_trailing_empty_extra}")
        print(f"Bad rows (not auto-fixable): {bad}")

        if examples:
            print("\nExamples of bad rows (first few):")
            for ex in examples:
                line_no, orig_len, exp, left, extras = ex
                print(f"- Line {line_no}: had {orig_len} cols, expected {exp}. Extras (non-empty): {extras[:10]}")

        return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    args = ap.parse_args()
    raise SystemExit(inspect(Path(args.file)))


if __name__ == "__main__":
    main()
