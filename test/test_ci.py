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

    # assert is a statement that checks a condition.
    # - If the condition is True → nothing happens.
    # - If the condition is False → Python raises AssertionError.

    # uuid4 string format
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        a.article_id,
    )

    # re.fullmatch(pattern, value)
	# - Returns a match object if the entire string matches the pattern.
	# - Returns None if it does not match


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
    # check if content is limited to 10 characters.

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
    # check if published_at is set to current UTC time in ISO format when missing from raw input.

def test_config_raises_when_required_env_missing(monkeypatch):
    # monkeypatch is a pytest fixture.
    # - It lets you temporarily modify environment variables during a test.
    # - Changes are isolated to this test only.

    # Clear all required env vars
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)
    monkeypatch.delenv("NEWSAPI_QUERY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    monkeypatch.delenv("NOTIFY_EMAIL", raising=False)
    # raising=False means:
    # - If the variable does not exist, do not throw an error.

    with pytest.raises(ValueError) as e:
        Config()
    # When Config() is executed, it must raise ValueError.

    msg = str(e.value)
    # This extracts the error message string.
    assert "Missing required environment variables" in msg
    assert "NEWSAPI_KEY" in msg
    assert "NEWSAPI_QUERY" in msg
    assert "DATABASE_URL" in msg
    assert "SMTP_USER" in msg
    assert "SMTP_PASSWORD" in msg
    assert "NOTIFY_EMAIL" in msg


def test_config_ok_when_required_env_present(monkeypatch):
    monkeypatch.setenv("NEWSAPI_KEY", "dummy")
    monkeypatch.setenv("NEWSAPI_QUERY", "bitcoin")
    monkeypatch.setenv("DATABASE_URL", "postgresql://dummy")
    monkeypatch.setenv("SMTP_USER", "sender@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "dummy_app_password")
    monkeypatch.setenv("NOTIFY_EMAIL", "recipient@gmail.com")

    c = Config()
    assert c.newsapi_key == "dummy"
    assert c.newsapi_query == "bitcoin"
    assert c.newsapi_base_url == "https://newsapi.org/v2/everything"
    assert c.smtp_user == "sender@gmail.com"
    assert c.notify_email == "recipient@gmail.com"
    assert c.schedule_frequency == "daily"
    assert c.schedule_time == "13:00"
    assert c.schedule_timezone == "Asia/Manila"


def test_config_raises_when_weekly_missing_day(monkeypatch):
    monkeypatch.setenv("NEWSAPI_KEY", "dummy")
    monkeypatch.setenv("NEWSAPI_QUERY", "bitcoin")
    monkeypatch.setenv("DATABASE_URL", "postgresql://dummy")
    monkeypatch.setenv("SMTP_USER", "sender@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "dummy_app_password")
    monkeypatch.setenv("NOTIFY_EMAIL", "recipient@gmail.com")
    monkeypatch.setenv("SCHEDULE_FREQUENCY", "weekly")
    monkeypatch.delenv("SCHEDULE_DAY_OF_WEEK", raising=False)

    with pytest.raises(ValueError) as e:
        Config()

    assert "SCHEDULE_DAY_OF_WEEK" in str(e.value)


def test_config_raises_when_monthly_missing_day(monkeypatch):
    monkeypatch.setenv("NEWSAPI_KEY", "dummy")
    monkeypatch.setenv("NEWSAPI_QUERY", "bitcoin")
    monkeypatch.setenv("DATABASE_URL", "postgresql://dummy")
    monkeypatch.setenv("SMTP_USER", "sender@gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "dummy_app_password")
    monkeypatch.setenv("NOTIFY_EMAIL", "recipient@gmail.com")
    monkeypatch.setenv("SCHEDULE_FREQUENCY", "monthly")
    monkeypatch.delenv("SCHEDULE_DAY_OF_MONTH", raising=False)

    with pytest.raises(ValueError) as e:
        Config()

    assert "SCHEDULE_DAY_OF_MONTH" in str(e.value)
