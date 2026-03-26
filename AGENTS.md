## Project Focus

This repository has a single focused API tracking workflow:

- [`qec_tracker.py`](qec_tracker.py) for date-windowed QEC collection via the arXiv API, SQLite storage, and CSV/JSONL/Markdown exports.
- [`bibtex_exporter.py`](bibtex_exporter.py) for filtered BibTeX exports from the local SQLite database.

## Skills

A skill is a reusable set of local instructions stored in a `SKILL.md` file. Use the project-local skills below when their trigger matches the task.

### Available skills

- `arxiv-scraper-maintenance`: Maintain the tracker, exporter, dependency setup, docs, and release workflow. Use when editing `qec_tracker.py`, `bibtex_exporter.py`, `README.md`, `requirements*.txt`, `AGENTS.md`, GitHub workflows, or the project skills. (file: `skills/arxiv-scraper-maintenance/SKILL.md`)
- `arxiv-paper-triage`: Review generated arXiv exports and shortlist papers relevant to QEC or adjacent fault-tolerant quantum computing topics. Use when analyzing `data/weekly/qec_*.csv`, `data/weekly/qec_*.jsonl`, or weekly Markdown digests, or when adding triage/filtering logic. (file: `skills/arxiv-paper-triage/SKILL.md`)

## Working Rules

- Read [`qec_tracker.py`](qec_tracker.py), [`bibtex_exporter.py`](bibtex_exporter.py), [`README.md`](README.md), and the relevant skill before making workflow changes.
- Treat `data/qec_papers.db`, `data/weekly/qec_*`, `data/weekly/*.bib`, and `data/bib_files/*.bib` as generated outputs. Do not hand-edit them.
- Prefer the local virtual environment at `.venv/` and install dependencies from `requirements.txt` and `requirements-dev.txt` as needed.
- When modifying network behavior, prefer explicit request timeouts and HTTP error handling instead of assuming arXiv will always respond cleanly.
- Preserve the CSV, JSONL, and Markdown exports from `qec_tracker.py` unless the user explicitly asks to remove one.
- Keep `bibtex_exporter.py` as the BibTeX export boundary unless the user explicitly asks to merge workflows.
- Update [`README.md`](README.md) whenever setup, usage, outputs, or limitations change.

## Environment

Bootstrap the local environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Validation

- Run `python3 -m py_compile qec_tracker.py bibtex_exporter.py` after code edits.
- Run `python3 -m pytest` after code or documentation changes that affect runtime assumptions, examples, or CI.
- Run `./.venv/bin/python qec_tracker.py` when you need a real date-windowed QEC dataset and Markdown digest.
- Run `./.venv/bin/python bibtex_exporter.py` when you need a real BibTeX export from the database.
- If a task changes source filters, output columns, or export behavior, reflect that in both the docs and the relevant skill.

## Public Release Improvements

This section lists high-priority feature improvements for the repository. These can be worked on by agents or contributors.

- Add a simple web interface or API endpoint for the tracker using Flask or FastAPI (integrate qec-tracker agent).
- [Completed] Optimize database queries and add indexing for better performance (added indexes in `qec_tracker.py` and case-insensitive filters in `bibtex_exporter.py`).
