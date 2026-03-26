# arXiv Tracker Workflow Reference

## Current Runtime Contract

- Tracker entry point: `qec_tracker.py`
- Export entry point: `bibtex_exporter.py`
- Config: `config/qec_filters.json`
- Persistent store: `data/qec_papers.db`
- Tracker outputs:
  - `data/weekly/qec_YYYYMMDD_YYYYMMDD.csv`
  - `data/weekly/qec_YYYYMMDD_YYYYMMDD.jsonl`
  - `data/weekly/qec_YYYYMMDD_YYYYMMDD.md`
  - Monthly mode uses `data/weekly/qec_YYYY_Mon_WkN.*`
- Output labels:
  - `core`
  - `adjacent`
  - `unlikely`
- Storage rule:
  - CSV, JSONL, and Markdown exports include all scored candidates.
  - SQLite stores only `core` and `adjacent` papers.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Validation

```bash
python3 -m py_compile qec_tracker.py bibtex_exporter.py
python3 -m pytest
```

Run the tracker only when network access is intended:

```bash
./.venv/bin/python qec_tracker.py --days 7
```

Run the exporter when BibTeX output is needed:

```bash
./.venv/bin/python bibtex_exporter.py --db data/qec_papers.db --out data/weekly/qec_papers.bib
```

## Known Limitations

- The tracker depends on arXiv API availability and rate limits.
- QEC relevance labels are heuristic and may require config tuning.
- Large date windows can take longer because the tracker throttles requests intentionally.
