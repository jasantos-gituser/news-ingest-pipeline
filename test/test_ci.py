import re
import pytest

from news_ingest_pipeline.models import Article
from news_ingest_pipeline.config import Config


def test_article_from_newsapi_normalizes_fields_and_generates_id():
    raw = {
        "source": {"name": "  Gizmodo.com  "},
        "title": "  Hello  ",
        "url": "  https://example.com/x  ",
        "author": None,
        "publishedAt": "  2026-02-10T16:10:27Z  ",
        "content": None,
    }

    a = Article.from_newsapi(raw)

    assert a.source_name == "Gizmodo.com"
    assert a.title == "Hello"
    assert a.url == "https://example.com/x"
    assert a.author == ""  # None becomes ""
    assert a.content == ""  # None becomes ""
    assert a.published_at == "2026-02-10T16:10:27Z"

    # uuid4 string format
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        a.article_id,
    )


def test_article_from_newsapi_truncates_content():
    raw = {
        "source": {"name": "Test"},
        "title": "T",
        "url": "U",
        "author": "A",
        "publishedAt": "2026-01-01T00:00:00Z",
        "content": "x" * 20,
    }

    a = Article.from_newsapi(raw, max_content_chars=10)
    assert a.content == "x" * 10


def test_article_from_newsapi_sets_published_at_when_missing():
    raw = {
        "source": {"name": "Test"},
        "title": "T",
        "url": "U",
        "author": "A",
        "publishedAt": "",
        "content": "C",
    }

    a = Article.from_newsapi(raw)

    # expects something like 2026-02-22T22:15:10Z format
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", a.published_at)


def test_config_raises_when_required_env_missing(monkeypatch):
    # Clear required env vars
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)
    monkeypatch.delenv("NEWSAPI_QUERY", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("KINESIS_STREAM_NAME", raising=False)

    with pytest.raises(ValueError) as e:
        Config()

    msg = str(e.value)
    assert "Missing required environment variables" in msg
    assert "NEWSAPI_KEY" in msg
    assert "NEWSAPI_QUERY" in msg
    assert "AWS_REGION" in msg
    assert "KINESIS_STREAM_NAME" in msg


def test_config_ok_when_required_env_present(monkeypatch):
    monkeypatch.setenv("NEWSAPI_KEY", "dummy")
    monkeypatch.setenv("NEWSAPI_QUERY", "bitcoin")
    monkeypatch.setenv("AWS_REGION", "ap-southeast-1")
    monkeypatch.setenv("KINESIS_STREAM_NAME", "dummy-stream")

    c = Config()
    assert c.newsapi_key == "dummy"
    assert c.newsapi_query == "bitcoin"
    assert c.aws_region == "ap-southeast-1"
    assert c.kinesis_stream_name == "dummy-stream"
    assert c.newsapi_base_url == "https://newsapi.org/v2/everything"