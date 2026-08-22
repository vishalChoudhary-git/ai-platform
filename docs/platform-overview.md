# Platform Overview

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

- OpenAI Embeddings
- OpenAI LLM
- OpenRouter reranking API
- NVIDIA `nvidia/llama-nemotron-rerank-vl-1b-v2:free` reranker
- Single Expense Agent with OpenAI tool calling
- LangGraph remains the planned agent runtime migration target

### Infrastructure

- Docker
- GitHub Actions

## Platform Architecture

```text
AI Knowledge Platform

React UI
   ↓
FastAPI Gateway
   ↓
Authentication / Guardrails / Rate Limiter
   ↓
Agent / RAG Runtime
   ├── Retriever
   ├── Tool Executor
   └── Memory Manager
          ↓
   Redis / PostgreSQL / External Connectors
          ↓
      Ingestion Pipeline
          ↓
   PostgreSQL + pgvector
```

## Core application flow

```text
HTTP Request
    ↓
Pydantic validation
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
Pydantic response
    ↓
JSON
```

## Retrieval + RAG

The platform provides:

- semantic vector retrieval with pgvector
- PostgreSQL keyword/full-text retrieval
- Reciprocal Rank Fusion (RRF)
- NVIDIA Nemotron reranking through OpenRouter
- grounded RAG with source attribution
- plugin-agnostic Knowledge API

### Current configuration

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

Detailed retrieval documentation remains in:

- `RETRIEVAL.md`
- `RAG.md`
- `KNOWLEDGE.md`

## SDK boundary

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

## Expense plugin architecture

The Expense plugin is deliberately domain-specific while reusing shared platform capabilities.

```text
Generic document ingestion
        ↓
Expense policy / receipt interpretation
        ↓
Expense Agent
        ↓
Decision + workflow state
```

### Expense policy

Policies are uploaded through the Expense domain:

```http
POST /plugins/expenses/policies
```

The target authorization model allows HR to publish policies. Development currently uses a temporary debug auth context until JWT authentication is available.

Policies are versioned and immutable. A new policy creates a new version rather than mutating an existing published version.

Policy processing uses shared document parsing/chunking/embedding infrastructure, extracts normalized policy rules, stores durable embeddings in PostgreSQL/pgvector, and caches the normalized policy snapshot in Redis.

### Expense evidence

```text
Receipt PDF
   ↓
Shared document ingestion
   ↓
Parsed chunks + embeddings
   ↓
Expense-specific structured extraction
   ↓
Expense evidence
   ↓
Expense Agent
```

The physical document is deduplicated by checksum at the platform document layer. `ExpenseDocument` owns the business relationship between an expense and a document.

### Expense decision flow

```text
POST /plugins/expenses
        ↓
submitted
        ↓
async document/evidence processing
        ↓
Expense Agent
        ↓
approved
   OR
information_required + manager_decision
        ↓
ExpenseApproval(PENDING)
        ↓
notification to employee + manager
```

The agent is intentionally single-agent. It can dynamically choose read-only tools instead of using a fixed hard-coded sequence.

### Status and actions

Statuses:

```text
submitted
information_required
approved
```

Required actions:

```text
none
additional_information
additional_document
manager_decision
```

### Notifications

Every completed Expense decision produces notification requests for both:

```text
employee_email
manager_email
```

An approval record is created only when manager action is actually required. Notification delivery is an infrastructure concern; Expense business logic uses a notification abstraction.

## Architecture decisions

ADR documents are maintained under `docs/adr/`.
