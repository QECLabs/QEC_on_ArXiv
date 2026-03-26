---
name: arxiv-scraper-maintenance
description: Maintain and extend the QEC_on_ArXiv API tracker and BibTeX export workflows. Use when updating qec_tracker.py, bibtex_exporter.py, README.md, AGENTS.md, requirements files, GitHub workflows, or project skills; when changing arXiv API queries, exports, filtering, deduplication, storage, or error handling; or when bootstrapping the local venv and validating the tools.
---

# arXiv Tracker Maintenance

## Overview

Maintain the repository as a small API-based research tool with a separate BibTeX exporter. Preserve the current output contract unless the user asks for a workflow change.

## Workflow

1. Read `qec_tracker.py`, `bibtex_exporter.py`, `README.md`, and `AGENTS.md` first.
2. Load `references/workflow.md` when you need the current runtime contract, setup commands, or validation checklist.
3. Treat `data/qec_papers.db`, `data/weekly/qec_*`, `data/weekly/*.bib`, and `data/bib_files/*.bib` as generated artifacts, not source files.
4. Use the local `.venv` plus `requirements.txt` and `requirements-dev.txt` when dependencies are missing or execution is required.
5. Update docs in the same turn when changing setup, API queries, output columns, filters, or limitations.

## Change Guardrails

- Preserve the CSV, JSONL, and Markdown exports from `qec_tracker.py` unless the user explicitly wants a format change.
- Preserve the SQLite plus weekly export workflow from `qec_tracker.py` unless the user asks to replace it.
- Preserve `bibtex_exporter.py` as a separate export step unless the user explicitly wants to merge workflows.
- Preserve the dated filename convention unless the user asks for configurable or versioned output names.
- Prefer adding timeout and HTTP-status handling when touching `requests.get(...)`.
- Assume arXiv API responses may omit optional fields. Use defensive parsing and clear error handling instead of brittle assumptions.
- Prefer tagging or scoring papers over silently dropping rows unless the user explicitly requests hard filtering.

## Validation

- Run `python3 -m py_compile qec_tracker.py bibtex_exporter.py` after edits.
- Run `python3 -m pytest` after edits that affect code paths, tests, docs, or CI expectations.
- Run the tracker only when the task requires a real API query and network access is acceptable.
- If a real run creates dated artifacts, summarize the generated filenames and any notable issues.
- Run the BibTeX exporter when the task changes export behavior or explicitly asks for generated BibTeX output.
