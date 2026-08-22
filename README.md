# AI Platform

AI Platform is a FastAPI-based platform for document intelligence, retrieval/RAG, and plugin-specific agentic workflows.

## Core stack

- Python 3.14, FastAPI, Pydantic, SQLAlchemy
- PostgreSQL + pgvector
- Redis
- Cloudflare R2
- AI Document Intelligence SDK
- OpenAI
- OpenRouter reranking

## Current capabilities

### Knowledge / RAG

- Document ingestion, chunking, embeddings
- Semantic + keyword retrieval
- Hybrid RRF ranking
- Reranking through OpenRouter
- Grounded RAG with source attribution

### Expense Resolution Agent

The Expense plugin currently supports an end-to-end agentic resolution flow:

```text
Expense submission
    ↓
Document processing
    ↓
Structured evidence
    ↓
Applicable published policy
    ↓
Single Expense Agent + tool calling
    ↓
Approved OR information_required
    ↓
Manager approval record when manager_decision is required
    ↓
Employee + manager notification
```

The create API returns without waiting for the asynchronous resolution workflow. Read the current state with:

```http
GET /plugins/expenses/{expense_id}
```

## Quick start

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Run tests:

```bash
uv run pytest
```

## Documentation

### Platform

- [Platform overview](docs/platform-overview.md)
- [Retrieval](RETRIEVAL.md)
- [RAG](RAG.md)
- [Knowledge](KNOWLEDGE.md)

### Expense Resolution

- [Current Expense Resolution flow](docs/expense-resolution-current-flow.md)
- [Agent execution flow](docs/expense-agent-flow.md)
- [Policy architecture](docs/expense-policy-architecture.md)
- [Policy processing](docs/expense-policy-processing.md)
- [Notification architecture](docs/expense-notifications.md)

### Architecture decisions

ADR documents are maintained under `docs/adr/`.
