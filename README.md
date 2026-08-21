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
- Single Expense Agent with OpenAI tool calling
- LangGraph for the planned agent runtime migration

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
    Agent / RAG Runtime
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
- [docs/expense-resolution-current-flow.md](docs/expense-resolution-current-flow.md) — current Expense Resolution architecture
- [docs/expense-agent-flow.md](docs/expense-agent-flow.md) — developer walkthrough of the agent/tool-calling loop
- [docs/expense-policy-architecture.md](docs/expense-policy-architecture.md) — immutable policy design

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

## Expense Resolution Agent

The Expense plugin currently implements an agentic expense-resolution flow:

```text
POST /plugins/expenses
        ↓
Expense created (submitted)
        ↓
Receipt/document processing
        ↓
Structured expense evidence
        ↓
Applicable published policy
        ↓
Expense Agent tool-calling loop
        ↓
AgentDecision
   ┌────┴────────────────┐
   ▼                     ▼
approved        information_required
                         │
                         ▼
                 manager_decision
                         │
                         ▼
                 ExpenseApproval
                    (pending)
```

The create API returns the current expense resource without waiting for document parsing and agent evaluation. The final state can be read through:

```http
GET /plugins/expenses/{expense_id}
```

The current agent is intentionally single-agent. It can dynamically choose read-only tools such as expense lookup, parsed evidence lookup, policy lookup, and policy search. Manager notification/action is a separate workflow and is not performed by the agent.

### Expense Policy

Company expense policies are uploaded through the Expense domain rather than the generic document upload API:

```http
POST /plugins/expenses/policies
```

Only an authenticated HR identity will be allowed to publish policies in the target architecture. During local development, a temporary debug authentication header is used until JWT authentication is implemented.

Policies are versioned and immutable. A policy change creates a new version; previously published versions remain available for historical evaluation.

Policy processing uses the shared document ingestion pipeline for parsing/chunking/embeddings, normalizes policy rules, stores durable embeddings in PostgreSQL/pgvector, and uses Redis for hot policy snapshots/cache.

### Expense Evidence

Receipt documents follow the shared document ingestion pipeline and then receive Expense-specific structured extraction:

```text
Receipt PDF
   ↓
Document ingestion
   ↓
Parsed chunks + embeddings
   ↓
Expense evidence extraction
   ↓
Structured receipt evidence
   ↓
Expense Agent
```

The same physical document is deduplicated by checksum at the platform document layer while ExpenseDocument owns the business relationship between an expense and a document.

### Expense Statuses

```text
submitted
information_required
approved
```

Required actions currently include:

```text
none
additional_information
additional_document
manager_decision
```

### Notifications

Expense decision notifications are designed to be sent to **both the employee and manager regardless of the final expense status**.

```text
Expense decision
   ↓
Employee notification
   +
Manager notification
```

A manager approval record is created only when `manager_decision` is required. The actual notification provider is intentionally abstracted so local development can use a test/sandbox provider and production can use a transactional email provider without changing Expense business logic.

## Email Provider Options

For local development and testing, the application should depend on an internal email/notification abstraction rather than a specific provider.

Potential providers include:

| Option | Local setup | Free/current offering | Best fit |
|---|---|---|---|
| Ethereal | No Docker | Free disposable SMTP testing | Simple local capture |
| Mailtrap | No Docker | Free Email API/SMTP tier and separate Email Sandbox tier | Best cloud testing/sandbox experience |
| Resend | No Docker | Free transactional tier with 3,000 emails/month and 100/day | Simple real transactional email API |
| Brevo | No Docker | Free transactional email with 300 emails/day | Higher free volume + SMTP/API |
| Postmark | No Docker | Free developer tier with 100 emails/month | Transactional email and deliverability testing |
| Mailpit | Local/self-hosted | Free/open source | Fully local development, but requires installation/container |

Provider choice should remain outside the Expense domain. The Expense plugin should call a notification service/interface; provider-specific SMTP/API credentials belong in infrastructure configuration.

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
| ADR-009 | Expense Resolution Agent |
