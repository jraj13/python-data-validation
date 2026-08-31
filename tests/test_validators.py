from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from data_validation.validators import (
    ValidationError,
    validate_column_types,
    validate_composite_uniqueness,
    validate_nulls,
    validate_parquet,
    validate_reference_values,
)


def test_validate_column_types_passes(tmp_path: Path) -> None:
    parquet_path = tmp_path / "valid_types.parquet"

    schema = pa.schema(
        [
            ("model_id", pa.string()),
            ("forecast_date", pa.date32()),
            ("location_id", pa.string()),
            ("horizon", pa.int64()),
            ("value", pa.float64()),
        ]
    )

    table = pa.Table.from_pylist(
        [
            {
                "model_id": "model-a",
                "forecast_date": date(2026, 8, 31),
                "location_id": "01",
                "horizon": 1,
                "value": 10.5,
            }
        ],
        schema=schema,
    )

    pq.write_table(table, parquet_path)

    validate_column_types(parquet_path)


def test_validate_column_types_fails_for_wrong_type(tmp_path: Path) -> None:
    parquet_path = tmp_path / "wrong_type.parquet"

    table = pa.table(
        {
            "model_id": ["model-a"],
            "forecast_date": [date(2026, 8, 31)],
            "location_id": ["01"],
            "horizon": ["1"],
            "value": [10.5],
        }
    )

    pq.write_table(table, parquet_path)

    with pytest.raises(
        ValidationError,
        match="Invalid type for column 'horizon'",
    ):
        validate_column_types(parquet_path)


def test_validate_nulls_passes(tmp_path: Path) -> None:
    parquet_path = tmp_path / "no_nulls.parquet"

    table = pa.table(
        {
            "model_id": ["model-a"],
            "forecast_date": [date(2026, 8, 31)],
            "location_id": ["01"],
            "horizon": [1],
            "value": [10.5],
        }
    )

    pq.write_table(table, parquet_path)

    validate_nulls(parquet_path)


def test_validate_nulls_fails_when_null_present(tmp_path: Path) -> None:
    parquet_path = tmp_path / "contains_null.parquet"

    table = pa.table(
        {
            "model_id": ["model-a", None],
            "forecast_date": [
                date(2026, 8, 31),
                date(2026, 9, 1),
            ],
            "location_id": ["01", "02"],
            "horizon": [1, 2],
            "value": [10.5, 11.5],
        }
    )

    pq.write_table(table, parquet_path)

    with pytest.raises(
        ValidationError,
        match="Column 'model_id' contains 1 null value",
    ):
        validate_nulls(parquet_path)


def test_validate_composite_uniqueness_passes(tmp_path: Path) -> None:
    parquet_path = tmp_path / "unique.parquet"

    table = pa.table(
        {
            "model_id": ["model-a", "model-a"],
            "forecast_date": [
                date(2026, 8, 31),
                date(2026, 8, 31),
            ],
            "location_id": ["01", "02"],
            "horizon": [1, 1],
            "value": [10.5, 11.5],
        }
    )

    pq.write_table(table, parquet_path)

    validate_composite_uniqueness(parquet_path)


def test_validate_composite_uniqueness_fails_for_duplicate_key(
    tmp_path: Path,
) -> None:
    parquet_path = tmp_path / "duplicate.parquet"

    table = pa.table(
        {
            "model_id": ["model-a", "model-a"],
            "forecast_date": [
                date(2026, 8, 31),
                date(2026, 8, 31),
            ],
            "location_id": ["01", "01"],
            "horizon": [1, 1],
            "value": [10.5, 99.9],
        }
    )

    pq.write_table(table, parquet_path)

    with pytest.raises(
        ValidationError,
        match="Duplicate rows found for composite key",
    ):
        validate_composite_uniqueness(parquet_path)


def test_validate_parquet_runs_all_checks(tmp_path: Path) -> None:
    parquet_path = tmp_path / "valid_dataset.parquet"

    table = pa.table(
        {
            "model_id": ["model-a", "model-a"],
            "forecast_date": [
                date(2026, 8, 31),
                date(2026, 8, 31),
            ],
            "location_id": ["01", "02"],
            "horizon": [1, 1],
            "value": [10.5, 11.5],
        }
    )

    pq.write_table(table, parquet_path)

    result = validate_parquet(parquet_path)

    assert result.parquet_path == str(parquet_path)
    assert result.checks_run == (
        "required_columns",
        "column_types",
        "nulls",
        "composite_uniqueness",
    )
    assert result.row_count == 2
    assert result.execution_time_seconds >= 0


def test_validate_parquet_stops_on_validation_error(tmp_path: Path) -> None:
    parquet_path = tmp_path / "invalid_dataset.parquet"

    table = pa.table(
        {
            "model_id": ["model-a"],
            "forecast_date": [date(2026, 8, 31)],
            "location_id": ["01"],
            "horizon": [1],
        }
    )

    pq.write_table(table, parquet_path)

    with pytest.raises(
        ValidationError,
        match="Missing required columns: value",
    ):
        validate_parquet(parquet_path)


def test_validate_reference_values_passes(tmp_path: Path) -> None:
    parquet_path = tmp_path / "valid_reference.parquet"

    table = pa.table(
        {
            "model_id": ["model-a", "model-b"],
            "forecast_date": [
                date(2026, 8, 31),
                date(2026, 8, 31),
            ],
            "location_id": ["01", "02"],
            "horizon": [1, 1],
            "value": [10.5, 11.5],
        }
    )

    pq.write_table(table, parquet_path)

    reference_values = {
        "model_id": {"model-a", "model-b"},
        "location_id": {"01", "02", "03"},
    }

    validate_reference_values(
        parquet_path,
        reference_values,
    )


def test_validate_reference_values_fails_for_unknown_value(
    tmp_path: Path,
) -> None:
    parquet_path = tmp_path / "invalid_reference.parquet"

    table = pa.table(
        {
            "model_id": ["model-a", "unknown-model"],
            "forecast_date": [
                date(2026, 8, 31),
                date(2026, 8, 31),
            ],
            "location_id": ["01", "99"],
            "horizon": [1, 1],
            "value": [10.5, 11.5],
        }
    )

    pq.write_table(table, parquet_path)

    reference_values = {
        "model_id": {"model-a", "model-b"},
        "location_id": {"01", "02", "03"},
    }

    with pytest.raises(
        ValidationError,
        match="Invalid reference value",
    ):
        validate_reference_values(
            parquet_path,
            reference_values,
        )
