"""Test configuration and fixtures for QEC on ArXiv tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_atom_feed():
    """Provide a minimal Atom feed with one paper and a PDF link."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>1</opensearch:totalResults>
  <entry>
    <id>http://arxiv.org/abs/2601.12345v1</id>
    <updated>2026-03-20T12:00:00Z</updated>
    <published>2026-03-20T12:00:00Z</published>
    <title>Quantum Error Correction Advances</title>
    <summary>This paper discusses advances in quantum error correction.</summary>
    <author>
      <name>John Doe</name>
    </author>
    <author>
      <name>Jane Smith</name>
    </author>
    <link rel="alternate" type="text/html" href="http://arxiv.org/abs/2601.12345v1" />
    <link rel="related" title="pdf" type="application/pdf" href="http://arxiv.org/pdf/2601.12345v1" />
    <arxiv:primary_category term="quant-ph" />
    <category term="quant-ph" />
    <category term="cs.IT" />
  </entry>
</feed>
"""


@pytest.fixture
def sample_paper_data():
    """Provide sample paper data for testing."""
    return {
        "arxiv_id": "2601.12345",
        "title": "Quantum Error Correction Advances",
        "summary": "This paper discusses advances in quantum error correction...",
        "published": "2026-03-20T12:00:00Z",
        "updated": "2026-03-20T12:00:00Z",
        "primary_category": "quant-ph",
        "categories": ["quant-ph", "cs.IT"],
        "authors": ["John Doe", "Jane Smith"],
        "abs_url": "http://arxiv.org/abs/2601.12345",
        "pdf_url": "https://arxiv.org/pdf/2601.12345v1",
        "label": "core",
        "score": 15,
    }
