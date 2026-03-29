import smtplib
from email.mime.text import MIMEText

from news_ingest_pipeline.config import Config


def send_ingest_notification(
    config: Config,
    fetched: int,
    processed: int,
    failed: int,
) -> None:
    body = (
        f"Scheduled ingestion completed.\n\n"
        f"Fetched:    {fetched}\n"
        f"Processed:  {processed}\n"
        f"Failed:     {failed}\n"
    )

    msg = MIMEText(body)
    msg["Subject"] = "News Ingest Pipeline - Scheduled Run Complete"
    msg["From"] = config.smtp_user
    msg["To"] = config.notify_email

    with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
        server.starttls()
        server.login(config.smtp_user, config.smtp_password)
        server.sendmail(config.smtp_user, config.notify_email, msg.as_string())
