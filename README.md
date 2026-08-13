Built and published an open-source Python package for intelligent document parsing with support for Docling, table extraction, metadata generation, and semantic chunking.

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy

### Document Intelligence

- AI Document Intelligence SDK
- Document parsing and preprocessing
- Chunking
- Embeddings

### Storage

- PostgreSQL
- pgvector for vector storage and semantic search
- Redis
- Cloudflare R2 for document/object storage

### AI / LLM

- OpenAI Embeddings for document and query embeddings
- OpenAI LLM for grounded RAG answer generation
- OpenRouter as the reranking API gateway
- NVIDIA `nvidia/llama-nemotron-rerank-vl-1b-v2:free` for reranking
- LangGraph for the planned agent runtime

### Retrieval

- pgvector semantic vector search
- PostgreSQL keyword/full-text search
- Reciprocal Rank Fusion (RRF)
- NVIDIA Nemotron reranking

### Infrastructure

- Docker
- GitHub Actions

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

### Current RAG Configuration

```text
LLM: OpenAI
RAG_LLM_MAX_TOKENS: 500
RAG_LLM_TEMPERATURE: 0.2

Candidate retrieval: 20
Final retrieved chunks: 5
Minimum semantic similarity: 0.30

Reranker:
nvidia/llama-nemotron-rerank-vl-1b-v2:free
```

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
