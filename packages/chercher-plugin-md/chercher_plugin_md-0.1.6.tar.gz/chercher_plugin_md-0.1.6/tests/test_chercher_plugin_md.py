from chercher_plugin_md import ingest, prune
from chercher import Document

CONTENT = """
---
title: TDD
---

# TDD
And how to do it in production.
"""


def test_ingest_valid_file_with_file_uri(tmp_path):
    p = tmp_path / "test.md"
    p.write_text(CONTENT)

    uri = p.as_uri()
    documents = list(ingest(uri=uri))
    assert len(documents) == 1
    for doc in documents:
        assert isinstance(doc, Document)
        assert doc.uri == uri
        assert doc.title == p.name
        assert doc.body != ""
        assert isinstance(doc.metadata, dict)
        assert doc.hash is not None


def test_ingest_valid_file_with_relative_uri(tmp_path):
    p = tmp_path / "test.md"
    p.write_text(CONTENT)

    uri = p.as_posix()
    documents = list(ingest(uri=uri))
    assert len(documents) == 1
    for doc in documents:
        assert isinstance(doc, Document)
        assert doc.uri == p.as_uri()
        assert doc.title == p.name
        assert doc.body != ""
        assert isinstance(doc.metadata, dict)
        assert doc.hash is not None


def test_ingest_invalid_file(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text(CONTENT)

    uri = p.as_uri()
    documents = list(ingest(uri=uri))
    assert documents == []


def test_ingest_missing_file(tmp_path):
    p = tmp_path / "missingno.md"
    documents = list(ingest(uri=p.as_uri()))
    assert documents == []


def test_ingest_invalid_uri():
    uri = "https://blog/post.md"
    documents = list(ingest(uri=uri))
    assert documents == []


def test_prune_valid_file(tmp_path):
    p = tmp_path / "test.md"
    p.write_text(CONTENT)

    uri = p.as_uri()
    assert prune(uri=uri) is None


def test_prune_missing_file(tmp_path):
    p = tmp_path / "missingno.md"
    uri = p.as_uri()
    assert prune(uri=uri)


def test_prune_invalid_uri():
    uri = "https://files/file.md"
    assert prune(uri=uri) is None
