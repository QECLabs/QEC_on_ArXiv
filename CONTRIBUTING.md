# Contributing to QEC on ArXiv

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/QEC_on_ArXiv.git
   cd QEC_on_ArXiv
   ```

3. **Set up the development environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   python -m pip install -r requirements-dev.txt
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Guidelines

- **Python Version**: Python 3.10+
- **Code Style**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Include docstrings for all functions and classes (Google style)
- **Testing**: Run syntax checks and `pytest` before opening a PR

## Making Changes

### For Tracker/BibTeX Changes
- Test `qec_tracker.py` and `bibtex_exporter.py` with `python3 -m py_compile`
- Run `python3 -m pytest`
- Do not hand-edit generated files (`data/weekly/`, `data/bib_files/`, `data/qec_papers.db`)
- Update `README.md` if you change output formats, source filters, or filtering logic
- Add timeout parameters to network requests to handle arXiv API failures gracefully

### For Documentation
- Update `README.md` when changing setup, usage, or limitations
- Update `AGENTS.md` when modifying agent specifications
- Update skill documents in `skills/*/SKILL.md` when workflow changes

## Submitting Changes

1. **Commit** your changes with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description"
   ```

2. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to any related issues
   - Explanation of changes

## Reporting Issues

When reporting bugs or suggesting features:
- **Check existing issues** first to avoid duplicates
- **Include details**: Python version, OS, error messages
- **Minimal reproducible example**: Show steps to reproduce
- **Expected vs. actual behavior**: Be specific

## Code Review

- All PRs will be reviewed for:
  - Code quality and consistency
  - Documentation completeness
  - Potential bugs or edge cases
  - Impact on existing functionality

## Questions?

- Open an issue with the `question` label
- Check the README.md and skill documentation first

Thank you for improving QEC on ArXiv!
