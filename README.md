Built and published an open-source Python package for intelligent document parsing with support for Docling, table extraction, metadata generation, and semantic chunking.

## Platform Architecture

```text
AI Knowledge Platform

┌──────────────────────┐
│      React UI        │
└──────────┬───────────┘
           │
           ▼
    FastAPI Gateway
           │
   ┌───────┼───────────────┐
   ▼       ▼               ▼
Authentication Guardrails Rate Limiter
           │
           ▼
    LangGraph Runtime
           │
   ┌───────┼───────────────┐
   ▼       ▼               ▼
Retriever Tool Executor Memory Manager
   │       │               │
   ▼       ▼               ▼
Connector External Tools Redis/Postgres
   │
   ▼
Ingestion Pipeline
   │
   ▼
PostgreSQL + pgvector
```

## Core Flow

```text
HTTP Request
    ↓
Pydantic Validation
    ↓
API
    ↓
Service
    ↓
Repository
    ↓
PostgreSQL
    ↓
Service
    ↓
Pydantic Response
    ↓
JSON Response
```

## Retrieval + RAG

The current platform includes:

- semantic vector retrieval with pgvector
- PostgreSQL keyword retrieval
- Reciprocal Rank Fusion (RRF)
- NVIDIA Nemotron reranking through OpenRouter
- grounded RAG with source attribution
- plugin-agnostic Knowledge API

Detailed documentation:

- [RETRIEVAL.md](RETRIEVAL.md) — semantic, keyword, hybrid, and reranking pipeline
- [RAG.md](RAG.md) — grounded RAG architecture and LLM configuration
- [KNOWLEDGE.md](KNOWLEDGE.md) — application-facing Knowledge feature and API

### Knowledge API

```http
POST /knowledge/query
```

Example request:

```json
{
  "query": "What is the hotel reimbursement limit?"
}
```

The Knowledge feature is intentionally domain-agnostic. Finance, Legal, HR, and other plugins consume the generic Knowledge/RAG capabilities rather than implementing their own retrieval logic.

## SDK Boundary

The document intelligence SDK owns preprocessing:

```text
Document
  ↓
Parser
  ↓
ParsedDocument
  ↓
Chunker
  ↓
DocumentChunks
  ↓
Embeddings
  ↓
ProcessedDocument
```

The AI Platform owns persistence, retrieval, reranking, RAG, Knowledge, and agents.

## ADRs

| ADR | Purpose |
|---|---|
| ADR-001 | Platform Architecture |
| ADR-002 | Plugin & Registry System |
| ADR-003 | Knowledge Model & Database |
| ADR-004 | LLM Gateway |
| ADR-005 | Retrieval Engine |
| ADR-006 | LangGraph Runtime |
| ADR-007 | Guardrails |
| ADR-008 | Observability & Evaluation |
