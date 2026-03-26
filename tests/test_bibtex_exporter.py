import sqlite3
import json
from pathlib import Path
from datetime import datetime, date

from bibtex_exporter import load_papers, write_bibtex


def test_load_all_papers(temp_dir, sample_paper_data):
    db_path = temp_dir / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE papers (
            arxiv_id TEXT PRIMARY KEY,
            title TEXT,
            summary TEXT,
            published TEXT,
            updated TEXT,
            primary_category TEXT,
            categories_json TEXT,
            authors_json TEXT,
            abs_url TEXT,
            pdf_url TEXT,
            latest_seen_at TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO papers (arxiv_id, title, summary, published, updated, primary_category, categories_json, authors_json, abs_url, pdf_url, latest_seen_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sample_paper_data["arxiv_id"],
            sample_paper_data["title"],
            sample_paper_data["summary"],
            sample_paper_data["published"],
            sample_paper_data["updated"],
            sample_paper_data["primary_category"],
            json.dumps(sample_paper_data["categories"]),
            json.dumps(sample_paper_data["authors"]),
            sample_paper_data["abs_url"],
            sample_paper_data["pdf_url"],
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    rows = load_papers(db_path)
    assert len(rows) == 1
    assert rows[0][0] == sample_paper_data["arxiv_id"]


def test_write_bibtex_creates_file(temp_dir, sample_paper_data):
    row = (
        sample_paper_data["arxiv_id"],
        sample_paper_data["title"],
        sample_paper_data["summary"],
        sample_paper_data["published"],
        sample_paper_data["primary_category"],
        json.dumps(sample_paper_data["authors"]),
        sample_paper_data["abs_url"],
        sample_paper_data["pdf_url"],
    )
    out_path = temp_dir / "out.bib"
    write_bibtex([row], out_path)

    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "@article{" in content
    assert f"% arXiv:{sample_paper_data['arxiv_id']}" in content
    assert f"journal = {{arXiv:{sample_paper_data['arxiv_id']}}}" in content
    assert "Doe_2601_12345" in content
    assert sample_paper_data["arxiv_id"] in content
    assert sample_paper_data["title"] in content


def test_load_by_summary_contains(temp_dir, sample_paper_data):
    db_path = temp_dir / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE papers (
            arxiv_id TEXT PRIMARY KEY,
            title TEXT,
            summary TEXT,
            published TEXT,
            updated TEXT,
            primary_category TEXT,
            categories_json TEXT,
            authors_json TEXT,
            abs_url TEXT,
            pdf_url TEXT,
            latest_seen_at TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO papers (arxiv_id, title, summary, published, updated, primary_category, categories_json, authors_json, abs_url, pdf_url, latest_seen_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sample_paper_data["arxiv_id"],
            sample_paper_data["title"],
            sample_paper_data["summary"],
            sample_paper_data["published"],
            sample_paper_data["updated"],
            sample_paper_data["primary_category"],
            json.dumps(sample_paper_data["categories"]),
            json.dumps(sample_paper_data["authors"]),
            sample_paper_data["abs_url"],
            sample_paper_data["pdf_url"],
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    rows = load_papers(db_path, summary_contains="advances")
    assert len(rows) == 1


def test_load_by_author_contains(temp_dir, sample_paper_data):
    db_path = temp_dir / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE papers (
            arxiv_id TEXT PRIMARY KEY,
            title TEXT,
            summary TEXT,
            published TEXT,
            updated TEXT,
            primary_category TEXT,
            categories_json TEXT,
            authors_json TEXT,
            abs_url TEXT,
            pdf_url TEXT,
            latest_seen_at TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO papers (arxiv_id, title, summary, published, updated, primary_category, categories_json, authors_json, abs_url, pdf_url, latest_seen_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sample_paper_data["arxiv_id"],
            sample_paper_data["title"],
            sample_paper_data["summary"],
            sample_paper_data["published"],
            sample_paper_data["updated"],
            sample_paper_data["primary_category"],
            json.dumps(sample_paper_data["categories"]),
            json.dumps(sample_paper_data["authors"]),
            sample_paper_data["abs_url"],
            sample_paper_data["pdf_url"],
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    rows = load_papers(db_path, author_contains="jane")
    assert len(rows) == 1


def test_load_by_date_range_includes_end_date_timestamp(temp_dir, sample_paper_data):
    db_path = temp_dir / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE papers (
            arxiv_id TEXT PRIMARY KEY,
            title TEXT,
            summary TEXT,
            published TEXT,
            updated TEXT,
            primary_category TEXT,
            categories_json TEXT,
            authors_json TEXT,
            abs_url TEXT,
            pdf_url TEXT,
            latest_seen_at TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO papers (arxiv_id, title, summary, published, updated, primary_category, categories_json, authors_json, abs_url, pdf_url, latest_seen_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sample_paper_data["arxiv_id"],
            sample_paper_data["title"],
            sample_paper_data["summary"],
            "2026-03-20T12:00:00Z",
            sample_paper_data["updated"],
            sample_paper_data["primary_category"],
            json.dumps(sample_paper_data["categories"]),
            json.dumps(sample_paper_data["authors"]),
            sample_paper_data["abs_url"],
            sample_paper_data["pdf_url"],
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    rows = load_papers(
        db_path,
        start_date=date(2026, 3, 20),
        end_date=date(2026, 3, 20),
    )
    assert len(rows) == 1
