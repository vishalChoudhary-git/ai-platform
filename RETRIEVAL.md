# Retrieval Pipeline

The AI Platform retrieval layer is responsible for application-level retrieval after document preprocessing and embedding generation have completed in the AI Document Intelligence SDK.

## Architecture

```text
Document ingestion
      |
      v
AI Document Intelligence SDK
  parsing -> chunking -> embeddings
      |
      v
PostgreSQL + pgvector
      |
      +----------------------+
      |                      |
      v                      v
Vector Search          PostgreSQL FTS
      |                      |
      +----------+-----------+
                 |
                 v
            RRF Fusion
                 |
                 v
         Candidate Chunks
                 |
                 v
     Nemotron Reranker
 (OpenRouter hosted API)
                 |
                 v
          Final Top-K
                 |
                 v
               RAG
```

## Responsibilities

### SDK

The document intelligence SDK owns preprocessing:

```text
Document -> Parser -> ParsedDocument -> Chunker -> DocumentChunks -> Embeddings -> ProcessedDocument
```

The SDK also exposes the same `EmbeddingProvider` used to create an embedding for arbitrary query text.

Retrieval does **not** belong to the SDK.

### AI Platform

The AI Platform owns:

```text
ProcessedDocument
    -> PostgreSQL + pgvector
    -> query embedding
    -> vector search
    -> keyword search
    -> hybrid fusion
    -> reranking
    -> retrieved chunks
    -> RAG / LLM / Agents
```

## Semantic Retrieval

Semantic retrieval uses the SDK `EmbeddingProvider` to embed the user's query and searches `document_chunks.embedding` using pgvector cosine distance.

A configurable minimum similarity is applied. The current default is:

```text
min_similarity = 0.30
```

This is a candidate-quality threshold, not an answer-confidence threshold.

## Keyword Retrieval

Keyword retrieval uses PostgreSQL Full-Text Search over chunk text.

Natural-language queries are converted into an OR-based `tsquery` so that a query such as:

```text
What is the hotel reimbursement limit?
```

can retrieve a chunk containing `hotel` and `reimbursement` even when the exact word `limit` is not present.

Keyword scores are used for ranking only. They do not use the vector similarity threshold because they are on a different scoring scale.

## Hybrid Retrieval

Semantic and keyword rankings are combined using Reciprocal Rank Fusion (RRF):

```text
RRF contribution = 1 / (60 + rank)
```

The current smoothing constant is:

```text
RRF_K = 60
```

The hybrid layer produces a candidate pool rather than the final answer context.

## Reranking

Hybrid candidates are reranked with:

```text
nvidia/llama-nemotron-rerank-vl-1b-v2:free
```

through the OpenRouter rerank API.

The current deployment intentionally keeps the reranker outside the Render application process. This avoids loading a large reranker model into the Render free-tier instance.

The first implementation sends text chunks to the multimodal reranker. The candidate representation can later be extended to include page images or other visual document content without changing the `Reranker` abstraction.

Reranker scores are ranking signals only. No hard reranker-score threshold is currently applied.

## RetrievalService

`RetrievalService` provides three internal operations:

```text
semantic_search()
keyword_search()
hybrid_search()
```

and the production retrieval entry point:

```text
retrieve()
```

`retrieve()` performs:

```text
hybrid candidate generation
        -> reranking
        -> final top-k
```

This keeps temporary retrieval strategies out of the public HTTP API.

## Development Examples

Retrieval evaluation scripts live under:

```text
examples/retrieval/
    semantic_search.py
    keyword_search.py
    hybrid_search.py
    test_cases/
        hotel_reimbursement.json
        expense_approval.json
        alex_experience.json
```

Run them from the repository root as modules:

```bash
uv run python -m examples.retrieval.semantic_search
uv run python -m examples.retrieval.keyword_search
uv run python -m examples.retrieval.hybrid_search
```

The examples are development/evaluation tools, not permanent retrieval APIs.

## Configuration

OpenRouter configuration is centralized in `app/core/config.py` through `Settings`.

```env
OPENROUTER_API_KEY=...
OPENROUTER_SITE_URL=https://github.com/vishalChoudhary-git/ai-platform
OPENROUTER_SITE_NAME=AI Platform
OPENROUTER_RERANKER_MODEL=nvidia/llama-nemotron-rerank-vl-1b-v2:free
```

When deployed, `OPENROUTER_SITE_URL` should point to the public application URL.

## Current Retrieval Defaults

```text
min_similarity = 0.30
vector_top_k = 20
keyword_top_k = 20
candidate_top_k = 20
final_top_k = 5
RRF_K = 60
```

These are initial evaluation defaults and can be tuned later based on retrieval evaluation data.

## Evaluation Notes

The current test cases were selected to exercise different retrieval behaviors:

1. Hotel reimbursement — lexical + semantic matching with a numeric answer.
2. Expense approval — exact business rule and numeric threshold.
3. Alex Morgan experience — a case where reranking can distinguish a title/summary from the detailed Experience section.

The retrieval stack has been validated independently before proceeding to RAG.
