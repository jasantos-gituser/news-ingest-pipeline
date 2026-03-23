import os
import pytest
from news_ingest_pipeline.config import Config

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skipped in CI")
def test_supabase_connection():
    config = Config()
    conn = config.get_supabase_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT article_id, source_name, title FROM news_ingest.articles LIMIT 3;")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    assert len(rows) > 0, "No rows returned from Supabase"

    for row in rows:
        article_id, source_name, title = row
        print(f"article_id={article_id} | source_name={source_name} | title={title}")
        assert article_id is not None
        assert source_name is not None
        assert title is not None
