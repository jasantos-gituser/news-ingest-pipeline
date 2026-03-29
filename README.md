# News Ingest Pipeline

## Overview

This project implements a backend news ingestion pipeline built in
Python.

The pipeline retrieves articles from the NewsAPI Everything endpoint,
normalizes and validates the data, inserts each article into Supabase
(PostgreSQL), and publishes events to Upstash Kafka for downstream
processing. When the pipeline is triggered automatically on a schedule,
an email notification is sent to the configured recipient address.

The project demonstrates practical backend engineering concepts:

-   API data ingestion
-   data normalization and schema validation
-   backend pipeline architecture
-   Supabase (PostgreSQL) persistent storage
-   Upstash Kafka event streaming
-   FastAPI API layer for triggering the pipeline
-   scheduled ingestion with email notification
-   automated testing using pytest
-   continuous integration using GitHub Actions
-   containerization using Docker
-   cloud deployment using Render

------------------------------------------------------------------------

# Architecture Diagram

High level pipeline design

     +------------------+         +-------------------+
     |   APScheduler    |         |   Manual Trigger  |
     |  (scheduler.py)  |         |  (HTTP /ingest)   |
     +--------+---------+         +---------+---------+
              |                             |
              +-------------+---------------+
                            |
                            v
               +------------+------------+
               |          NewsAPI        |
               |      External Source    |
               +------------+------------+
                            |
                            v
                   +--------+--------+
                   |     Fetcher     |
                   | newsapi_client  |
                   +--------+--------+
                            |
                            v
                   +--------+--------+
                   |   Transformer   |
                   | normalization   |
                   | validation      |
                   +--------+--------+
                            |
                            v
                   +--------+--------+
                   |   FastAPI API   |
                   |  /ingest route  |
                   +--------+--------+
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
 +--------------+  +--------------+  +--------------+
 |   Supabase   |  | Upstash Kafka|  |    Email     |
 |  PostgreSQL  |  | Event Stream |  | Notification |
 |  (storage)   |  | (streaming)  |  | (scheduled   |
 +--------------+  +--------------+  |  runs only)  |
                                     +--------------+

------------------------------------------------------------------------

# Current Implementation Status

Implemented

-   NewsAPI article retrieval
-   normalization and cleaning
-   schema validation with Pydantic
-   UUID article identifiers
-   Docker containerization
-   pytest test coverage
-   GitHub Actions CI pipeline
-   GitHub Actions CD pipeline using Render deployment

Planned

-   FastAPI ingestion endpoints
-   Supabase (PostgreSQL) storage
-   Upstash Kafka event streaming
-   Scheduled ingestion job (APScheduler — runs inside FastAPI process,
    free on Render web service tier, no separate infrastructure needed)
-   Email notification on each scheduled run (smtplib via SMTP)

------------------------------------------------------------------------

# Data Processing Flow

Pipeline workflow

    Poll NewsAPI
        ↓
    Normalize article fields
        ↓
    Validate schema (Pydantic)
        ↓
    Generate article_id (UUID)
        ↓
    Insert into Supabase (PostgreSQL)
        ↓
    Publish to Upstash Kafka
        ↓
    Send email notification (scheduled runs only)
        ↓
    Return API response

------------------------------------------------------------------------

# Normalization Rules

The ingestion pipeline applies several cleaning rules:

-   converts null values to empty strings
-   trims leading and trailing whitespace
-   ensures published_at uses ISO 8601 UTC
-   truncates oversized article content
-   generates unique article_id using uuid4()

These steps ensure all records are safe for storage and streaming.

------------------------------------------------------------------------

# Output Schema

Example record

    {
      "article_id": "3f8e5c2a-7b91-4d8a-a2f3-5c0b7e6f9d12",
      "source_name": "Gizmodo.com",
      "title": "Major Bitcoin Miner Sells $305 Million Worth of Crypto to Fund Pivot to AI",
      "content": "Over the weekend, bitcoin miner Cango sold 4,451 bitcoin for around $305 million…",
      "url": "https://gizmodo.com/...",
      "author": "Kyle Torpey",
      "published_at": "2026-02-10T16:10:27Z",
      "ingested_at": "2026-02-22T22:15:10Z"
    }

------------------------------------------------------------------------

# Project Structure

    isentia-news-ingest-pipeline/
    │
    ├── README.md
    ├── requirements.txt
    ├── Dockerfile
    ├── .env
    │
    ├── src/
    │   └── news_ingest_pipeline/
    │       ├── main.py
    │       ├── config.py
    │       ├── newsapi_client.py
    │       ├── models.py
    │       ├── api.py
    │       ├── db_writer.py
    │       ├── kafka_writer.py
    │       └── scheduler.py
    │
    ├── test/
    │   ├── conftest.py
    │   ├── test_ci.py
    │   ├── test_smoke.py
    │   └── test_supabase_connection.py
    │
    └── .github/
        └── workflows/
            └── ci.yml

