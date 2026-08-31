"""Schema definitions for model output data."""

from __future__ import annotations

import pyarrow as pa

REQUIRED_COLUMNS = {
    "model_id",
    "forecast_date",
    "location_id",
    "horizon",
    "value",
}

COMPOSITE_KEY = (
    "model_id",
    "forecast_date",
    "location_id",
    "horizon",
)

EXPECTED_SCHEMA = pa.schema(
    [
        pa.field("model_id", pa.string(), nullable=False),
        pa.field("forecast_date", pa.date32(), nullable=False),
        pa.field("location_id", pa.string(), nullable=False),
        pa.field("horizon", pa.int64(), nullable=False),
        pa.field("value", pa.float64(), nullable=False),
    ]
)
