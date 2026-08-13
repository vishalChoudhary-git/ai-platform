# RAG Pipeline

## Overview

The RAG layer is a plugin-agnostic platform capability that converts retrieved document evidence into a grounded answer.

```text
User Query
    ↓
RAGService
    ↓
RetrievalService
    ↓
Semantic Search + Keyword Search
    ↓
RRF Fusion
    ↓
Nemotron Reranker
    ↓
Final Retrieved Chunks
    ↓
ContextBuilder
    ↓
LLMGenerator
    ↓
Grounded Answer
    +
Cited Sources
```

RAG does not contain domain-specific logic for Finance, Legal, HR, or Healthcare. Domain plugins consume the generic RAG/Knowledge capability.

## Responsibilities

### Retrieval Layer

The retrieval layer is responsible for finding relevant evidence:

- semantic vector search using pgvector
- keyword search using PostgreSQL full-text search
- Reciprocal Rank Fusion (RRF)
- Nemotron reranking

See `RETRIEVAL.md` for the retrieval architecture.

### RAG Layer

The RAG layer is responsible for:

- retrieval orchestration
- context construction
- grounded prompting
- LLM answer generation
- source attribution
- no-evidence handling

### LLM Layer

The LLM provider is responsible only for generating the final answer from the user query and retrieved context. It does not perform document retrieval.

## Components

```text
app/rag/
├── schemas.py
├── context_builder.py
├── service.py
└── llm/
    ├── base.py
    └── openai_generator.py
```

### RAGService

`RAGService.answer()` is the main orchestration entry point. It validates the query, retrieves evidence, handles empty retrieval, builds grounded context, invokes the LLM, and maps cited source references back to authoritative retrieved chunks.

## Context Construction

Retrieved chunks are converted into numbered sources before being passed to the LLM.

```text
SOURCE [1]
Document ID: ...
Page: 1
Chunk: 2

Hotel reimbursement is capped at 180 dollars per night...
```

The numbered source identifiers allow the LLM to reference evidence using `[1]`, `[2]`, and so on.

## Grounding Rules

The LLM is instructed to:

1. Answer only from the supplied sources.
2. Do not invent information.
3. Do not use knowledge outside the supplied sources.
4. State that the information was not found when the evidence is insufficient.
5. Keep answers concise and factual.
6. Cite supporting evidence using `[1]`, `[2]`, etc.

## Source Attribution

Retrieved candidates and cited sources are different concepts:

```text
Retrieved candidates
        ↓
      Top 5
        ↓
       LLM
        ↓
Answer containing [1], [3]
        ↓
Return only sources 1 and 3
```

The application owns the authoritative source metadata. The LLM is not trusted to invent document IDs, chunk IDs, or page numbers.

## No-Evidence Handling

When retrieval returns no relevant chunks, `RAGService` returns a no-evidence response and does not call the LLM.

```text
Query
 ↓
RetrievalService
 ↓
[]
 ↓
The information was not found in the supplied documents.
```

This prevents the LLM from answering from its general knowledge when the document corpus contains no supporting evidence.

## LLM Configuration

Configuration is managed centrally through `app.core.config.Settings`.

```env
OPENAI_API_KEY=...
RAG_LLM_MODEL=gpt-4.1-mini
RAG_LLM_MAX_TOKENS=500
RAG_LLM_TEMPERATURE=0.2
```

### Defaults

| Setting | Value | Purpose |
|---|---:|---|
| `RAG_LLM_MAX_TOKENS` | `500` | Keeps grounded answers concise while allowing multi-source responses |
| `RAG_LLM_TEMPERATURE` | `0.2` | Low variability for factual document-grounded answers |

## Retrieval Configuration

The current RAG retrieval policy is:

```text
candidate_top_k = 20
final_top_k     = 5
min_similarity  = 0.30
```

```text
20 vector candidates
+
20 keyword candidates
        ↓
      RRF
        ↓
20 hybrid candidates
        ↓
Nemotron reranker
        ↓
final 5 chunks
```

## Reranking

The current reranker is:

```text
OpenRouter
    ↓
nvidia/llama-nemotron-rerank-vl-1b-v2:free
```

The reranker is behind an abstraction so the provider can be replaced without changing the RAG layer.

The current implementation sends text chunks to the reranker. Its multimodal capability can be used later for page images, tables, or other visual evidence.

## Example

Run the RAG example with:

```bash
uv run python -m examples.rag.rag_example
```

Example query:

```text
What is the hotel reimbursement limit?
```

Expected behavior:

```text
The hotel reimbursement limit is capped at 180 dollars per night
for standard business travel in major cities. [1]
```

with `[1]` mapped to the supporting document chunk.

## Architecture Boundary

The platform is intentionally layered:

```text
Plugin / Feature
       ↓
   Knowledge
       ↓
     RAG
       ↓
  Retrieval
       ↓
 PostgreSQL + pgvector
```

RAG and retrieval are reusable, domain-agnostic platform capabilities. Finance, Legal, HR, and other plugins provide domain-specific instructions, tools, and workflows on top of them.

## Next Stage

The next application-facing layer is:

```text
POST /knowledge/query
```

which will call `RAGService` and expose a stable user-facing knowledge-query contract.

The Finance Agent will consume the generic knowledge/RAG capability rather than embedding retrieval logic directly inside the plugin.
