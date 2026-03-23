# News Ingest Pipeline

![CI](https://github.com/JapopoSantos/isentia-news-ingest-pipeline/actions/workflows/ci.yml/badge.svg)

## Overview

This project implements a backend news ingestion pipeline built in
Python.

The pipeline retrieves articles from the NewsAPI Everything endpoint,
normalizes and validates the data, and prepares structured records for
downstream processing.

The project demonstrates practical backend engineering concepts:

-   API data ingestion
-   data normalization and schema validation
-   backend pipeline architecture
-   automated testing using pytest
-   continuous integration using GitHub Actions
-   containerization using Docker
-   FastAPI API layer for triggering the pipeline
-   planned cloud deployment using Render
-   optional AWS Kinesis streaming integration

------------------------------------------------------------------------

# Architecture Diagram

High level pipeline design

                 +-------------------+
                 |     NewsAPI       |
                 |  External Source  |
                 +---------+---------+
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
                           v
              +------------+-------------+
              | Downstream Destination   |
              | JSON response or Kinesis |
              +--------------------------+

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

Planned

-   FastAPI ingestion endpoints
-   Render deployment
-   AWS Kinesis streaming integration

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
    Prepare structured JSON output
        ↓
    Return API response or send to downstream target

------------------------------------------------------------------------

# Normalization Rules

The ingestion pipeline applies several cleaning rules:

-   converts null values to empty strings
-   trims leading and trailing whitespace
-   ensures published_at uses ISO 8601 UTC
-   truncates oversized article content
-   generates unique article_id using uuid4()

These steps ensure all records are safe for storage or streaming.

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
    │       └── kinesis_writer.py
    │
    ├── tests/
    │   └── test_pipeline.py
    │
    └── .github/
        └── workflows/
            └── ci.yml

------------------------------------------------------------------------

# Requirements

-   Python 3.9+
-   NewsAPI key
-   Docker
-   optional AWS account for Kinesis

------------------------------------------------------------------------

# Environment Variables

    NEWSAPI_KEY=your_key
    NEWSAPI_QUERY=bitcoin
    AWS_REGION=ap-southeast-1
    KINESIS_STREAM_NAME=your_stream

------------------------------------------------------------------------

# Setup Instructions

Clone repository

    git clone https://github.com/JapopoSantos/isentia-news-ingest-pipeline.git
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
-   simplify testing
-   provide built in Swagger documentation

Endpoints

    GET /health
    POST /ingest
    GET /sample-output

Swagger documentation

    http://localhost:8000/docs

------------------------------------------------------------------------

# API Usage Examples

Start FastAPI

    uvicorn news_ingest_pipeline.api:app --reload

Health check

    curl http://localhost:8000/health

Run ingestion

    curl -X POST http://localhost:8000/ingest

Example response

    {
      "status": "success",
      "fetched_count": 10,
      "processed_count": 10,
      "failed_count": 0
    }

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

# AWS Kinesis Integration

The pipeline can send records to AWS Kinesis using boto3.

Each article is sent as a JSON record.

Partition key

    article_id

Kinesis limits

-   max record size 1 MB
-   max 500 records per batch

------------------------------------------------------------------------

# Testing Strategy

Tests implemented with pytest.

Coverage includes

-   API fetch handling
-   transformation logic
-   schema validation
-   output structure

GitHub Actions runs tests automatically.

------------------------------------------------------------------------

# Future Improvements

Possible improvements

-   enable AWS Kinesis streaming
-   scheduled ingestion jobs
-   PostgreSQL storage layer
-   ingestion monitoring
-   Prometheus metrics
-   message queue integration
