from typing import Any, Dict, List, Optional

import psycopg2

from news_ingest_pipeline.models import Article


def insert_article(conn: psycopg2.extensions.connection, article: Article) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO news_ingest.articles (article_id, source_name, title, content, url, author, published_at, ingested_at)
            VALUES (%(article_id)s, %(source_name)s, %(title)s, %(content)s, %(url)s, %(author)s, %(published_at)s, %(ingested_at)s)
            ON CONFLICT (article_id) DO NOTHING
            """,
            {
                "article_id": article.article_id,
                "source_name": article.source_name,
                "title": article.title,
                "content": article.content,
                "url": article.url,
                "author": article.author,
                "published_at": article.published_at,
                "ingested_at": article.ingested_at,
            },
        )
    conn.commit()


def get_articles(
    conn: psycopg2.extensions.connection,
    from_date: Optional[Any] = None,
    to_date: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    columns = ["article_id", "source_name", "title", "content", "url", "author", "published_at", "ingested_at"]

    with conn.cursor() as cur:
        if from_date and to_date:
            cur.execute(
                f"SELECT {', '.join(columns)} FROM news_ingest.articles WHERE published_at::date >= %s AND published_at::date <= %s ORDER BY published_at DESC",
                (str(from_date), str(to_date)),
            )
        elif from_date:
            cur.execute(
                f"SELECT {', '.join(columns)} FROM news_ingest.articles WHERE published_at::date >= %s ORDER BY published_at DESC",
                (str(from_date),),
            )
        elif to_date:
            cur.execute(
                f"SELECT {', '.join(columns)} FROM news_ingest.articles WHERE published_at::date <= %s ORDER BY published_at DESC",
                (str(to_date),),
            )
        else:
            cur.execute(
                f"SELECT {', '.join(columns)} FROM news_ingest.articles ORDER BY published_at DESC"
            )

        rows = cur.fetchall()

    return [dict(zip(columns, row)) for row in rows]
