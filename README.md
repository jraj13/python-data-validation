# Python Data Validation

[![CI](https://github.com/jraj13/python-data-validation/actions/workflows/ci.yml/badge.svg)](https://github.com/jraj13/python-data-validation/actions/workflows/ci.yml)

A reusable Python validation library for Parquet-based analytical datasets.

The project demonstrates production-style validation patterns using **Python, PyArrow, DuckDB, pytest, Ruff, pre-commit, and GitHub Actions**.

It is intentionally built with synthetic data and generic forecasting concepts so the repository can demonstrate reusable engineering patterns without relying on employer or client code.

---

## Features

The validator currently supports:

- Required-column validation
- Column data-type validation
- Null-value validation
- Composite-key uniqueness validation using DuckDB
- Reference / metadata value validation
- Reusable Python validation API
- Structured validation results
- Row-count and execution-time reporting
- Command-line validation
- Text and JSON CLI output
- Non-zero exit codes for validation failures
- Automated unit tests with pytest
- Ruff formatting and linting
- GitHub Actions CI

---

## Validation Flow

```text
Parquet Dataset
      |
      v
+-------------------------+
| Required Columns        |
+-------------------------+
      |
      v
+-------------------------+
| Column Types            |
+-------------------------+
      |
      v
+-------------------------+
| Null Checks             |
+-------------------------+
      |
      v
+-------------------------+
| Composite Uniqueness    |
|        DuckDB           |
+-------------------------+
      |
      v
 Validation Passed
```

The individual validators remain independently reusable, while `validate_parquet()` provides a single orchestration entry point for running the complete validation pipeline.

---

## Project Structure

```text
python-data-validation/
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   └── sample/
│       └── forecast.parquet
├── src/
│   └── data_validation/
│       ├── __init__.py
│       ├── cli.py
│       ├── schema.py
│       └── validators.py
├── tests/
│   ├── test_cli.py
│   ├── test_schema.py
│   └── test_validators.py
├── pyproject.toml
└── README.md
```

---

## Example Schema

The synthetic example dataset contains:

| Column | Type | Description |
| --- | --- | --- |
| `model_id` | string | Identifier for the model |
| `forecast_date` | date | Date the forecast was generated |
| `location_id` | string | Geographic identifier |
| `horizon` | integer | Forecast horizon |
| `value` | float | Forecast value |

The example composite key is:

```text
model_id
+ forecast_date
+ location_id
+ horizon
```

`value` is intentionally excluded from the composite key because it represents the observation associated with the record rather than part of the record's identity.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/jraj13/python-data-validation.git
cd python-data-validation
```

Create a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the package and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

---

## Command-Line Usage

The package exposes the `validate-data` command.

```bash
validate-data data/sample/forecast.parquet
```

Example output:

```text
Validation passed: data/sample/forecast.parquet
Rows validated: 2
Execution time: 0.021 seconds
Checks run:
  - required_columns
  - column_types
  - nulls
  - composite_uniqueness
```

````markdown
### JSON Output

For CI/CD pipelines, automation, and orchestration systems, validation results can also be returned as JSON:
````
```bash
validate-data data/sample/forecast.parquet --format json
```

Example:
```
{
  "status": "passed",
  "parquet_path": "data/sample/forecast.parquet",
  "row_count": 2,
  "checks_run": [
    "required_columns",
    "column_types",
    "nulls",
    "composite_uniqueness"
  ],
  "execution_time_seconds": 0.021
}
```

Validation failures also support machine-readable JSON:
```
{
  "status": "failed",
  "parquet_path": "data/sample/invalid.parquet",
  "error": "Missing required columns: value"
}
```

A validation failure returns a non-zero exit code, making the CLI suitable for use in CI/CD pipelines.

Put this after the Python Usage section:

````markdown
## Reference / Metadata Validation

Datasets can also be checked against approved reference values.
````
For example:

```python
from data_validation import validate_reference_values

reference_values = {
    "model_id": {"model-a", "model-b"},
    "location_id": {"01", "02", "03"},
}

validate_reference_values(
    "data/sample/forecast.parquet",
    reference_values,
)
```

If the dataset contains a value outside the approved reference set, validation fails with a `ValidationError`.

This pattern is useful when analytical datasets depend on controlled metadata such as model identifiers, location codes, categories, or other reference data.

Reference validation is intentionally separate from the default `validate_parquet()` pipeline because it requires an external reference source.

---

## Python Usage

The complete validation pipeline can also be called directly from Python:

```python
from data_validation import validate_parquet

result = validate_parquet("data/sample/forecast.parquet")

print(result.parquet_path)
print(result.checks_run)
```

Individual validators can also be used independently:

```python
from data_validation import (
    validate_column_types,
    validate_composite_uniqueness,
    validate_nulls,
    validate_required_columns,
)

path = "data/sample/forecast.parquet"

validate_required_columns(path)
validate_column_types(path)
validate_nulls(path)
validate_composite_uniqueness(path)
```

---

## Why DuckDB?

Composite-key validation can become expensive for large analytical datasets.

DuckDB can query Parquet directly without requiring the full dataset to first be materialized as Python objects.

The uniqueness validator performs a grouped query similar to:

```sql
SELECT
    model_id,
    forecast_date,
    location_id,
    horizon,
    COUNT(*) AS duplicate_count
FROM read_parquet(...)
GROUP BY
    model_id,
    forecast_date,
    location_id,
    horizon
HAVING COUNT(*) > 1;
```

This design demonstrates an approach that can scale beyond small in-memory Python validation workloads.

---

## Testing

Run the complete test suite:

```bash
pytest -v
```

The test suite covers:

- Valid schemas
- Missing required columns
- Correct and incorrect data types
- Null detection
- Unique composite keys
- Duplicate composite keys
- Reference / metadata validation
- Complete validation orchestration
- Row-count reporting
- Execution-time reporting
- CLI success and failure behavior
- Text CLI output
- JSON CLI success output
- JSON CLI failure output

---

## Code Quality

Format the project:

```bash
ruff format .
```

Check formatting without modifying files:

```bash
ruff format --check .
```

Run linting:

```bash
ruff check .
```

Automatically fix supported lint issues:

```bash
ruff check . --fix
```

---

## Continuous Integration

GitHub Actions automatically runs quality checks for pushes and pull requests to `main`.

The CI pipeline performs:

```text
Checkout
   |
Set up Python
   |
Install Package
   |
Ruff Format Check
   |
Ruff Lint
   |
pytest
```

This helps ensure that changes remain formatted, linted, installable, and covered by automated tests.

---

## Design Principles

This project intentionally separates:

- **Schema definition** from validation behavior
- **Individual checks** from validation orchestration
- **Library functionality** from CLI behavior
- **Data identity fields** from measured values
- **Validation logic** from test fixtures

These boundaries make the validation components easier to test, extend, and reuse in larger data engineering or orchestration workflows.

---

## Roadmap

Potential future enhancements include:

- Configuration-driven validation rules
- Reference data loaded from CSV, databases, or APIs
- Multiple-file and partitioned-dataset validation
- Detailed duplicate reporting
- File-size and Parquet metadata checks
- Performance benchmarking on larger synthetic datasets
- Memory-usage reporting
- Configurable validation severity levels
- GitHub Actions validation of uploaded datasets
- Integration examples for workflow orchestrators

---

## Technology Stack

**Python | PyArrow | Parquet | DuckDB | pytest | Ruff | pre-commit | GitHub Actions | CI/CD | Data Validation | DataOps**

---

## Purpose

This repository is an independent portfolio and learning project demonstrating reusable data-validation and DataOps engineering patterns.

All example data is synthetic. No employer or client source code or proprietary data is included.
