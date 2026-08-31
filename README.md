# Python Data Validation

A reusable Python validation library for Parquet-based analytical datasets.

The project demonstrates production-style validation patterns using **Python, PyArrow, DuckDB, pytest, Ruff, pre-commit, and GitHub Actions**.

It is intentionally built with synthetic data and generic forecasting concepts so the repository can demonstrate reusable engineering patterns without relying on employer or client code.

---

## Features

The validator currently supports:

- Required-column validation
- Column data-type validation
- Null-value validation
- Composite-key uniqueness validation
- DuckDB-based Parquet querying
- Reusable Python validation API
- Command-line validation
- Automated unit tests
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
Checks run:
  - required_columns
  - column_types
  - nulls
  - composite_uniqueness
```

A validation failure returns a non-zero exit code, making the CLI suitable for use in CI/CD pipelines.

Example:

```text
Validation failed: Missing required columns: value
```

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
- Complete validation orchestration
- CLI success and failure behavior

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

- Reference / metadata validation
- Structured validation reports
- Row-count and file metadata checks
- Multiple-file validation
- JSON validation output
- Performance benchmarking
- GitHub Actions validation of uploaded datasets
- Additional DuckDB-based large-file checks

---

## Technology Stack

**Python | PyArrow | Parquet | DuckDB | pytest | Ruff | GitHub Actions | CI/CD**

---

## Purpose

This repository is an independent portfolio and learning project demonstrating reusable data-validation and DataOps engineering patterns.

All example data is synthetic. No employer or client source code or proprietary data is included.
