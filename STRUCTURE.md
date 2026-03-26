# Project Structure

Current repository layout:

```text
QEC_on_ArXiv/
├── .github/
│   ├── agents/
│   │   └── qec-tracker.agent.md
│   ├── workflows/
│   │   └── tests.yml
│   └── README.md
├── config/
│   └── qec_filters.json
├── data/
│   ├── bib_files/                  # Generated BibTeX outputs
│   ├── weekly/                     # Generated CSV / JSONL / Markdown / BibTeX outputs
│   └── qec_papers.db               # Generated SQLite database
├── examples/
│   ├── example_filtered_exports.py
│   └── example_weekly_run.py
├── skills/
│   ├── arxiv-paper-triage/
│   └── arxiv-scraper-maintenance/
├── tests/
│   ├── conftest.py
│   ├── test_bibtex_exporter.py
│   └── test_tracker.py
├── .gitignore
├── AGENTS.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── TESTING.md
├── bibtex_exporter.py
├── pytest.ini
├── qec_tracker.py
├── requirements-dev.txt
└── requirements.txt
```

## Key Files

- `qec_tracker.py`: date-windowed arXiv API collector, scorer, SQLite writer, and CSV/JSONL/Markdown exporter
- `bibtex_exporter.py`: filtered BibTeX exporter for the SQLite database
- `config/qec_filters.json`: query terms, anchor rules, and scoring terms
- `tests/test_tracker.py`: unit tests for tracker helpers, feed parsing, and exports
- `tests/test_bibtex_exporter.py`: unit tests for DB filtering and BibTeX generation

## Generated Artifacts

These paths are local outputs rather than source files:

- `data/qec_papers.db`
- `data/weekly/qec_*.csv`
- `data/weekly/qec_*.jsonl`
- `data/weekly/qec_*.md`
- `data/weekly/*.bib`
- `data/bib_files/*.bib`
- `*.log`
- `__pycache__/`
- `.venv/`

The repository ignores these paths so public commits stay focused on source, docs, and tests.