------------------------------------------------------------------------

# Requirements

-   Python 3.9+
-   NewsAPI key
-   Docker
-   Supabase account (free tier)
-   Upstash Kafka account (free tier)
-   Render account (free tier)
-   SMTP credentials (e.g., Gmail app password)

------------------------------------------------------------------------

# Environment Variables

    NEWSAPI_KEY=your_key
    NEWSAPI_QUERY=bitcoin
    DATABASE_URL=postgresql://...supabase.co:5432/postgres
    KAFKA_BOOTSTRAP_SERVERS=your-upstash-endpoint:9092
    KAFKA_SASL_USERNAME=your_username
    KAFKA_SASL_PASSWORD=your_password
    KAFKA_TOPIC=news-articles
    NOTIFY_EMAIL=recipient@example.com
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=sender@example.com
    SMTP_PASSWORD=your_app_password

------------------------------------------------------------------------

# Setup Instructions

Clone repository

    git clone https://github.com/jasantos-gituser/isentia-news-ingest-pipeline.git
    cd isentia-news-ingest-pipeline

Create environment

    python3 -m venv venv
    source venv/bin/activate

Install dependencies

    pip install -r requirements.txt

------------------------------------------------------------------------

# Running the Pipeline

Because this project uses a src layout:

    export PYTHONPATH=src
    python3 -m news_ingest_pipeline.main

------------------------------------------------------------------------

# FastAPI API Layer

FastAPI exposes the pipeline through HTTP endpoints.

Purpose

-   trigger ingestion from an API
-   query stored articles by date range
-   provide built in Swagger documentation

Endpoints

    GET  /health
    POST /ingest
    GET  /sample-output?from=YYYY-MM-DD&to=YYYY-MM-DD

The `from` and `to` query parameters filter articles by `published_at`
date range. Both parameters are optional — omitting them returns all
available articles.

Swagger documentation

    http://localhost:8000/docs

------------------------------------------------------------------------

# API Usage Examples

Start FastAPI

    uvicorn news_ingest_pipeline.api:app --reload

Health check

    curl http://localhost:8000/health

Run ingestion for a date range

    curl -X POST "http://localhost:8000/ingest?from=2026-03-01&to=2026-03-27"

Sample output for a date range

    curl "http://localhost:8000/sample-output?from=2026-03-01&to=2026-03-27"

Example response

    {
      "status": "success",
      "fetched_count": 10,
      "processed_count": 10,
      "failed_count": 0
    }

------------------------------------------------------------------------

# Scheduled Job

The pipeline runs automatically on a configured interval using
APScheduler embedded inside the FastAPI process.

After each scheduled run completes, an email notification is sent to
the address set in `NOTIFY_EMAIL`. The email includes a summary of the
run: articles fetched, inserted, and any errors encountered.

Email is sent via SMTP using Python's built-in smtplib. No third-party
email service is required. Gmail, Outlook, or any SMTP provider works
with the appropriate host, port, and credentials.

The scheduler runs as part of the same Render web service — no
additional infrastructure or paid plan is needed.

------------------------------------------------------------------------

# Continuous Integration

GitHub Actions runs automated tests.

On every push or pull request the pipeline:

-   installs dependencies
-   runs pytest
-   validates pipeline functionality

CI helps detect regressions early.

------------------------------------------------------------------------

# Continuous Deployment

Deployment target: Render

Reasons

-   strong support for Python backend services
-   simple FastAPI deployment
-   automatic GitHub deploys
-   free tier available

Example start command

    uvicorn news_ingest_pipeline.api:app --host 0.0.0.0 --port $PORT

------------------------------------------------------------------------

# Docker Usage

Build container

    docker build -t news-ingest-pipeline .

Run container

    docker run --rm --env-file .env news-ingest-pipeline

Export image

    docker save -o news-ingest-pipeline.tar news-ingest-pipeline

Load image

    docker load -i news-ingest-pipeline.tar

------------------------------------------------------------------------

# Testing Strategy

Tests implemented with pytest.

Coverage includes

-   API fetch handling
-   transformation logic
-   schema validation
-   output structure
-   Supabase connection

GitHub Actions runs tests automatically.

------------------------------------------------------------------------

# Future Improvements

-   Prometheus metrics endpoint
-   dead letter queue for failed records
-   Grafana dashboard for pipeline observability
-   article enrichment pipeline (classification, tagging)
