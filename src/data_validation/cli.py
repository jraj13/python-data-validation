"""Command-line interface for Parquet validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from data_validation.validators import ValidationError, validate_parquet


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Validate a Parquet dataset.")
    parser.add_argument(
        "parquet_path",
        type=Path,
        help="Path to the Parquet file to validate.",
    )
    return parser


def main() -> int:
    """Run the validation CLI."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        result = validate_parquet(args.parquet_path)
    except (ValidationError, FileNotFoundError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Validation passed: {result.parquet_path}")
    print(f"Rows validated: {result.row_count:,}")
    print(f"Execution time: {result.execution_time_seconds:.3f} seconds")
    print("Checks run:")

    for check in result.checks_run:
        print(f"  - {check}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
