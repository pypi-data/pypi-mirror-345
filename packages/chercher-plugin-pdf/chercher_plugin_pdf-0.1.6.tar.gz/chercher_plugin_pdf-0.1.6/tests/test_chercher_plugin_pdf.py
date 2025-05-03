from pathlib import Path
import pytest
from chercher_plugin_pdf import ingest, prune
from chercher import Document


@pytest.fixture
def sample_files():
    samples_dir = Path(__file__).parent / "samples"
    return [file.as_uri() for file in samples_dir.iterdir() if file.is_file()]


def test_ingest_valid_file(sample_files):
    for uri in sample_files:
        documents = list(ingest(uri=uri))
        assert documents != []
        for doc in documents:
            assert isinstance(doc, Document)
            assert doc.uri == uri
            assert doc.title != ""
            assert doc.body != ""
            assert isinstance(doc.metadata, dict)


def test_ingest_invalid_file(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Test")

    uri = p.as_uri()
    documents = list(ingest(uri=uri))
    assert documents == []


def test_ingest_missing_file(tmp_path):
    p = tmp_path / "missingno.epub"
    documents = list(ingest(uri=p.as_uri()))
    assert documents == []


def test_ingest_invalid_uri():
    uri = "https://www.gutenberg.org/cache/epub/11/pg11-images.html"
    documents = list(ingest(uri=uri))
    assert documents == []


def test_prune_valid_file(sample_files):
    uri = sample_files[0]
    assert prune(uri=uri) is None


def test_prune_missing_file(tmp_path):
    p = tmp_path / "missingno.pdf"
    uri = p.as_uri()
    assert prune(uri=uri)


def test_prune_invalid_uri():
    uri = "https://files/file.pdf"
    assert prune(uri=uri) is None
