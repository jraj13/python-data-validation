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
