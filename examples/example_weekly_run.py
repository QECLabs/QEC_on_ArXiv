#!/usr/bin/env python3
"""
Example script: Run QEC tracker for the last 7 days and export BibTeX.

This script demonstrates basic usage of qec_tracker.py and bibtex_exporter.py.
It fetches QEC papers from the last week, stores them in the database,
and exports all papers to a BibTeX file.
"""

import subprocess
import sys
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent.parent
if not (project_root / "qec_tracker.py").exists():
    print("Error: Run this script from the examples/ directory or adjust paths.")
    sys.exit(1)

# Change to project root
import os
os.chdir(project_root)

# Activate virtual environment if it exists
venv_path = project_root / ".venv" / "bin" / "activate"
if venv_path.exists():
    print("Activating virtual environment...")
    # Note: In a real script, you'd source the venv, but for demo we assume it's active

# Run the tracker for last 7 days
print("Running QEC tracker for the last 7 days...")
result = subprocess.run([sys.executable, "qec_tracker.py"], capture_output=True, text=True)
if result.returncode != 0:
    print(f"Tracker failed: {result.stderr}")
    sys.exit(1)
print("Tracker completed successfully.")

# Export all papers to BibTeX
print("Exporting all papers to BibTeX...")
output_file = "data/weekly/example_all_papers.bib"
result = subprocess.run([sys.executable, "bibtex_exporter.py", "--out", output_file], capture_output=True, text=True)
if result.returncode != 0:
    print(f"Exporter failed: {result.stderr}")
    sys.exit(1)
print(f"BibTeX export completed: {output_file}")

print("Example completed! Check the generated files.")