# QEC on arXiv

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)

Track quantum error correction papers on arXiv using date-bounded API queries, SQLite storage, weekly review exports, and a separate BibTeX exporter.

## Repository Overview

This repository has two user-facing entry points:

- `qec_tracker.py` queries the arXiv API, scores candidate papers for QEC relevance, stores relevant papers in SQLite, and writes review exports in CSV, JSONL, and Markdown.
- `bibtex_exporter.py` reads the SQLite database and writes BibTeX for all papers or filtered subsets.

The tracker labels papers as:

- `core`
- `adjacent`
- `unlikely`

Weekly exports include all scored candidates for review. The SQLite database stores only `core` and `adjacent` papers to keep long-term storage focused.

## Quick Start

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/<your-github-username>/QEC_on_ArXiv.git
cd QEC_on_ArXiv
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

If you want to run tests locally:

```bash
python -m pip install -r requirements-dev.txt
```

## Run the Tracker

Default run for the last 7 days:

```bash
python qec_tracker.py
```

Specific window:

```bash
python qec_tracker.py --start-date 2026-03-16 --end-date 2026-03-23
```

Longer rolling window:

```bash
python qec_tracker.py --days 14
```

Monthly batch mode:

```bash
python qec_tracker.py --month 2026-03
```

Useful options:

- `--config` to use a different filter config
- `--db` to write to a different SQLite file
- `--out-dir` to redirect generated weekly exports
- `--page-size` to change arXiv API pagination

## Tracker Outputs

By default the tracker writes:

- `data/qec_papers.db`
- `data/weekly/qec_YYYYMMDD_YYYYMMDD.csv`
- `data/weekly/qec_YYYYMMDD_YYYYMMDD.jsonl`
- `data/weekly/qec_YYYYMMDD_YYYYMMDD.md`

Monthly mode writes:

- `data/weekly/qec_YYYY_Mon_Wk1.csv`
- `data/weekly/qec_YYYY_Mon_Wk1.jsonl`
- `data/weekly/qec_YYYY_Mon_Wk1.md`

The export fields include arXiv ID, title, summary, published and updated timestamps, categories, authors, score label, source queries, abstract URL, and PDF URL when available.

## Export BibTeX

Export every paper currently stored in the database:

```bash
python bibtex_exporter.py --db data/qec_papers.db --out data/weekly/qec_papers.bib
```

Useful filters:

- `--category quant-ph`
- `--category cs.IT`
- `--start-date 2026-03-01 --end-date 2026-03-31`
- `--title-contains surface`
- `--summary-contains ldpc`
- `--author-contains gottesman`
- `--text-contains "quantum error correction"`
- `--ids-file ids.txt`

Date filters are inclusive of both the start and end date.

## Configuration

QEC search terms and category rules live in `config/qec_filters.json`.

The config currently separates:

- `categories` used for category-based arXiv queries
- `query_terms` used for keyword chunks
- `anchor_categories` and `anchor_terms` used to avoid over-scoring unrelated papers
- `core_terms`, `adjacent_terms`, and `exclude_terms` used by the scorer

Tuning this file is the main way to reduce false positives or capture adjacent topics more aggressively.

## Examples

The `examples/` directory contains small runnable examples:

- `examples/example_weekly_run.py`
- `examples/example_filtered_exports.py`

Run them from the project root with the virtual environment activated.

## Testing

Quick validation:

```bash
python -m py_compile qec_tracker.py bibtex_exporter.py
python -m pytest
```

Coverage-enabled run:

```bash
pytest --cov=qec_tracker --cov=bibtex_exporter --cov-report=term-missing --cov-report=xml
```

The current test suite includes regression coverage for:

- Atom feed parsing and PDF URL extraction
- CSV and JSONL export serialization
- BibTeX writing
- Inclusive end-date filtering in `bibtex_exporter.py`

See `TESTING.md` for more detail.

## Generated Local Artifacts

The following are generated locally and are typically not committed:

- `.venv/`
- `__pycache__/`
- `*.log`
- `data/qec_papers.db`
- `data/weekly/qec_*.csv`
- `data/weekly/qec_*.jsonl`
- `data/weekly/qec_*.md`
- `data/weekly/*.bib`
- `data/bib_files/*.bib`

## Limitations

- arXiv API availability and rate limits affect runtime.
- QEC relevance labels are heuristic and will occasionally misclassify adjacent work.
- Large windows take longer because the tracker intentionally sleeps between requests.
- Weekly exports include `unlikely` candidates for review, but the database does not retain them.

## Contributing

See `CONTRIBUTING.md` for contribution guidelines and `STRUCTURE.md` for the current repository layout.

## Citation

If you use this project in research, update the repository URL below to the final published location:

```bibtex
@software{qec_arxiv_2026,
  author = {QEC on ArXiv Contributors},
  title = {QEC on ArXiv: Quantum Error Correction Paper Tracker},
  url = {https://github.com/<your-github-username>/QEC_on_ArXiv},
  year = {2026}
}
```

## Acknowledgments

- arXiv API documentation: https://arxiv.org/help/api/

## License

This project is licensed under the MIT License. See `LICENSE`.
