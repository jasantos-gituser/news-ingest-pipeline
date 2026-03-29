import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

class Config:
    def __init__(self) -> None:
        # NewsAPI configuration
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.newsapi_query = os.getenv("NEWSAPI_QUERY")
        self.newsapi_base_url = os.getenv(
            "NEWSAPI_BASE_URL",
            "https://newsapi.org/v2/everything"
        )

        # Supabase configuration
        self.database_url = os.getenv("DATABASE_URL")

        # SMTP / email configuration
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.notify_email = os.getenv("NOTIFY_EMAIL")

        # Scheduler configuration
        self.schedule_frequency = os.getenv("SCHEDULE_FREQUENCY", "daily")
        self.schedule_time = os.getenv("SCHEDULE_TIME", "13:00")
        self.schedule_timezone = os.getenv("SCHEDULE_TIMEZONE", "Asia/Manila")
        self.schedule_day_of_week = os.getenv("SCHEDULE_DAY_OF_WEEK")
        self.schedule_day_of_month = os.getenv("SCHEDULE_DAY_OF_MONTH")

        self._validate()

    def _validate(self) -> None:
        missing = []

        if not self.newsapi_key:
            missing.append("NEWSAPI_KEY")
        if not self.newsapi_query:
            missing.append("NEWSAPI_QUERY")
        if not self.database_url:
            missing.append("DATABASE_URL")
        if not self.smtp_user:
            missing.append("SMTP_USER")
        if not self.smtp_password:
            missing.append("SMTP_PASSWORD")
        if not self.notify_email:
            missing.append("NOTIFY_EMAIL")
        if self.schedule_frequency == "weekly" and not self.schedule_day_of_week:
            missing.append("SCHEDULE_DAY_OF_WEEK")
        if self.schedule_frequency == "monthly" and not self.schedule_day_of_month:
            missing.append("SCHEDULE_DAY_OF_MONTH")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def get_supabase_connection(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(self.database_url)
