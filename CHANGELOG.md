# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- narrowed the runtime dependency set to the current API tracker and exporter workflow
- updated repository docs, skills, and GitHub metadata to match `qec_tracker.py` and `bibtex_exporter.py`
- refreshed `.gitignore` so current generated weekly exports and BibTeX outputs stay out of public commits

### Fixed

- fixed `qec_tracker.py` Atom feed parsing so PDF URLs are extracted without crashing
- fixed inclusive end-date filtering in `bibtex_exporter.py`
- repaired `requirements-dev.txt` so test dependencies install correctly
- repaired GitHub Actions syntax and aligned CI with the current entry points
- added regression tests for feed parsing, export serialization, and inclusive date filtering

## [1.0.0] - 2026-03-25

### Added

- initial public release structure for the API-based QEC tracker
- `qec_tracker.py`: API-based weekly tracker with SQLite storage
- `bibtex_exporter.py`: standalone database-to-BibTeX exporter
- QEC paper filtering and ranking system
- support for multiple export formats (CSV, JSONL, Markdown)
- configuration system for QEC filter terms and categories
