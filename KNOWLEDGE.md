# Knowledge Feature

## Overview

The Knowledge feature is the application-facing, plugin-agnostic interface for asking questions over the indexed document corpus.

```text
POST /knowledge/query
        ↓
KnowledgeService
        ↓
RAGService
        ↓
RetrievalService
        ↓
Hybrid Retrieval + RRF
        ↓
Nemotron Reranker
        ↓
LLM
        ↓
Answer + Cited Sources
```

The Knowledge feature does not contain domain-specific logic for Finance, Legal, HR, Healthcare, or other business domains.

## Purpose

The Knowledge feature provides a stable application-level API for document-grounded question answering.

It acts as the boundary between user-facing application features and reusable RAG/retrieval platform capabilities.

## API

### Query Knowledge

```http
POST /knowledge/query
```

### Request

```json
{
  "query": "What is the hotel reimbursement limit?"
}
```

### Response

```json
{
  "answer": "The hotel reimbursement limit is capped at 180 dollars per night for standard business travel in major cities [1].",
  "sources": [
    {
      "source_index": 1,
      "chunk_id": "04a389a8-12ad-4349-8c2c-...",
      "document_id": "465c96af-be46-4edf-8427-e2d6535e082c",
      "page_number": 1,
      "chunk_index": 2,
      "text": "Hotel reimbursement is capped at 180 dollars per night for standard business travel in major cities."
    }
  ]
}
```

## Architecture

```text
                    Knowledge API
                         │
                         ▼
                ┌─────────────────┐
                │ KnowledgeService│
                └────────┬────────┘
                         │
                         ▼
                   RAGService
                         │
                         ▼
                RetrievalService
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       Vector Search            Keyword Search
          pgvector                PostgreSQL
             │                       │
             └───────────┬───────────┘
                         ▼
                    RRF Fusion
                         │
                         ▼
                  Top Candidates
                         │
                         ▼
              Nemotron Reranker
                         │
                         ▼
                  Final Context
                         │
                         ▼
                       LLM
                         │
                         ▼
                Answer + Sources
```

## Responsibilities

### Knowledge API

Responsible for:

- accepting the user query
- validating the request
- returning the application-level response
- exposing a stable `/knowledge/query` contract

### KnowledgeService

Responsible for:

- delegating the query to `RAGService`
- mapping the RAG response to the Knowledge response model

The service does not implement:

- vector search
- keyword search
- RRF
- reranking
- prompt construction
- direct LLM calls

### RAG

Responsible for:

- retrieval orchestration
- context construction
- grounded prompting
- LLM generation
- source attribution
- no-evidence handling

See `RAG.md`.

### Retrieval

Responsible for:

- semantic vector search
- keyword search
- hybrid fusion using RRF
- Nemotron reranking

See `RETRIEVAL.md`.

## Response Contract

The Knowledge feature owns its response schema instead of exposing the internal RAG schema directly.

```text
RAGResponse
     ↓
KnowledgeQueryResponse
```

This keeps the application-facing contract decoupled from the internal RAG implementation.

### Knowledge Source

Each returned source contains:

```text
source_index
chunk_id
document_id
page_number
chunk_index
text
```

## Source Attribution

Retrieved candidates and cited sources are different concepts.

```text
Retrieved Candidates
        ↓
      Final Top-K
        ↓
       LLM
        ↓
Answer references [1], [3]
        ↓
Return sources 1 and 3
```

Only sources referenced by the generated answer are returned by the Knowledge API.

The application owns authoritative source metadata.

The LLM does not generate or control document IDs, chunk IDs, page numbers, or source metadata.

## No-Evidence Handling

When retrieval does not return relevant evidence, the Knowledge feature returns the RAG no-evidence response.

Example:

```text
What is the company's maternity leave policy?
```

Response:

```json
{
  "answer": "The information was not found in the supplied documents.",
  "sources": []
}
```

The LLM is not called when retrieval returns no chunks.

This prevents the system from generating an answer from information that is not present in the supplied document corpus.

## Plugin Agnostic Design

The Knowledge feature is intentionally independent of domain plugins.

```text
Finance Plugin
      │
      ├── Knowledge
      │
      └── Domain Tools

Legal Plugin
      │
      ├── Knowledge
      │
      └── Domain Tools

HR Plugin
      │
      ├── Knowledge
      │
      └── Domain Tools
```

All plugins can consume the same generic Knowledge capability.

Domain-specific behavior belongs in the plugin or agent layer, not inside the Knowledge feature.

## Application Boundary

```text
Domain Plugin / Feature
          ↓
       Knowledge
          ↓
          RAG
          ↓
      Retrieval
          ↓
 PostgreSQL + pgvector
```

The Knowledge feature is the application-facing boundary.

RAG and Retrieval remain reusable, domain-agnostic platform capabilities.

## Validation

The Knowledge API has been validated with:

- hotel reimbursement lookup
- expense approval lookup
- multi-source professional experience query
- unsupported maternity-leave query

The unsupported query returns a no-evidence response with an empty source list.

## Example

Start the application:

```bash
uv run uvicorn app.main:create_app --factory --reload
```

Query the Knowledge API:

```bash
curl -X POST http://localhost:8000/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the hotel reimbursement limit?"}'
```

## Relationship to the Document Intelligence SDK

The Knowledge feature does not perform document preprocessing.

The SDK remains responsible for:

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

The AI Platform owns:

```text
ProcessedDocument
   ↓
Persistence
   ↓
Retrieval
   ↓
Reranking
   ↓
RAG
   ↓
Knowledge
```

The SDK must not contain application-level retrieval or Knowledge logic.

## Current Retrieval Defaults

The Knowledge feature currently uses the RAG/retrieval defaults:

```text
candidate_top_k = 20
final_top_k     = 5
min_similarity  = 0.30
```

Reranking is provided through:

```text
OpenRouter
    ↓
nvidia/llama-nemotron-rerank-vl-1b-v2:free
```

LLM generation currently uses:

```text
RAG_LLM_MODEL
RAG_LLM_MAX_TOKENS = 500
RAG_LLM_TEMPERATURE = 0.2
```

## Next Stage

The Knowledge feature is the reusable knowledge-access layer.

The next stage is the domain-specific Finance Agent, which will add finance-specific reasoning, domain tools, policy/business rules, multi-step workflows, and agent decision making.

The Finance Agent should consume Knowledge/RAG rather than reimplement retrieval.
