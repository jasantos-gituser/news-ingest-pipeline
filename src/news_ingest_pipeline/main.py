from news_ingest_pipeline.config import Config
from news_ingest_pipeline.newsapi_client import fetch_articles
from news_ingest_pipeline.models import Article
from news_ingest_pipeline.kinesis_writer import KinesisWriter

def main() -> None:
    config = Config()
    # print("Configuration loaded successfully")
    # print(f"NEWSAPI_QUERY={config.newsapi_query}")
    # print(f"AWS_REGION={config.aws_region}")
    # print(f"KINESIS_STREAM_NAME={config.kinesis_stream_name}")

    # fetch raw data from NewsAPI
    raw_articles = fetch_articles(config, page_size=5)

    print(f"Fetched {len(raw_articles)} articles")
    for a in raw_articles[:4]:
        print(a.get("publishedAt"), "-", a.get("title"))

    # fetched data aggregation / ingestion
    articles = [Article.from_newsapi(a) for a in raw_articles]

    print(f"Fetched raw: {len(raw_articles)}")
    print(f"Transformed: {len(articles)}")

    if articles:
    #     first = articles[0].model_dump()
    #     print(first)
        for article in articles:
           print(article.model_dump())

    # uncomment the following lines to enable Kinesis writing (make sure AWS credentials and permissions are set up correctly)
    # writer = KinesisWriter(config)

    # sent = 0
    # for article in articles:
    #     record = article.model_dump()
    #     writer.send_one(record, partition_key=article.article_id)
    #     sent += 1

    # print(f"Sent to Kinesis: {sent}")

if __name__ == "__main__":
    main()