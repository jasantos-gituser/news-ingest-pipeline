from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from news_ingest_pipeline import db_writer, notifier
from news_ingest_pipeline.config import Config
from news_ingest_pipeline.models import Article
from news_ingest_pipeline.newsapi_client import fetch_articles


def run_scheduled_ingest() -> None:
    config = Config()

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

    notifier.send_ingest_notification(config, fetched_count, processed_count, failed_count)


def build_scheduler(config: Config) -> AsyncIOScheduler:
    hour, minute = config.schedule_time.split(":")
    tz = config.schedule_timezone

    if config.schedule_frequency == "daily":
        trigger = CronTrigger(hour=hour, minute=minute, timezone=tz)
    elif config.schedule_frequency == "weekly":
        trigger = CronTrigger(
            day_of_week=config.schedule_day_of_week.lower(),
            hour=hour,
            minute=minute,
            timezone=tz,
        )
    elif config.schedule_frequency == "monthly":
        trigger = CronTrigger(
            day=config.schedule_day_of_month,
            hour=hour,
            minute=minute,
            timezone=tz,
        )
    else:
        raise ValueError(f"Invalid SCHEDULE_FREQUENCY: {config.schedule_frequency}. Must be daily, weekly, or monthly.")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_scheduled_ingest, trigger)
    return scheduler
