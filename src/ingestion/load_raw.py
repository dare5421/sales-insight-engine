#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path
#from typing import List

import psycopg2
from psycopg2.extras import execute_values

EXPECTED_COLS = 61

# Compute a hash for a row of values
def row_hash(values: list[str]) -> str:
    # minimal normalization: strip spaces, keep content as-is
    payload = "\x1f".join([(v or "").strip() for v in values])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

# Connect to the Postgres database
def connect():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5433")),
        dbname=os.getenv("DB_NAME", "sales_engine"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )

# Main function
def main():
    # Parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--batch-id", required=True)
    ap.add_argument("--chunk-size", type=int, default=2000)
    args = ap.parse_args()

    # Validate file path
    file_path = Path(args.file)
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")

    # Get source file name
    source_file = file_path.name

    # Read rows from CSV
    rows: list[list[str]] = []
    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise SystemExit("CSV is empty (no header).")
        if len(header) != EXPECTED_COLS:
            raise SystemExit(f"Header has {len(header)} columns, expected {EXPECTED_COLS}.")

        for line_no, r in enumerate(reader, start=2):
            if len(r) != EXPECTED_COLS:
                raise SystemExit(f"Row {line_no} has {len(r)} columns, expected {EXPECTED_COLS}.")
            rows.append(r)

    if not rows:
        print("No data rows found.")
        return

    # Prepare insert payload
    # columns: source_file, load_batch_id, row_hash, c01..c61
    payload = []
    for r in rows:
        payload.append([source_file, args.batch_id, row_hash(r)] + r)

    cols = ["source_file", "load_batch_id", "row_hash"] + [f"c{i:02d}" for i in range(1, EXPECTED_COLS + 1)]
    sql = f"""
        insert into raw_karamad_sales ({", ".join(cols)})
        values %s
        on conflict (source_system, row_hash) do nothing;
    """

    conn = connect()
    try:

        with conn:
            with conn.cursor() as cur:
                for start in range(0, len(payload), args.chunk_size):
                    chunk = payload[start : start + args.chunk_size]
                    execute_values(cur, sql, chunk, page_size=len(chunk))

                cur.execute(
                    "select count(*) from raw_karamad_sales where load_batch_id=%s and source_file=%s",
                    (args.batch_id, source_file),
                )
                
                row = cur.fetchone()
                if row is None:
                    raise SystemExit("Unexpected: SELECT count(*) returned no row")
                inserted = row[0]

        print(f"File: {source_file}")
        print(f"Rows read: {len(rows)}")
        print(f"Rows present in RAW for this batch/file: {inserted}")
        if inserted < len(rows):
            print(f"Skipped as duplicates: {len(rows) - inserted}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
