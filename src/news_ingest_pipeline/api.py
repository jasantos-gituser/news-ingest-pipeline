import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from news_ingest_pipeline import db_writer
from news_ingest_pipeline.config import Config
from news_ingest_pipeline.models import Article
from news_ingest_pipeline.newsapi_client import fetch_articles
from news_ingest_pipeline.scheduler import build_scheduler

logging.basicConfig(level=logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = Config()
    scheduler = build_scheduler(config)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest():
    try:
        config = Config()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    raw_articles = fetch_articles(config) 
    fetched_count = len(raw_articles)
    processed_count = 0
    failed_count = 0

    conn = config.get_supabase_connection()
    try:
        for raw in raw_articles:
            try:
                article = Article.from_newsapi(raw)
                db_writer.insert_article(conn, article)
                processed_count += 1
            except Exception:
                failed_count += 1
    finally:
        conn.close()

    return {
        "status": "success",
        "fetched_count": fetched_count,
        "processed_count": processed_count,
        "failed_count": failed_count,
    }


@app.get("/sample-output")
def sample_output(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    try:
        config = Config()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    conn = config.get_supabase_connection()
    try:
        articles = db_writer.get_articles(conn, from_date=from_date, to_date=to_date)
    finally:
        conn.close()

    return {"count": len(articles), "articles": articles}
