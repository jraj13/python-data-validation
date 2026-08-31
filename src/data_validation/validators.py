"""Reusable data validation functions."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import duckdb
import pyarrow.parquet as pq

from data_validation.schema import (
    COMPOSITE_KEY,
    EXPECTED_SCHEMA,
    REQUIRED_COLUMNS,
)


class ValidationError(Exception):
    """Raised when input data fails validation."""


@dataclass(frozen=True)
class ValidationResult:
    """Summary of a successful validation run."""

    parquet_path: str
    row_count: int
    checks_run: tuple[str, ...]
    execution_time_seconds: float


def validate_parquet(parquet_path: str | Path) -> ValidationResult:
    """Run all validation checks against a Parquet file."""
    parquet_path = Path(parquet_path)
    start_time = time.perf_counter()

    validate_required_columns(parquet_path)
    validate_column_types(parquet_path)
    validate_nulls(parquet_path)
    validate_composite_uniqueness(parquet_path)

    metadata = pq.read_metadata(parquet_path)
    row_count = metadata.num_rows

    execution_time = time.perf_counter() - start_time

    return ValidationResult(
        parquet_path=str(parquet_path),
        row_count=row_count,
        checks_run=(
            "required_columns",
            "column_types",
            "nulls",
            "composite_uniqueness",
        ),
        execution_time_seconds=execution_time,
    )


def validate_required_columns(parquet_path: str | Path) -> None:
    """Validate that a Parquet file contains all required columns."""
    parquet_path = Path(parquet_path)

    schema = pq.read_schema(parquet_path)
    actual_columns = set(schema.names)

    missing_columns = REQUIRED_COLUMNS - actual_columns

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValidationError(f"Missing required columns: {missing}")


def validate_column_types(parquet_path: str | Path) -> None:
    """Validate required column data types against the expected schema."""
    parquet_path = Path(parquet_path)

    actual_schema = pq.read_schema(parquet_path)
    actual_fields = {field.name: field.type for field in actual_schema}

    for expected_field in EXPECTED_SCHEMA:
        actual_type = actual_fields.get(expected_field.name)

        if actual_type is None:
            continue

        if actual_type != expected_field.type:
            raise ValidationError(
                f"Invalid type for column '{expected_field.name}': "
                f"expected {expected_field.type}, got {actual_type}"
            )


def validate_nulls(parquet_path: str | Path) -> None:
    """Validate that required columns do not contain null values."""
    parquet_path = Path(parquet_path)

    table = pq.read_table(parquet_path, columns=sorted(REQUIRED_COLUMNS))

    for column_name in REQUIRED_COLUMNS:
        null_count = table[column_name].null_count

        if null_count > 0:
            raise ValidationError(f"Column '{column_name}' contains {null_count} null value(s)")


def validate_composite_uniqueness(parquet_path: str | Path) -> None:
    """Validate that the composite key uniquely identifies each row."""
    parquet_path = Path(parquet_path)

    key_columns = ", ".join(COMPOSITE_KEY)

    query = f"""
        SELECT
            {key_columns},
            COUNT(*) AS duplicate_count
        FROM read_parquet(?)
        GROUP BY {key_columns}
        HAVING COUNT(*) > 1
        LIMIT 1
    """

    with duckdb.connect() as connection:
        duplicate = connection.execute(
            query,
            [str(parquet_path)],
        ).fetchone()

    if duplicate is not None:
        raise ValidationError("Duplicate rows found for composite key: " + ", ".join(COMPOSITE_KEY))


def validate_reference_values(
    parquet_path: str | Path,
    reference_values: dict[str, set[str]],
) -> None:
    """Validate column values against approved reference values."""
    parquet_path = Path(parquet_path)

    table = pq.read_table(
        parquet_path,
        columns=sorted(reference_values),
    )

    for column_name, allowed_values in reference_values.items():
        actual_values = {value.as_py() for value in table[column_name] if value.as_py() is not None}

        invalid_values = actual_values - allowed_values

        if invalid_values:
            invalid = ", ".join(sorted(str(value) for value in invalid_values))
            raise ValidationError(
                f"Invalid reference value(s) for column '{column_name}': {invalid}"
            )
