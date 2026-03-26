"""Tests for qec_tracker.py functionality."""

import csv
import json
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from qec_tracker import (
    Paper,
    export_csv,
    export_jsonl,
    parse_iso_date,
    parse_feed,
    resolve_window,
    load_config,
)
from bibtex_exporter import load_papers, write_bibtex


class TestDateHandling:
    """Test date parsing and window resolution."""

    def test_parse_iso_date(self):
        """Test ISO date string parsing."""
        result = parse_iso_date("2026-03-25")
        assert result == date(2026, 3, 25)

    def test_parse_iso_date_invalid(self):
        """Test parsing invalid date raises error."""
        with pytest.raises(ValueError):
            parse_iso_date("2026/03/25")

    def test_resolve_window_default(self):
        """Test window resolution with default 7-day span."""
        class Args:
            end_date = None
            start_date = None
            days = 7

        args = Args()
        start, end = resolve_window(args)
        assert end >= start
        assert (end - start).days >= 6  # 7 days includes start and end

    def test_resolve_window_explicit_dates(self):
        """Test window resolution with explicit dates."""
        class Args:
            end_date = "2026-03-25"
            start_date = "2026-03-18"
            days = 7

        args = Args()
        start, end = resolve_window(args)
        assert start == date(2026, 3, 18)
        assert end == date(2026, 3, 25)

    def test_resolve_window_invalid_range(self):
        """Test that invalid date ranges raise error."""
        class Args:
            end_date = "2026-03-18"
            start_date = "2026-03-25"
            days = 7

        args = Args()
        with pytest.raises(ValueError):
            resolve_window(args)


class TestPaperDataclass:
    """Test the Paper dataclass."""

    def test_paper_creation(self, sample_paper_data):
        """Test creating a Paper instance."""
        paper = Paper(
            arxiv_id=sample_paper_data["arxiv_id"],
            title=sample_paper_data["title"],
            summary=sample_paper_data["summary"],
            published=sample_paper_data["published"],
            updated=sample_paper_data["updated"],
            primary_category=sample_paper_data["primary_category"],
            categories=sample_paper_data["categories"],
            authors=sample_paper_data["authors"],
            abs_url=sample_paper_data["abs_url"],
            pdf_url=sample_paper_data["pdf_url"],
            source_queries={"quantum error correction"},
        )

        assert paper.arxiv_id == "2601.12345"
        assert paper.title == "Quantum Error Correction Advances"
        assert len(paper.categories) == 2

    def test_paper_equality(self, sample_paper_data):
        """Test that papers with same arxiv_id can be compared."""
        paper1 = Paper(
            arxiv_id="2601.12345",
            title="Test Title",
            summary="",
            published="2026-03-20T00:00:00Z",
            updated="2026-03-20T00:00:00Z",
            primary_category="quant-ph",
            categories=["quant-ph"],
            authors=[],
            abs_url="",
            pdf_url="",
            source_queries=set(),
        )

        paper2 = Paper(
            arxiv_id="2601.12345",
            title="Different Title",
            summary="",
            published="2026-03-20T00:00:00Z",
            updated="2026-03-20T00:00:00Z",
            primary_category="quant-ph",
            categories=["quant-ph"],
            authors=[],
            abs_url="",
            pdf_url="",
            source_queries=set(),
        )

        # Same arxiv_id means they represent the same paper
        assert paper1.arxiv_id == paper2.arxiv_id


class TestFeedParsing:
    """Test Atom feed parsing."""

    def test_parse_feed_extracts_pdf_url(self, sample_atom_feed):
        """Test that parse_feed extracts IDs, metadata, and PDF links."""
        total, papers = parse_feed(sample_atom_feed, "keyword_chunk_1")

        assert total == 1
        assert len(papers) == 1
        paper = papers[0]
        assert paper.arxiv_id == "2601.12345"
        assert paper.abs_url == "http://arxiv.org/abs/2601.12345v1"
        assert paper.pdf_url == "https://arxiv.org/pdf/2601.12345v1"
        assert paper.primary_category == "quant-ph"
        assert paper.categories == ["quant-ph", "cs.IT"]
        assert paper.authors == ["John Doe", "Jane Smith"]
        assert paper.source_queries == {"keyword_chunk_1"}


class TestFilterConfig:
    """Test filter configuration loading."""

    def test_load_filters_file_exists(self):
        """Test loading filters from config file."""
        filters = load_config(Path("config/qec_filters.json"))
        assert "categories" in filters
        assert "query_terms" in filters
        assert len(filters["categories"]) > 0
        assert len(filters["query_terms"]) > 0

    def test_load_filters_structure(self):
        """Test that loaded filters have expected structure."""
        filters = load_config(Path("config/qec_filters.json"))
        assert isinstance(filters["categories"], list)
        assert isinstance(filters["query_terms"], list)
        assert isinstance(filters.get("anchor_categories"), list)
        assert isinstance(filters.get("anchor_terms"), list)


