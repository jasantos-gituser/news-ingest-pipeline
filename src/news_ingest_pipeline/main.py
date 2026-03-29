from news_ingest_pipeline.config import Config
from news_ingest_pipeline.newsapi_client import fetch_articles
from news_ingest_pipeline.models import Article

def main() -> None:
    config = Config()
    # print("Configuration loaded successfully")
    # print(f"NEWSAPI_QUERY={config.newsapi_query}")

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


if __name__ == "__main__":
    main()