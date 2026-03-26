# GitHub Configuration

This directory contains GitHub-specific configuration for the current API-based QEC tracker workflow.

## Directory Structure

### `agents/`

- `qec-tracker.agent.md` defines a Copilot-oriented helper that reads the latest weekly exports and formats paper summaries for downstream interfaces.

### `ISSUE_TEMPLATE/`

- `bug_report.yml` collects reproducible tracker, exporter, test, and docs bugs.
- `feature_request.yml` captures workflow and feature proposals.
- `config.yml` links contributors back to the README before filing.

### `workflows/`

- `tests.yml` runs syntax checks and the pytest suite on pushes and pull requests.
- The workflow currently targets Python 3.10, 3.11, and 3.12.

### `pull_request_template.md`

- Provides a small checklist for summary, validation, and follow-up notes on pull requests.

## GitHub Actions

The test workflow installs both `requirements.txt` and `requirements-dev.txt`, validates:

```bash
python -m py_compile qec_tracker.py bibtex_exporter.py
```

and then runs:

```bash
pytest --cov=qec_tracker --cov=bibtex_exporter --cov-report=term-missing --cov-report=xml
```

## Local Workflow Testing

If you use `act`, you can run the workflow locally with:

```bash
act push -W .github/workflows/tests.yml -j test
```
