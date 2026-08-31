import json
from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from data_validation.cli import main


def test_cli_passes_for_valid_parquet(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
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

    monkeypatch.setattr(
        "sys.argv",
        ["validate-data", str(parquet_path)],
    )

    exit_code = main()

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Validation passed" in captured.out
    assert "required_columns" in captured.out
    assert "composite_uniqueness" in captured.out


def test_cli_fails_for_invalid_parquet(
    tmp_path: Path,
    monkeypatch,
    capsys,
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

    monkeypatch.setattr(
        "sys.argv",
        ["validate-data", str(parquet_path)],
    )

    exit_code = main()

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Validation failed" in captured.err


def test_cli_json_output_for_valid_parquet(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    parquet_path = tmp_path / "valid_json.parquet"

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

    monkeypatch.setattr(
        "sys.argv",
        [
            "validate-data",
            str(parquet_path),
            "--format",
            "json",
        ],
    )

    exit_code = main()
    captured = capsys.readouterr()

    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == "passed"
    assert payload["parquet_path"] == str(parquet_path)
    assert payload["row_count"] == 1
    assert payload["checks_run"] == [
        "required_columns",
        "column_types",
        "nulls",
        "composite_uniqueness",
    ]
    assert payload["execution_time_seconds"] >= 0


def test_cli_json_output_for_invalid_parquet(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    parquet_path = tmp_path / "invalid_json.parquet"

    table = pa.table(
        {
            "model_id": ["model-a"],
            "forecast_date": [date(2026, 8, 31)],
            "location_id": ["01"],
            "horizon": [1],
        }
    )

    pq.write_table(table, parquet_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "validate-data",
            str(parquet_path),
            "--format",
            "json",
        ],
    )

    exit_code = main()
    captured = capsys.readouterr()

    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["status"] == "failed"
    assert payload["parquet_path"] == str(parquet_path)
    assert "Missing required columns: value" in payload["error"]
