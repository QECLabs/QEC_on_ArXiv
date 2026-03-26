# Testing Guide for QEC on arXiv

This document describes how to validate the API tracker and BibTeX exporter locally.

## Setup

Install runtime and test dependencies in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Fast Validation

Syntax-check the main entry points:

```bash
python -m py_compile qec_tracker.py bibtex_exporter.py
```

Run the test suite:

```bash
pytest
```

## Focused Test Runs

Tracker tests only:

```bash
pytest tests/test_tracker.py
```

BibTeX exporter tests only:

```bash
pytest tests/test_bibtex_exporter.py
```

Verbose output:

```bash
pytest -v
```

## Coverage

Generate a terminal coverage summary and XML report:

```bash
pytest --cov=qec_tracker --cov=bibtex_exporter --cov-report=term-missing --cov-report=xml
```

## What the Current Tests Cover

`tests/test_tracker.py` covers:

- date parsing and window resolution
- Atom feed parsing
- CSV and JSONL export serialization
- config loading
- basic database interactions

`tests/test_bibtex_exporter.py` covers:

- loading papers from SQLite
- filtered lookup by summary and author
- inclusive end-date handling
- BibTeX file generation

`tests/conftest.py` provides reusable fixtures for sample paper metadata and a minimal Atom feed.

## When to Run Real Commands

The test suite is offline. Run the real tools when you need end-to-end confirmation:

```bash
./.venv/bin/python qec_tracker.py --days 7
./.venv/bin/python bibtex_exporter.py --db data/qec_papers.db --out data/weekly/qec_papers.bib
```

Because those commands create generated artifacts, do not hand-edit the resulting files.

## CI

GitHub Actions runs the same core validation in `.github/workflows/tests.yml`:

- install runtime and dev dependencies
- `python -m py_compile qec_tracker.py bibtex_exporter.py`
- `pytest --cov=qec_tracker --cov=bibtex_exporter --cov-report=term-missing --cov-report=xml`
