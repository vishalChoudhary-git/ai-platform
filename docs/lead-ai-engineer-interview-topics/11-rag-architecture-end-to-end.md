# Topic 11 — RAG Architecture: End-to-End Pipeline

**Status:** Complete

## Focus
Ingestion, parsing, chunking, embeddings, persistence, retrieval, reranking, prompt/context construction, generation, streaming and citations.

## 1. What is RAG?

> **RAG (Retrieval-Augmented Generation) is a pattern where we retrieve relevant information from an external knowledge source and provide it to an LLM so the model can generate an answer grounded in that information.**

```text
Question
   ↓
Retrieve relevant knowledge
   ↓
LLM + retrieved context
   ↓
Grounded answer
```

RAG is useful for private/company data, frequently changing information and large external knowledge collections without requiring the model to be retrained for every data change.

## 2. Two pipelines

### Ingestion pipeline

```text
PDF / DOCX
   ↓
Parser
   ↓
ParsedDocument
   ↓
Chunker
   ↓
Chunks
   ↓
Embeddings
   ↓
Vector DB / index
```

### Query pipeline

```text
User Query
   ↓
Query embedding
   ↓
Vector search + keyword search
   ↓
RRF
   ↓
Reranker
   ↓
Top-K context
   ↓
Prompt/context construction
   ↓
LLM
   ↓
Answer + citations
```

**Interview point:** clearly distinguish work performed at ingestion time from work performed for each query.

## 3. Project architecture connection

Our document-intelligence work covers document parsing, structure-aware/semantic chunking, metadata and embeddings. The AI platform owns persistence, retrieval and application-level orchestration.

Conceptually:

```text
Document Intelligence SDK
→ parse → normalize → chunk → embed

AI Platform
→ persist → retrieve → hybrid search → RRF → rerank → RAG
```

This separation prevents document-processing implementation details from leaking into retrieval/application logic.

## 4. Retrieval

For a query such as:

> What was the company's revenue in Q4 2025?

we embed the query and perform retrieval through multiple signals:

```text
Query
 ├── vector/semantic retrieval
 └── keyword retrieval
          ↓
         RRF
          ↓
      candidates
          ↓
       reranker
          ↓
        top-K
```

## 5. Context construction

The LLM receives a combination of instructions, retrieved evidence and the user question.

```text
Instructions
+
Retrieved context
+
User question
=
LLM input
```

Retrieved chunks should be selected and formatted intentionally rather than concatenating arbitrary context.

## 6. Grounding and hallucination

RAG can reduce unsupported answers but does not guarantee truth.

```text
Bad parsing
   ↓
Bad chunks
   ↓
Bad retrieval
   ↓
Bad context
   ↓
Bad answer
```

Even with correct retrieval, the model can misinterpret or ignore evidence. Therefore retrieval quality and generation quality need separate evaluation.

## 7. Citations and provenance

Retrieved chunks should preserve metadata such as:

```text
document_id
page_number
section
chunk_id
source metadata
```

This enables source attribution, debugging, filtering and auditing.

## 8. RAG failure modes

```text
Parsing failure
     ↓
Chunking failure
     ↓
Embedding failure
     ↓
Retrieval failure
     ↓
RRF/ranking failure
     ↓
Reranking failure
     ↓
Context construction failure
     ↓
LLM generation failure
```

A good debugging process identifies which stage introduced the problem rather than immediately changing the LLM.

## 9. RAG latency

End-to-end latency can include:

```text
Query embedding
   +
Vector search
   +
Keyword search
   +
RRF
   +
Reranking
   +
LLM generation
```

Useful optimizations include concurrent retrieval, caching, efficient vector indexes, smaller candidate sets, reranking only a limited candidate pool and streaming generation.

## 10. RAG cost

Typical costs include:

- embedding calls
- vector/database infrastructure
- reranker inference
- LLM input tokens
- LLM output tokens

Our AI Knowledge Assistant project is a useful example of reducing LLM token usage using context compression and semantic caching.

## 11. RAG evaluation

Evaluate at multiple levels.

### Retrieval quality

Examples:

- Context Precision
- Context Recall

### Generation quality

Examples:

- Faithfulness
- Answer Relevance
- Answer Correctness

### System quality

- latency
- cost
- token usage
- failure rate

Ragas and LangSmith are part of the later dedicated evaluation/observability topic.

## 12. Interview questions

### What is RAG?

> RAG retrieves relevant external knowledge and gives it to an LLM as context so the answer can be grounded in that information.

### Walk me through your RAG pipeline.

> Documents are parsed into a normalized representation, chunked, embedded and indexed. At query time we embed the user query, perform semantic and keyword retrieval, fuse ranked results with RRF, optionally rerank the candidates and provide the final relevant chunks as context to the LLM. We preserve source metadata for attribution and traceability.

### What happens during ingestion vs query time?

> Ingestion prepares the knowledge base: parsing, chunking, embedding and indexing. Query time performs query embedding, retrieval, fusion, reranking, context construction and generation.

### Why do we need reranking?

> Initial retrieval is optimized for efficiently generating a candidate set. A reranker can perform a more precise relevance judgment over that smaller set before the LLM receives context.

### Where can RAG fail?

> It can fail during parsing, chunking, embedding, retrieval, fusion, reranking, context construction or generation. I would isolate the failing stage before changing components.

### How do you reduce hallucination in RAG?

> Improve retrieval and grounding, constrain context construction, preserve provenance, instruct the model to rely on supplied evidence, and evaluate both retrieval and generation quality.

### How do you evaluate a RAG pipeline?

> Evaluate retrieval quality, generation quality and system metrics such as latency, cost and failures. Retrieval and answer quality should be measured separately.

### How would you reduce RAG latency and cost?

> Parallelize independent retrieval, cache query/LLM work where appropriate, limit candidate counts, use efficient indexes, rerank only a small candidate set, compress unnecessary context and stream generation.

### Why not simply use the largest context window?

> A larger context window does not mean irrelevant context is beneficial. Excess context can increase cost and latency and reduce signal-to-noise ratio.

## 13. High-value project answer

> "Our pipeline starts with document ingestion where documents are parsed into a standardized representation, chunked into retrieval units and embedded. The embeddings and metadata are persisted for retrieval. When a user sends a query, we embed it and perform semantic and keyword retrieval. We fuse those ranked results using RRF, optionally rerank the candidates, and use the final relevant chunks as context for the LLM. We preserve chunk metadata so we can provide source attribution and enforce retrieval constraints."

## 14. Mental model

```text
                 INGESTION
                     │
Document → Parse → Chunk → Embed → Store
                                      │
                                      ▼
                                 Vector Store
                                      │
                                      │
                  QUERY             │
User Query → Embed → Vector Search ──┤
      │                               │
      └────────→ Keyword Search ─────┤
                                      ▼
                                     RRF
                                      ▼
                                  Reranker
                                      ▼
                                   Top-K
                                      ▼
                              Context Construction
                                      ▼
                                     LLM
                                      ▼
                               Answer + Citations
```

## Checklist

- [x] RAG definition
- [x] ingestion pipeline
- [x] query pipeline
- [x] parsing/chunking/embedding boundary
- [x] vector + keyword retrieval
- [x] RRF
- [x] reranking
- [x] context construction
- [x] grounding
- [x] citations/provenance
- [x] failure modes
- [x] latency
- [x] cost
- [x] retrieval vs generation evaluation
- [x] project-based interview answer