class TestDatabaseOperations:
    """Test database creation and operations."""

    def test_database_initialization(self, temp_dir):
        """Test that database can be created."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create papers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                arxiv_id TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                published TEXT,
                primary_category TEXT
            )
        """)
        conn.commit()

        # Verify table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_database_paper_insertion(self, temp_dir, sample_paper_data):
        """Test inserting and retrieving papers from database."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                arxiv_id TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                published TEXT,
                primary_category TEXT
            )
        """)

        # Insert sample paper
        cursor.execute("""
            INSERT INTO papers (arxiv_id, title, summary, published, primary_category)
            VALUES (?, ?, ?, ?, ?)
        """, (
            sample_paper_data["arxiv_id"],
            sample_paper_data["title"],
            sample_paper_data["summary"],
            sample_paper_data["published"],
            sample_paper_data["primary_category"],
        ))
        conn.commit()

        # Retrieve and verify
        cursor.execute("SELECT title FROM papers WHERE arxiv_id=?", (sample_paper_data["arxiv_id"],))
        result = cursor.fetchone()
        assert result[0] == sample_paper_data["title"]
        conn.close()


class TestExportFormats:
    """Test export file generation."""

    def test_csv_export_format(self, temp_dir, sample_paper_data):
        """Test that CSV export writes the expected columns and values."""
        row = {
            "label": sample_paper_data["label"],
            "arxiv_id": sample_paper_data["arxiv_id"],
            "summary": sample_paper_data["summary"],
            "updated": sample_paper_data["updated"],
            "primary_category": sample_paper_data["primary_category"],
            "categories": sample_paper_data["categories"],
            "authors": sample_paper_data["authors"],
            "source_queries": ["keyword_chunk_1"],
            "abs_url": sample_paper_data["abs_url"],
            "title": sample_paper_data["title"],
            "pdf_url": sample_paper_data["pdf_url"],
            "published": sample_paper_data["published"],
        }
        csv_path = temp_dir / "papers.csv"

        export_csv(csv_path, [row])
        with csv_path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))

        assert rows[0]["arxiv_id"] == sample_paper_data["arxiv_id"]
        assert rows[0]["title"] == sample_paper_data["title"]
        assert rows[0]["pdf_url"] == sample_paper_data["pdf_url"]
        assert rows[0]["authors"] == "John Doe; Jane Smith"
        assert rows[0]["source_queries"] == "keyword_chunk_1"

    def test_jsonl_export_format(self, temp_dir, sample_paper_data):
        """Test that JSONL export writes valid JSON rows."""
        row = {
            "label": sample_paper_data["label"],
            "arxiv_id": sample_paper_data["arxiv_id"],
            "title": sample_paper_data["title"],
            "summary": sample_paper_data["summary"],
            "published": sample_paper_data["published"],
            "updated": sample_paper_data["updated"],
            "primary_category": sample_paper_data["primary_category"],
            "categories": sample_paper_data["categories"],
            "authors": sample_paper_data["authors"],
            "abs_url": sample_paper_data["abs_url"],
            "pdf_url": sample_paper_data["pdf_url"],
            "source_queries": ["keyword_chunk_1"],
        }
        jsonl_path = temp_dir / "papers.jsonl"

        export_jsonl(jsonl_path, [row])
        parsed = json.loads(jsonl_path.read_text().strip())
        assert parsed["arxiv_id"] == sample_paper_data["arxiv_id"]
        assert parsed["title"] == sample_paper_data["title"]

    def test_export_bibtex_from_db(self, temp_dir, sample_paper_data):
        """Test that BibTeX export writes entries and matches data."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
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
            INSERT INTO papers (
                arxiv_id, title, summary, published, updated, primary_category,
                categories_json, authors_json, abs_url, pdf_url, latest_seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

        bib_path = temp_dir / "papers.bib"
        rows = load_papers(db_path)
        write_bibtex(rows, bib_path)

        text = bib_path.read_text()
        assert "@article{" in text
        assert f"% arXiv:{sample_paper_data['arxiv_id']}" in text
        assert f"journal = {{arXiv:{sample_paper_data['arxiv_id']}}}" in text
        assert sample_paper_data["arxiv_id"] in text
        assert sample_paper_data["title"] in text
        assert "author" in text
