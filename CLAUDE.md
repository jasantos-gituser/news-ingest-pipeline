# news-ingest-pipeline — Claude Code Context

## Stack
- Python 3.8+
- FastAPI + Uvicorn
- Supabase (hosted PostgreSQL — psycopg2 or asyncpg via connection string)
- Upstash Kafka (kafka-python or confluent-kafka)
- Pydantic v2
- pytest
- Docker + Docker Compose
- Render (deployment)
- GitHub Actions (CI/CD)

## Behavior Rules

### Clarification First
Before starting any task, Claude Code must:
1. Restate the goal in one sentence to confirm understanding
2. List any ambiguities or missing context that would affect the solution
3. Ask clarifying questions if needed — wait for answers before proceeding
4. Only skip clarification for clearly unambiguous, single-step tasks

### Change Preview (Show Before Apply)
Before making any file changes, Claude Code must:
1. List every file that will be created, modified, or deleted
2. Show a summary of what changes will be made per file (not the full diff — a plain-English description)
3. Display the full proposed code/content for each affected file
4. Explicitly ask: "Do you want to apply these changes? (yes / no / modify)"
5. Wait for explicit approval before writing anything to disk
6. On decline: ask what to adjust, then re-show the updated plan before applying

This applies to: new files, edits to existing files, deletions, config changes, and Docker/CI updates.

## Code Rules
- Never fabricate XML nodes, API fields, or data not in provided samples
- Always return full files — never partial snippets
- Uploaded files take priority over assumptions
- Keep modules separated: fetcher, transformer, db_writer, kafka_writer
- One responsibility per module — no mixing ingestion and storage logic

## Commands
```bash
# Run pipeline locally
export PYTHONPATH=src
python3 -m news_ingest_pipeline.main

# Run FastAPI
uvicorn news_ingest_pipeline.api:app --reload

# Run tests
pytest tests/

# Docker
docker build -t news-ingest-pipeline .
docker run --rm --env-file .env news-ingest-pipeline
docker-compose up --build
```

## Current Status
Implemented: fetcher, transformer, Pydantic validation, Docker, pytest, CI
In progress: FastAPI layer, PostgreSQL, Upstash Kafka, Render deploy,
             APScheduler, Prometheus

## Next Priorities
1. FastAPI layer (api.py)
2. PostgreSQL storage (db_writer.py)
3. Upstash Kafka writer (kafka_writer.py)
4. Scheduled ingestion (scheduler.py)
5. Render deployment
6. Prometheus metrics