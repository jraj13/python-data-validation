from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from data_validation.validators import ValidationError, validate_required_columns


def test_validate_required_columns_passes(tmp_path: Path) -> None:
    parquet_path = tmp_path / "valid.parquet"

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

    validate_required_columns(parquet_path)


def test_validate_required_columns_fails_when_column_missing(
    tmp_path: Path,
) -> None:
    parquet_path = tmp_path / "invalid.parquet"

    table = pa.table(
        {
            "model_id": ["model-a"],
            "forecast_date": [date(2026, 8, 31)],
            "location_id": ["01"],
            "horizon": [1],
        }
    )

    pq.write_table(table, parquet_path)

    with pytest.raises(ValidationError, match="value"):
        validate_required_columns(parquet_path)
