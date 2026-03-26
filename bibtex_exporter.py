#!/usr/bin/env python3
"""Export papers from data/qec_papers.db into a single BibTeX file.

Supports multiple selection modes:
- all: full DB export
- category: export by one or more categories
- date: export by published date range
- ids: export by explicit arXiv IDs listed in a file

This file is intentionally separate from qec_tracker.py, but shares
BibTeX formatting behavior.
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bibtex_exporter.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


def bibtex_escape(text: str | None) -> str:
    if text is None:
        return ""
    escaped = text.replace("\\", "\\\\")
    escaped = escaped.replace("{", "\\{")
    escaped = escaped.replace("}", "\\}")
    escaped = escaped.replace('"', '``')  # or '' but `` is common
    escaped = escaped.replace("\n", " ")
    escaped = escaped.replace("\r", " ")
    escaped = " ".join(escaped.split())  # normalize whitespace
    return escaped


def build_bibtex_entry(row: tuple) -> str:
    (arxiv_id, title, summary, published, primary_category, authors_json, abs_url, pdf_url) = row

    try:
        authors = json.loads(authors_json) if authors_json else []
    except json.JSONDecodeError:
        authors = []

    author_field = " and ".join([bibtex_escape(a) for a in authors]) if authors else ""
    year = published[:4] if published else ""
    month = published[5:7] if len(published) >= 7 else ""
    day = published[8:10] if len(published) >= 10 else ""

    # Entry key format: FirstAuthorLastname_arXivID (with dot replaced by underscore), fallback to arXivID when author unavailable
    if authors:
        first_author = authors[0].strip()
        last_name = first_author.split()[-1] if first_author else ""
    else:
        last_name = ""

    normalized_arxiv = arxiv_id.replace("/", "_").replace(".", "_")
    safe_last = ''.join(ch for ch in last_name if ch.isalnum() or ch == '_') if last_name else ''
    entry_key = f"{safe_last}_{normalized_arxiv}" if safe_last else normalized_arxiv

    # Truncate abstract to 1000 characters for readability
    truncated_summary = summary[:1000] + "..." if summary and len(summary) > 1000 else summary

    fields = [
        ("title", bibtex_escape(title)),
        ("author", author_field),
        ("year", year),
    ]
    if month:
        fields.append(("month", month))
    if day:
        fields.append(("day", day))
    fields.extend([
        ("eprint", bibtex_escape(arxiv_id)),
        ("archivePrefix", "arXiv"),
        ("primaryClass", bibtex_escape(primary_category)),
        ("url", bibtex_escape(abs_url)),
    ])

    if pdf_url:
        fields.append(("pdf", bibtex_escape(pdf_url)))
    if truncated_summary:
        fields.append(("abstract", bibtex_escape(truncated_summary)))

    body_lines = [f"  {k} = {{{v}}}," for k, v in fields if v]
    if body_lines:
        body_lines[-1] = body_lines[-1].rstrip(",")

    # Add a comment with arXiv ID
    comment = f"% arXiv:{arxiv_id}"
    journal_field = f"arXiv:{arxiv_id}"
    body_lines.insert(3, f"  journal = {{{bibtex_escape(journal_field)}}},")
    entry_lines = [comment, f"@article{{{entry_key},"] + body_lines + ["}"]
    return "\n".join(entry_lines)


def load_papers(
    db_path: Path,
    category_filters: list[str] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    arxiv_ids: set[str] | None = None,
    title_contains: str | None = None,
    summary_contains: str | None = None,
    author_contains: str | None = None,
    text_contains: str | None = None,
) -> list[tuple]:
    connection = sqlite3.connect(str(db_path))
    cursor = connection.cursor()

    where_clauses: list[str] = []
    args: list[str] = []

    if category_filters:
        placeholders = ",".join("?" for _ in category_filters)
        where_clauses.append(f"primary_category IN ({placeholders})")
        args.extend(category_filters)

    if start_date:
        where_clauses.append("published >= ?")
        args.append(start_date.isoformat())

    if end_date:
        where_clauses.append("published < ?")
        args.append((end_date + timedelta(days=1)).isoformat())

    if title_contains:
        where_clauses.append("title LIKE ? COLLATE NOCASE")
        args.append(f"%{title_contains}%")

    if summary_contains:
        where_clauses.append("summary LIKE ? COLLATE NOCASE")
        args.append(f"%{summary_contains}%")

    if author_contains:
        where_clauses.append("authors_json LIKE ? COLLATE NOCASE")
        args.append(f"%{author_contains}%")

    if text_contains:
        where_clauses.append("(title LIKE ? COLLATE NOCASE OR summary LIKE ? COLLATE NOCASE OR authors_json LIKE ? COLLATE NOCASE)")
        val = f"%{text_contains}%"
        args.extend([val, val, val])

    if arxiv_ids:
        placeholders = ",".join("?" for _ in arxiv_ids)
        where_clauses.append(f"arxiv_id IN ({placeholders})")
        args.extend(sorted(arxiv_ids))

    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    query = (
        "SELECT arxiv_id, title, summary, published, primary_category, authors_json, abs_url, pdf_url "
        "FROM papers"
        + where_sql
        + " ORDER BY published DESC"
    )

    cursor.execute(query, tuple(args))
    rows = cursor.fetchall()
    connection.close()
    return rows


def write_bibtex(rows: list[tuple], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for i, row in enumerate(rows):
            handle.write(build_bibtex_entry(row))
            if i < len(rows) - 1:
                handle.write("\n\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export BibTeX from qec_papers.db")
    parser.add_argument("--db", default="data/qec_papers.db", help="SQLite DB path")
    parser.add_argument("--out", default="data/weekly/qec_papers.bib", help="BibTeX output file")
    parser.add_argument("--category", action="append", help="Category filter (can be repeated)")
    parser.add_argument("--start-date", help="Published date start (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Published date end (YYYY-MM-DD)")
    parser.add_argument("--title-contains", help="Case-insensitive substring filter for title")
    parser.add_argument("--summary-contains", help="Case-insensitive substring filter for summary")
    parser.add_argument("--author-contains", help="Case-insensitive substring filter for author name")
    parser.add_argument("--text-contains", help="Case-insensitive substring filter applied to title OR summary OR authors")
    parser.add_argument("--ids-file", help="Path to newline-separated arXiv IDs to export")
    return parser.parse_args()


def main() -> int:
    logger.info("Starting BibTeX export")
    args = parse_args()
    db_path = Path(args.db)
    out_path = Path(args.out)

    if args.ids_file:
        ids_path = Path(args.ids_file)
        arxiv_ids = {line.strip() for line in ids_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    else:
        arxiv_ids = None

    if args.start_date:
        start_date = date.fromisoformat(args.start_date)
    else:
        start_date = None

    if args.end_date:
        end_date = date.fromisoformat(args.end_date)
    else:
        end_date = None

    rows = load_papers(
        db_path=db_path,
        category_filters=args.category,
        start_date=start_date,
        end_date=end_date,
        arxiv_ids=arxiv_ids,
        title_contains=args.title_contains,
        summary_contains=args.summary_contains,
        author_contains=args.author_contains,
        text_contains=args.text_contains,
    )

    if not rows:
        logger.warning("No matching papers found in database")
        print("No matching papers found in DB.")
        return 0

    write_bibtex(rows, out_path)
    logger.info(f"Exported {len(rows)} BibTeX entries to {out_path}")
    print(f"Wrote {len(rows)} BibTeX entries to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
