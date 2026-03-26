#!/usr/bin/env python3

"""Collect weekly QEC-related arXiv papers and store them locally."""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import logging
import sqlite3
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('qec_tracker.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

API_URL = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
OPENSEARCH_NS = {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"}
REQUEST_DELAY_SECONDS = 5
PAGE_SIZE = 100


@dataclass
class Paper:
    arxiv_id: str
    title: str
    summary: str
    published: str
    updated: str
    primary_category: str
    categories: list[str]
    authors: list[str]
    abs_url: str
    pdf_url: str | None
    source_queries: set[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track QEC-related arXiv papers for a date window.",
    )
    parser.add_argument(
        "--config",
        default="config/qec_filters.json",
        help="Path to the QEC filter configuration JSON file.",
    )
    parser.add_argument(
        "--db",
        default="data/qec_papers.db",
        help="SQLite database path for persistent paper storage.",
    )
    parser.add_argument(
        "--out-dir",
        default="data/weekly",
        help="Directory for weekly CSV, JSONL, and Markdown exports.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to include when start/end dates are not provided.",
    )
    parser.add_argument(
        "--start-date",
        help="Inclusive start date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--end-date",
        help="Inclusive end date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=PAGE_SIZE,
        help="Number of results to request per API call.",
    )
    parser.add_argument(
        "--month",
        help="Month in YYYY-MM format. If provided, generates weekly reports for each week in the month.",
    )
    return parser.parse_args()


def parse_iso_date(raw: str) -> date:
    return datetime.strptime(raw, "%Y-%m-%d").date()


def resolve_window(args: argparse.Namespace) -> tuple[date, date]:
    end_date = parse_iso_date(args.end_date) if args.end_date else date.today()
    if args.start_date:
        start_date = parse_iso_date(args.start_date)
    else:
        if args.days < 1:
            raise ValueError("days must be at least 1")
        start_date = end_date - timedelta(days=args.days - 1)
    if start_date > end_date:
        raise ValueError("start-date must be on or before end-date")
    return start_date, end_date


def load_config(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def compact_whitespace(text: str) -> str:
    return " ".join(text.split())


def format_date_filter(start_date: date, end_date: date) -> str:
    start_stamp = start_date.strftime("%Y%m%d") + "0000"
    end_stamp = end_date.strftime("%Y%m%d") + "2359"
    return f"submittedDate:[{start_stamp} TO {end_stamp}]"


def quoted_term(term: str) -> str:
    if " " in term or "-" in term:
        return f'"{term}"'
    return term


def build_category_queries(start_date: date, end_date: date, categories: Iterable[str]) -> list[tuple[str, str]]:
    queries = []
    for category in categories:
        queries.append((f"category:{category}", f"{format_date_filter(start_date, end_date)} AND cat:{category}"))
    return queries


def chunk_terms(terms: list[str], chunk_size: int) -> list[list[str]]:
    return [terms[index:index + chunk_size] for index in range(0, len(terms), chunk_size)]


def build_keyword_queries(start_date: date, end_date: date, terms: list[str], chunk_size: int = 6) -> list[tuple[str, str]]:
    queries = []
    for index, chunk in enumerate(chunk_terms(terms, chunk_size), start=1):
        field_terms = []
        for term in chunk:
            quoted = quoted_term(term)
            field_terms.append(f"ti:{quoted}")
            field_terms.append(f"abs:{quoted}")
        joined = " OR ".join(field_terms)
        queries.append((f"keyword_chunk_{index}", f"{format_date_filter(start_date, end_date)} AND ({joined})"))
    return queries


def extract_arxiv_id(abs_url: str) -> str:
    paper_id = abs_url.rstrip("/").split("/")[-1]
    return paper_id.split("v")[0]


def extract_pdf_url(entry: ET.Element) -> str | None:
    for link in entry.findall("atom:link", ATOM_NS):
        href = link.attrib.get("href")
        if not href:
            continue
        title = link.attrib.get("title", "").lower()
        link_type = link.attrib.get("type", "").lower()
        rel = link.attrib.get("rel", "").lower()
        if title == "pdf" or link_type == "application/pdf" or (rel == "related" and "/pdf/" in href):
            return href.replace("http://", "https://", 1)
    return None


def parse_feed(xml_text: str, source_name: str) -> tuple[int, list[Paper]]:
    root = ET.fromstring(xml_text)
    total = int(root.findtext("opensearch:totalResults", namespaces=OPENSEARCH_NS, default="0"))
    papers = []
    for entry in root.findall("atom:entry", ATOM_NS):
        abs_url = entry.findtext("atom:id", default="", namespaces=ATOM_NS)
        arxiv_id = extract_arxiv_id(abs_url)
        if not arxiv_id:
            logger.warning(f"Skipping entry with invalid arXiv ID from {abs_url}")
            continue
        title = compact_whitespace(entry.findtext("atom:title", default="", namespaces=ATOM_NS))
        if not title:
            logger.warning(f"Skipping entry {arxiv_id} with no title")
            continue
        summary = compact_whitespace(entry.findtext("atom:summary", default="", namespaces=ATOM_NS))
        published = entry.findtext("atom:published", default="", namespaces=ATOM_NS)
        if not published:
            logger.warning(f"Skipping entry {arxiv_id} with no published date")
            continue
        updated = entry.findtext("atom:updated", default="", namespaces=ATOM_NS)
        primary_category_elem = entry.find("arxiv:primary_category", ATOM_NS)
        primary_category = primary_category_elem.attrib.get("term", "") if primary_category_elem is not None else ""
        categories = [node.attrib.get("term", "") for node in entry.findall("atom:category", ATOM_NS)]
        pdf_url = extract_pdf_url(entry)
        authors = [
            compact_whitespace(author.findtext("atom:name", default="", namespaces=ATOM_NS))
            for author in entry.findall("atom:author", ATOM_NS)
        ]
        if not authors:
            logger.warning(f"Skipping entry {arxiv_id} with no authors")
            continue
        papers.append(
            Paper(
                arxiv_id=arxiv_id,
                title=title,
                summary=summary,
                published=published,
                updated=updated,
                primary_category=primary_category,
                categories=categories,
                authors=authors,
                abs_url=abs_url,
                pdf_url=pdf_url,
                source_queries={source_name},
            )
        )
    return total, papers


def fetch_query(query: str, source_name: str, page_size: int) -> list[Paper]:
    session = requests.Session()
    headers = {"User-Agent": "QEC_on_ArXiv tracker"}
    collected: list[Paper] = []
    start = 0
    total = None
    while total is None or start < total:
        params = {
            "search_query": query,
            "start": start,
            "max_results": page_size,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        if start:
            time.sleep(REQUEST_DELAY_SECONDS)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = session.get(API_URL, params=params, headers=headers, timeout=60)
                response.raise_for_status()
                break
            except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Timeout on attempt {attempt + 1}, retrying in {wait_time} seconds...", file=sys.stderr)
                    time.sleep(wait_time)
                else:
                    print(f"Failed after {max_retries} attempts: {e}", file=sys.stderr)
                    raise
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}", file=sys.stderr)
                raise
        
        total, papers = parse_feed(response.text, source_name)
        collected.extend(papers)
        start += page_size
        if not papers:
            break
    return collected


def fetch_queries(queries: list[tuple[str, str]], page_size: int) -> list[Paper]:
    logger.info(f"Fetching {len(queries)} queries from arXiv API")
    papers: list[Paper] = []
    for index, (source_name, query) in enumerate(queries):
        if index:
            time.sleep(REQUEST_DELAY_SECONDS)
        try:
            papers.extend(fetch_query(query, source_name, page_size))
        except Exception as e:
            logger.error(f"Failed to fetch from {source_name}: {e}")
            # Continue with other queries
    logger.info(f"Collected {len(papers)} papers from API")
    return papers


def merge_papers(*paper_lists: list[Paper]) -> list[Paper]:
    merged: dict[str, Paper] = {}
    for papers in paper_lists:
        for paper in papers:
            if paper.arxiv_id in merged:
                merged[paper.arxiv_id].source_queries.update(paper.source_queries)
            else:
                merged[paper.arxiv_id] = paper
    return sorted(merged.values(), key=lambda paper: (paper.published, paper.arxiv_id), reverse=True)


def score_paper(paper: Paper, config: dict) -> tuple[int, str, list[str]]:
    title = paper.title.lower()
    summary = paper.summary.lower()
    score = 0
    reasons: list[str] = []
    has_anchor = paper.primary_category in config.get("anchor_categories", config["categories"]) or any(
        term in title or term in summary for term in config.get("anchor_terms", [])
    )

    for term in config["core_terms"]:
        if term in title:
            score += 4
            reasons.append(f"title:{term}")
        elif term in summary:
            score += 2
            reasons.append(f"summary:{term}")

    for term in config["adjacent_terms"]:
        if term in title:
            score += 2
            reasons.append(f"title:{term}")
        elif term in summary:
            score += 1
            reasons.append(f"summary:{term}")

    for term in config["exclude_terms"]:
        if term in title or term in summary:
            score -= 3
            reasons.append(f"exclude:{term}")

    if paper.primary_category in config["categories"]:
        score += 1
        reasons.append(f"category:{paper.primary_category}")

    if not has_anchor:
        score = min(score, 2)
        reasons.append("no-anchor")

    unique_reasons = sorted(set(reasons))
    if score >= 6:
        label = "core"
    elif score >= 3:
        label = "adjacent"
    else:
        label = "unlikely"
    return score, label, unique_reasons


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            arxiv_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            published TEXT NOT NULL,
            updated TEXT NOT NULL,
            primary_category TEXT,
            categories_json TEXT NOT NULL,
            authors_json TEXT NOT NULL,
            abs_url TEXT NOT NULL,
            pdf_url TEXT,
            latest_seen_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS weekly_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            collected_at TEXT NOT NULL,
            window_start TEXT NOT NULL,
            window_end TEXT NOT NULL,
            total_candidates INTEGER NOT NULL,
            core_count INTEGER NOT NULL,
            adjacent_count INTEGER NOT NULL,
            config_path TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS weekly_run_papers (
            run_id INTEGER NOT NULL,
            arxiv_id TEXT NOT NULL,
            label TEXT NOT NULL,
            source_queries_json TEXT NOT NULL,
            PRIMARY KEY (run_id, arxiv_id),
            FOREIGN KEY (run_id) REFERENCES weekly_runs(run_id),
            FOREIGN KEY (arxiv_id) REFERENCES papers(arxiv_id)
        )
        """
    )

    # Indexes for performance
    connection.execute("CREATE INDEX IF NOT EXISTS idx_papers_published ON papers(published)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_papers_primary_category ON papers(primary_category)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_papers_latest_seen_at ON papers(latest_seen_at)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_papers_title_ci ON papers(title COLLATE NOCASE)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_papers_summary_ci ON papers(summary COLLATE NOCASE)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_weekly_run_papers_label ON weekly_run_papers(label)")

    return connection


def upsert_papers(connection: sqlite3.Connection, papers: list[Paper]) -> None:
    seen_at = datetime.now(timezone.utc).isoformat()
    for paper in papers:
        connection.execute(
            """
            INSERT INTO papers (
                arxiv_id, title, summary, published, updated, primary_category,
                categories_json, authors_json, abs_url, pdf_url, latest_seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(arxiv_id) DO UPDATE SET
                title=excluded.title,
                summary=excluded.summary,
                published=excluded.published,
                updated=excluded.updated,
                primary_category=excluded.primary_category,
                categories_json=excluded.categories_json,
                authors_json=excluded.authors_json,
                abs_url=excluded.abs_url,
                pdf_url=excluded.pdf_url,
                latest_seen_at=excluded.latest_seen_at
            """,
            (
                paper.arxiv_id,
                paper.title,
                paper.summary,
                paper.published,
                paper.updated,
                paper.primary_category,
                json.dumps(paper.categories),
                json.dumps(paper.authors),
                paper.abs_url,
                paper.pdf_url,
                seen_at,
            ),
        )


def record_run(
    connection: sqlite3.Connection,
    start_date: date,
    end_date: date,
    config_path: str,
    scored_rows: list[dict],
) -> int:
    core_count = sum(1 for row in scored_rows if row["label"] == "core")
    adjacent_count = sum(1 for row in scored_rows if row["label"] == "adjacent")
    cursor = connection.execute(
        """
        INSERT INTO weekly_runs (
            collected_at, window_start, window_end, total_candidates,
            core_count, adjacent_count, config_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            start_date.isoformat(),
            end_date.isoformat(),
            len(scored_rows),
            core_count,
            adjacent_count,
            config_path,
        ),
    )
    run_id = cursor.lastrowid
    for row in scored_rows:
        connection.execute(
            """
            INSERT OR REPLACE INTO weekly_run_papers (
                run_id, arxiv_id, label, source_queries_json
            ) VALUES (?, ?, ?, ?)
            """,
            (
                run_id,
                row["arxiv_id"],
                row["label"],
                json.dumps(row["source_queries"]),
            ),
        )
    connection.commit()
    return int(run_id)


def export_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "label",
                "arxiv_id",
                "pdf_url",
                "title",
                "summary",
                "published",
                "updated",
                "primary_category",
                "categories",
                "authors",
                "source_queries",
                "abs_url",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "categories": "; ".join(row["categories"]),
                    "authors": "; ".join(row["authors"]),
                    "source_queries": "; ".join(row["source_queries"]),
                }
            )


def export_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def run_for_window(start_date: date, end_date: date, slug: str, args: argparse.Namespace, config: dict, config_path: Path, out_dir: Path, db_path: Path) -> None:
    logger.info(f"Starting QEC tracker run for window {start_date} to {end_date}")
    category_queries = build_category_queries(start_date, end_date, config["categories"])
    keyword_terms = config.get("query_terms", config["core_terms"] + config["adjacent_terms"])
    keyword_queries = build_keyword_queries(start_date, end_date, keyword_terms)

    category_papers = fetch_queries(category_queries, args.page_size)
    keyword_papers = fetch_queries(keyword_queries, args.page_size)
    merged_papers = merge_papers(category_papers, keyword_papers)

    # Score papers and filter to only store relevant ones (core + adjacent)
    # This prevents database bloat from storing irrelevant papers
    relevant_papers = []
    scored_rows = []
    for paper in merged_papers:
        score, label, reasons = score_paper(paper, config)
        if score >= 3:  # Keep core (≥6) and adjacent (≥3) papers
            relevant_papers.append(paper)
        scored_rows.append({
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "summary": paper.summary,
            "published": paper.published,
            "updated": paper.updated,
            "primary_category": paper.primary_category,
            "categories": paper.categories,
            "authors": paper.authors,
            "abs_url": paper.abs_url,
            "pdf_url": paper.pdf_url or "",
            "label": label,
            "source_queries": sorted(paper.source_queries),
        })

    # Sort scored rows for exports (all papers, including unlikely ones for reference)
    label_rank = {"core": 0, "adjacent": 1, "unlikely": 2}
    scored_rows.sort(key=lambda row: row["arxiv_id"], reverse=True)
    scored_rows.sort(key=lambda row: row["published"], reverse=True)
    scored_rows.sort(key=lambda row: label_rank[row["label"]])

    csv_path = out_dir / f"qec_{slug}.csv"
    jsonl_path = out_dir / f"qec_{slug}.jsonl"
    markdown_path = out_dir / f"qec_{slug}.md"

    connection = init_db(db_path)
    upsert_papers(connection, relevant_papers)
    export_csv(csv_path, scored_rows)
    export_jsonl(jsonl_path, scored_rows)
    export_markdown(markdown_path, scored_rows, start_date, end_date)
    run_id = record_run(connection, start_date, end_date, str(config_path), scored_rows)
    connection.close()

    core_count = sum(1 for row in scored_rows if row["label"] == "core")
    adjacent_count = sum(1 for row in scored_rows if row["label"] == "adjacent")
    unlikely_count = sum(1 for row in scored_rows if row["label"] == "unlikely")
    print(f"Run ID: {run_id}")
    print(f"Window: {start_date.isoformat()} to {end_date.isoformat()}")
    print(f"Candidates collected: {len(scored_rows)}")
    print(f"Core papers: {core_count}")
    print(f"Adjacent papers: {adjacent_count}")
    print(f"Unlikely papers: {unlikely_count} (filtered from database)")
    print(f"Papers stored in DB: {len(relevant_papers)}")
    print(f"DB: {db_path}")
    print(f"CSV: {csv_path}")
    print(f"JSONL: {jsonl_path}")
    print(f"Markdown: {markdown_path}")
    logger.info(f"Completed run {run_id} for {slug}: {len(scored_rows)} candidates collected, {len(relevant_papers)} papers stored in database")


def export_markdown(path: Path, rows: list[dict], start_date: date, end_date: date) -> None:
    core_rows = [row for row in rows if row["label"] == "core"]
    adjacent_rows = [row for row in rows if row["label"] == "adjacent"]
    unlikely_rows = [row for row in rows if row["label"] == "unlikely"]
    lines = [
        f"# QEC arXiv Digest ({start_date.isoformat()} to {end_date.isoformat()})",
        "",
        f"- Core papers: {len(core_rows)}",
        f"- Adjacent papers: {len(adjacent_rows)}",
        f"- Other candidates included in this digest only: {len(unlikely_rows)}",
        "",
        "## Core",
        "",
    ]
    if core_rows:
        for row in core_rows:
            lines.append(
                f"- [{row['title']}]({row['abs_url']}) | {row['arxiv_id']}"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Adjacent", ""])
    if adjacent_rows:
        for row in adjacent_rows:
            lines.append(
                f"- [{row['title']}]({row['abs_url']}) | {row['arxiv_id']}"
            )
    else:
        lines.append("- None")

    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    out_dir = Path(args.out_dir)
    db_path = Path(args.db)

    config = load_config(config_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.month:
        year, month_num = map(int, args.month.split('-'))
        month_start = date(year, month_num, 1)
        if month_num == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month_num + 1
            next_year = year
        month_end = date(next_year, next_month, 1) - timedelta(days=1)
        windows = []
        current = month_start
        while current <= month_end:
            week_end = min(current + timedelta(days=6), month_end)
            windows.append((current, week_end))
            current = week_end + timedelta(days=1)
        month_abbr = calendar.month_abbr[month_num]
        for i, (start_date, end_date) in enumerate(windows, 1):
            slug = f"{year}_{month_abbr}_Wk{i}"
            run_for_window(start_date, end_date, slug, args, config, config_path, out_dir, db_path)
            if i < len(windows):
                time.sleep(5)
    else:
        try:
            start_date, end_date = resolve_window(args)
        except ValueError as error:
            print(f"Window error: {error}", file=sys.stderr)
            return 1
        slug = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        run_for_window(start_date, end_date, slug, args, config, config_path, out_dir, db_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
