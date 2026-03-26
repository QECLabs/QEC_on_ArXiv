#!/usr/bin/env python3
"""
Example script: Export BibTeX with filters.

This script demonstrates using bibtex_exporter.py with various filters
to export specific subsets of QEC papers from the database.
"""

import subprocess
import sys
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent.parent
if not (project_root / "bibtex_exporter.py").exists():
    print("Error: Run this script from the examples/ directory or adjust paths.")
    sys.exit(1)

# Change to project root
import os
os.chdir(project_root)

# Examples of filtered exports
filters = [
    ("--title-contains", "surface", "data/weekly/example_surface_code.bib"),
    ("--summary-contains", "ldpc", "data/weekly/example_ldpc.bib"),
    ("--author-contains", "gottesman", "data/weekly/example_gottesman.bib"),
    ("--text-contains", "quantum error correction", "data/weekly/example_qec_general.bib"),
]

for filter_type, value, output_file in filters:
    print(f"Exporting papers with {filter_type} '{value}' to {output_file}...")
    result = subprocess.run([sys.executable, "bibtex_exporter.py", filter_type, value, "--out", output_file], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Export failed for {filter_type} '{value}': {result.stderr}")
    else:
        print(f"Exported to {output_file}")

print("Filtered export examples completed!")