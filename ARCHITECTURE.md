# Architecture Decision Record
## news-ingest-pipeline

---

## Overview

This document explains the architectural decisions made in this project,
including why specific tools and patterns were chosen over alternatives.

---

## Pipeline Architecture
```
NewsAPI (External Source)
    ↓
Fetcher — newsapi_client.py
    ↓
Transformer — transformer.py
    ↓
Pydantic Validation — models.py
    ↓
FastAPI Layer — api.py (/ingest endpoint)
    ↓
    ├── PostgreSQL — db_writer.py (persistent storage)
    └── Upstash Kafka — kafka_writer.py (event streaming)
                            ↓
                    Downstream consumers
                    (analytics, enrichment, etc.)
```

Scheduling via APScheduler triggers the pipeline automatically.
Prometheus exposes metrics for observability.
Docker packages the service. Render handles cloud deployment.
GitHub Actions runs CI on every push.

---

## Decision 1 — Upstash Kafka over AWS Kinesis

### Options considered
- AWS Kinesis
- Upstash Kafka
- Redis Streams
- RabbitMQ

### Decision
Upstash Kafka

### Reasoning
AWS Kinesis requires an active AWS account with billing enabled.
For a personal project and learning environment, this introduces
unnecessary cost risk and setup overhead.

Upstash Kafka is fully Kafka-compatible, serverless, and has a
free tier with no credit card required. It exposes a standard
Kafka API over HTTP, which means the knowledge and patterns
transfer directly to any production Kafka environment.

Kafka is the industry standard for event streaming at scale.
Redis Streams is simpler but less recognized in data engineering
roles. RabbitMQ is better suited for task queues than event
streaming pipelines.

### Trade-off
Upstash free tier has a daily message limit (10,000 messages).
For a personal ingestion pipeline running on a small news feed,
this is not a constraint. A production system with high volume
would move to a paid Upstash plan or self-hosted Kafka.

---

## Decision 2 — PostgreSQL over MongoDB for storage

### Options considered
- PostgreSQL
- MongoDB

### Decision
Supabase

### Reasoning
Supabase provides a fully managed PostgreSQL instance with a
generous free tier, no credit card required. It includes a
web-based table editor, SQL editor, and auto-generated REST API
— useful for inspecting ingested data without a separate DB client.

Since Supabase is standard PostgreSQL under the hood, all
psycopg2 or asyncpg connection patterns work without modification.
The knowledge transfers directly to any PostgreSQL environment.

Self-hosted PostgreSQL via Docker works locally but adds
infrastructure management overhead for deployment. Railway and
Neon are valid alternatives with similar free tiers — Supabase
was chosen for its richer UI and broader community documentation.

### Trade-off
Supabase free tier pauses the database after 1 week of inactivity.
A simple keep-alive query on a schedule resolves this for a
personal project. Production workloads would use a paid plan.

---

## Decision 3 — FastAPI over Flask or Django

### Options considered
- FastAPI
- Flask
- Django REST Framework

### Decision
FastAPI

### Reasoning
FastAPI is the current industry standard for Python API services
in data and backend engineering. It provides automatic OpenAPI
documentation via Swagger, native async support, and tight
Pydantic integration — which this pipeline already uses for
schema validation.

Flask requires more boilerplate for validation and documentation.
Django is a full-framework solution that adds unnecessary overhead
for a focused pipeline service.

### Trade-off
FastAPI has a smaller community than Flask or Django for legacy
integrations, but for modern Python backend services it is the
preferred choice.

---

## Decision 4 — APScheduler over cron

### Options considered
- Linux cron
- APScheduler
- Celery Beat

### Decision
APScheduler

### Reasoning
APScheduler runs inside the Python process, which means it is
portable across local development, Docker, and Render deployment
without requiring OS-level cron configuration.

Linux cron works well on a dedicated server but does not travel
with the container. Celery Beat is powerful but introduces a
message broker dependency (Redis or RabbitMQ) that is unnecessary
for a single scheduled job.

APScheduler is the simplest correct solution for this use case.

### Trade-off
If the pipeline scaled to many scheduled jobs with complex
dependencies, Celery Beat or Airflow would be the right move.

---

## Decision 5 — Render over AWS ECS or Heroku

### Options considered
- Render
- AWS ECS / Fargate
- Heroku
- Railway

### Decision
Render

### Reasoning
Render has a free tier for Python web services, automatic deploys
from GitHub, and straightforward Docker support. It deploys a
FastAPI service with a single start command and no infrastructure
configuration.

AWS ECS is production-grade but introduces significant setup
overhead for a personal project. Heroku removed its free tier.
Railway is a valid alternative but Render has stronger Python
and Docker documentation.

### Trade-off
Render free tier spins down inactive services after inactivity.
For a scheduled pipeline this means the first request after
idle may be slow. A paid tier or a keep-alive ping resolves this.

---

## Decision 6 — Pydantic v2 for schema validation

### Options considered
- Pydantic v2
- Marshmallow
- Manual validation

### Decision
Pydantic v2

### Reasoning
Pydantic is natively integrated with FastAPI and provides
type-safe schema validation with minimal boilerplate. V2 is
significantly faster than V1 and is now the standard in
production FastAPI applications.

Marshmallow is a valid alternative but requires more
configuration. Manual validation is error-prone and not
maintainable at scale.

---

## Monitoring and Observability

Prometheus metrics are exposed via a /metrics endpoint.

Key metrics tracked:
- articles_fetched_total
- articles_inserted_total
- duplicates_skipped_total
- ingestion_errors_total
- pipeline_duration_seconds

This provides visibility into pipeline health without requiring
a full observability stack. For production scale, these metrics
would feed into Grafana dashboards or CloudWatch.

---

## What This Project Demonstrates

| Concept | Implementation |
|---|---|
| API data ingestion | NewsAPI fetcher with pagination |
| Schema validation | Pydantic v2 models |
| ETL pipeline pattern | Fetcher → Transformer → Writer |
| Event streaming | Upstash Kafka (Kafka-compatible) |
| Persistent storage | PostgreSQL with indexes |
| REST API layer | FastAPI + Swagger docs |
| Scheduling | APScheduler |
| Containerization | Docker + Docker Compose |
| CI pipeline | GitHub Actions + pytest |
| CD pipeline | Render auto-deploy from GitHub |
| Observability | Prometheus metrics |

---

## Future Considerations

- Dead letter queue for failed records
- Pydantic-based enrichment pipeline (classification, tagging)
- Grafana dashboard for Prometheus metrics
- Schema registry for Kafka topics
- GitHub Actions CD step for automated Render deploy