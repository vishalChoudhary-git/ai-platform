# 02 — Production RAG

> Interview-prep notes. Learn the concepts first; use the interview questions at the end to practice explaining them.

## 1. RAG Fundamentals

### What is RAG?
Retrieval-Augmented Generation combines retrieval with LLM generation. The system first finds relevant external knowledge and then gives that context to the model to produce a grounded response.

### Why RAG?
RAG keeps knowledge outside the model, so private or changing data can be updated without retraining. It also reduces the need to place the entire knowledge base in the prompt.

### Basic RAG flow
```text
Documents
→ Parse
→ Clean / Structure
→ Chunk
→ Metadata
→ Embed
→ Index

User Query
→ Query Processing
→ Retrieve
→ Filter / Rerank
→ Build Context
→ LLM
→ Answer + Citations
```

### RAG vs Fine-tuning
- **RAG:** provides external knowledge at inference time.
- **Fine-tuning:** changes model behavior or task-specific capabilities.
- For frequently changing factual knowledge, RAG is usually the first choice.

### When RAG is unnecessary
If the task does not require external knowledge, retrieval can add latency and complexity. Classification, transformation, simple generation, and deterministic workflows may not need RAG.

---

## 2. Document Ingestion & Parsing

### Production ingestion
A production pipeline validates files, stores the raw artifact, parses content, normalizes structure, extracts metadata, chunks content, generates embeddings, and indexes the result.

### Why parsing matters
RAG quality depends heavily on what enters the retrieval layer. Poor parsing can destroy headings, tables, page relationships, and reading order, which leads to poor chunks and poor retrieval.

### PDF handling
First distinguish digital PDFs from scanned PDFs.
- **Digital PDF:** text/layout extraction.
- **Scanned PDF:** OCR, often with layout-aware processing.

Preserve page numbers and structural metadata for citations and filtering.

### Layout-aware parsing
Parsing should preserve document structure such as headings, paragraphs, lists, columns, tables, and sections instead of flattening everything into plain text.

### Tables
Tables should retain their row/column relationships and useful context such as table title, section, and page. Blindly flattening a table can destroy meaning.

### Images
Detect whether images contain useful information. OCR or multimodal extraction can turn image content into searchable text/representations while preserving source metadata.

### Metadata
Useful metadata includes:
- document ID and version
- tenant / owner
- page and section
- source and document type
- timestamps
- chunk position
- ACL / permission information

Metadata is important for filtering, authorization, citations, versioning, and document management.

### Multiple file formats
PDF, DOCX, PPTX, XLSX, and HTML should be processed with format-aware parsers and normalized into a common internal representation before chunking.

---

## 3. Chunking

### Why chunk?
Retrieval works better when documents are split into focused semantic units. Chunking affects retrieval precision, context quality, token usage, and latency.

### Fixed-size chunking
Splits text by a fixed token or character size, often with overlap. It is simple and predictable but can break semantic boundaries.

### Recursive chunking
Uses a hierarchy of separators and tries to split at larger boundaries before smaller ones. It is a strong general-purpose strategy.

### Semantic chunking
Splits based on semantic/topic changes rather than only length. It can create more meaningful chunks but is more computationally expensive and harder to tune.

### Sentence / paragraph chunking
Uses natural language boundaries. It preserves readability but may create chunks that are too small or too large depending on the document.

### Markdown / document-aware chunking
Uses headings, sections, lists, code blocks, and other document structure to keep related content together.

### Parent-child chunking
Use small child chunks for precise retrieval, then return a larger parent chunk for richer context. This separates retrieval precision from generation context.

### Context-aware chunking
Chunk boundaries consider surrounding meaning so a retrieved chunk remains understandable without excessive unrelated text.

### Chunk overlap
Overlap helps preserve meaning across boundaries. Too much overlap increases storage, duplicate retrievals, latency, and token cost.

### Choosing chunk size
There is no universal optimal size. Start with document structure and use evaluation to balance retrieval quality, context quality, latency, and cost.

### Domain-specific chunking
For legal, financial, or technical documents, preserve clauses, definitions, sections, tables, references, and other units that depend on surrounding context.

---

## 4. Embeddings

### What is an embedding?
An embedding is a numerical vector representing the semantic meaning of text or other content. Similar meanings should occupy nearby regions of vector space.

### Embeddings in RAG
Documents and queries are embedded so the system can perform semantic similarity search.

### Embedding dimension
The number of values in each vector. Larger dimensions may represent richer information but increase storage, memory, and compute requirements.

### Model compatibility
Document and query embeddings must be generated using compatible embedding spaces. Mixing incompatible models can make similarity scores meaningless.

### Similarity metrics
- **Cosine similarity:** compares vector direction; magnitude is largely ignored.
- **Dot product:** considers alignment and magnitude.
- **Euclidean distance:** measures geometric distance.

The correct metric depends on the embedding model and whether vectors are normalized.

### Normalization
Vectors may be scaled to unit length. With normalized vectors, cosine similarity and dot product become closely related.

### Embedding versioning
Store the embedding model/version with indexed data. A model change can alter dimensions or vector semantics, so reindexing should be controlled rather than mixing incompatible embeddings.

---

## 5. Vector Databases & Indexing

### Vector database
A vector database stores embeddings and supports similarity search, often together with metadata filtering.

### PostgreSQL + pgvector
A strong option when relational data, metadata, permissions, transactions, and vector search need to live together. It can simplify architecture for many enterprise workloads.

### Dedicated vector databases
Systems such as Pinecone, Weaviate, Qdrant, and Milvus can be preferred when vector search scale, specialized capabilities, or operational characteristics justify a dedicated system.

### Approximate Nearest Neighbor (ANN)
ANN algorithms trade some exactness for much faster search over large vector collections.

### HNSW
A graph-based ANN index that often provides strong recall and latency. The trade-off is higher memory usage and index-management cost.

### IVFFlat
Partitions vectors into clusters and searches selected clusters. It can reduce search work but requires tuning and can have lower recall than a well-tuned HNSW setup.

### HNSW vs IVFFlat
Think in terms of workload trade-offs rather than a universal winner:
- HNSW: strong query performance/recall, higher memory usage.
- IVFFlat: cluster-based search, potentially lower memory/search cost, but more tuning.

### Metadata indexes
Frequently filtered fields such as tenant, document, permissions, date, type, and version should be indexed appropriately.

---

## 6. Retrieval

### Dense retrieval
Uses embeddings to find semantically similar content. Strong when the query and relevant document use different wording but express similar meaning.

### Sparse retrieval / BM25
Uses lexical signals such as terms and term frequency. Strong for exact words, IDs, names, codes, and rare terms.

### Hybrid search
Combines dense and sparse retrieval. It is often more robust because semantic search handles meaning while lexical search handles exact terminology.

### Metadata filtering
Limits search to records matching constraints such as tenant, permission, document type, or time range.

### Query rewriting
Transforms the original query into a retrieval-friendly query, for example by resolving ambiguity or adding missing conversational context.

### Query expansion
Adds related terms or concepts to improve recall.

### Multi-query retrieval
Generates several search queries from one user question, retrieves for each, and combines the candidate results. Useful when one query wording may miss relevant evidence.

### HyDE
Hypothetical Document Embeddings generates a hypothetical answer/document and embeds that generated text for retrieval. It can help when query wording differs strongly from document wording.

### Self-query retrieval
Converts natural-language constraints into structured metadata filters plus a semantic search query.

### Parent-child retrieval
Retrieves fine-grained child chunks but expands them to their parent context before generation.

---

## 7. Reranking & Context Selection

### Why rerank?
Initial retrieval should be fast and high-recall. Reranking applies a stronger relevance model to a smaller candidate set to improve the final ordering.

### Cross-encoder reranker
Processes the query and candidate text together and predicts relevance. It is usually more accurate than raw vector similarity but more expensive.

### LLM reranker
Uses an LLM to judge candidate relevance. It can handle complex reasoning but usually has higher latency and cost.

### Cross-encoder vs LLM reranker
Cross-encoders are generally better for predictable high-throughput ranking. LLM reranking is useful when relevance requires richer reasoning and the extra cost is acceptable.

### Context compression
Reduces retrieved content to the most useful information before the LLM call. This reduces noise, token usage, and latency.

### Deduplication and diversity
Avoid sending repeated evidence. Candidate selection should balance relevance with diversity so the final context contains complementary information.

---

## 8. Advanced RAG Patterns

### Corrective RAG
Checks whether retrieved evidence is good enough and triggers a corrective retrieval strategy when it is weak.

### Adaptive RAG
Chooses different retrieval strategies based on the query, complexity, or confidence instead of using the same pipeline for every question.

### Self-RAG
The model is designed or trained to decide when retrieval is useful and to critique retrieved evidence or its generated answer.

### Graph RAG
Uses graph relationships alongside retrieval. It is useful when entities and relationships matter more than isolated text similarity.

### Agentic RAG
An agent iteratively decides what to retrieve, where to retrieve it from, and whether more evidence is needed.

### Standard RAG vs Graph RAG
Use standard RAG when relevant passages are mostly independent. Graph RAG becomes useful when the answer depends on multi-hop relationships among entities.

### Multi-hop retrieval
One retrieval step informs the next. This is useful when a question requires connecting multiple pieces of evidence.

### Conversational retrieval
Uses conversation history to resolve references and generate a meaningful search query. The goal is to retrieve using the user's current intent, not blindly search the entire conversation.

---

## 9. Permissions, Tenancy & Data Protection

### Permission-aware RAG
Authorization is part of retrieval. ACL/tenant constraints should be applied before content reaches the LLM context.

### Tenant isolation
Tenant identity must follow the request through authentication, storage, retrieval, caching, and logging. Cross-tenant access must be impossible by construction and tested explicitly.

### Retrieval-level authorization
Post-filtering unauthorized results after retrieval is not sufficient as the primary boundary. Retrieval should already be scoped to what the requester is allowed to access.

### Document ACLs
Store document/group/user permissions in a way that can be evaluated during retrieval.

### Document versioning
Track document versions and associate chunks/embeddings with the correct version. Retrieval should target the active version.

### PII
Detect and classify sensitive data, then apply masking, access controls, retention, and auditing according to requirements.

### PII filtering
Filtering can happen during ingestion, retrieval, or response handling depending on the policy. The important point is that sensitive information is controlled at defined security boundaries.

---

## 10. RAG Evaluation

### Retrieval metrics
- **Recall@K:** how much of the relevant evidence appears in the top K.
- **Precision@K:** how much of the top K is relevant.
- **MRR:** rewards the position of the first relevant result.
- **NDCG:** rewards highly relevant results appearing near the top and supports graded relevance.

### Context quality
Useful measures include context relevance, context precision, and context recall.

### Generation quality
- **Faithfulness:** answer claims are supported by retrieved evidence.
- **Answer relevance:** the response actually answers the question.
- **Citation accuracy:** cited sources genuinely support the associated claims.

### Retrieval vs generation debugging
Treat them as separate stages. First inspect query and retrieval quality; then inspect reranking/context assembly; only then blame the generation model or prompt.

### Evaluation dataset
Use representative queries with expected relevant evidence and expected answer behavior. Keep a fixed dataset for regression testing when comparing RAG changes.

---

## 11. Production Trade-offs

### Quality vs latency
More retrieval candidates, stronger reranking, and larger context can improve quality but usually increase latency.

### Quality vs cost
Higher-quality embedding, reranking, and generation models can improve results but increase compute/token costs.

### Recall vs precision
Increasing retrieval depth generally improves recall but may introduce more irrelevant context. Reranking helps recover precision after broad retrieval.

### Freshness vs complexity
Near-real-time indexing keeps knowledge fresh but requires more infrastructure, eventing, and consistency handling.

### General RAG vs advanced RAG
Start with the simplest architecture that meets quality requirements. Add rewriting, reranking, Graph RAG, or agentic behavior only when evaluation shows a need.

---

## 12. Production Failure Scenarios

### Irrelevant retrieval
Check query formulation, parsing, chunking, embedding model, similarity metric, metadata filters, candidate count, hybrid retrieval, and reranking.

### Low retrieval recall
Typical levers are better parsing/chunking, stronger embeddings, query rewriting, hybrid search, multi-query retrieval, or deeper candidate retrieval.

### Relevant context but wrong answer
Verify that the required evidence is actually present, that context was not truncated, and that generation is grounded rather than inventing unsupported claims.

### No relevant documents
Use confidence or relevance thresholds. Return an explicit insufficient-evidence response or trigger another retrieval path instead of hallucinating.

### Stale documents
Version documents and embeddings, update indexes asynchronously, and ensure queries target the active version.

### Duplicate ingestion
Use stable document/version identifiers and idempotent processing.

### Vector store unavailable
Retry transient failures, use a fallback path when appropriate, and fail gracefully rather than generating an unsupported answer.

### Large-scale ingestion
Use asynchronous queues, independently scalable workers, idempotent stages, retries, status tracking, and dead-letter handling.

---

## 13. Enterprise RAG Architecture

A typical production architecture looks like:

```text
                ┌───────────────┐
                │   Documents   │
                └───────┬───────┘
                        ↓
              ┌──────────────────┐
              │ Async Ingestion  │
              └────────┬─────────┘
                       ↓
        Parse → Clean → Chunk → Metadata
                       ↓
                   Embeddings
                       ↓
             Vector / Hybrid Index

User → Auth → Query Processing → Retrieval
                              ↓
                    Metadata / ACL Filter
                              ↓
                     Reranking / Selection
                              ↓
                       Context Builder
                              ↓
                             LLM
                              ↓
                   Answer + Citations
```

Production concerns should cover reliability, scaling, security, observability, freshness, and cost.

### Scaling
Keep query services stateless, scale ingestion workers horizontally, use queues for asynchronous work, and scale retrieval separately from generation.

### Reliability
Use timeouts, retries for transient failures, idempotency, circuit breakers where appropriate, health checks, and graceful degradation.

### Observability
Track retrieval quality, answer quality, latency by stage, token usage, cost, errors, cache behavior, ingestion status, and security events.

---

# Interview Questions

## Fundamentals
1. What is RAG and why is it needed?
2. What is the end-to-end RAG flow?
3. RAG vs fine-tuning vs prompting — when would you choose each?
4. When would you not use RAG?

## Ingestion & Parsing
5. Why is document parsing critical for RAG quality?
6. How would you process a scanned PDF?
7. What is layout-aware parsing?
8. How would you preserve table structure?
9. What metadata would you store with each chunk?
10. How would you process different document formats consistently?

## Chunking
11. Why do we chunk documents?
12. Fixed vs recursive vs semantic chunking?
13. When would you use document-aware chunking?
14. What is parent-child chunking?
15. How do you choose chunk size and overlap?
16. How would chunking differ for legal or financial documents?

## Embeddings & Vector Search
17. What is an embedding?
18. What does embedding dimension mean?
19. Cosine vs dot product vs Euclidean distance?
20. Why is embedding normalization useful?
21. Why do embeddings need versioning?
22. What is ANN search?
23. HNSW vs IVFFlat?
24. pgvector vs a dedicated vector database?

## Retrieval
25. Dense vs sparse retrieval?
26. Why use hybrid search?
27. What is metadata filtering?
28. What is query rewriting and when is it useful?
29. Query expansion vs multi-query retrieval?
30. What is HyDE?
31. What is self-query retrieval?
32. What is parent-child retrieval?

## Reranking & Advanced RAG
33. Why do we need reranking?
34. Cross-encoder vs LLM reranking?
35. What is context compression?
36. How do you avoid redundant context?
37. Corrective RAG vs Adaptive RAG?
38. What is Self-RAG?
39. What is Graph RAG and when would you use it?
40. What is Agentic RAG?
41. What is multi-hop retrieval?
42. How does conversational retrieval work?

## Security & Permissions
43. How would you design permission-aware RAG?
44. Why should authorization be enforced during retrieval?
45. How would you prevent cross-tenant data leakage?
46. How would you handle document ACLs?
47. How would you handle document versioning?
48. How would you protect PII in a RAG system?

## Evaluation
49. How do you evaluate retrieval quality?
50. Recall@K vs Precision@K?
51. MRR vs NDCG?
52. How do you evaluate answer quality separately from retrieval?
53. What is faithfulness?
54. What is citation accuracy?
55. How would you build a RAG regression dataset?
56. How do you determine whether a RAG change actually improved the system?

## Production Scenarios
57. Retrieval is irrelevant — how would you debug it?
58. Retrieval recall is low — what would you change?
59. Retrieved context is good but the answer is wrong — what do you inspect?
60. The system is accurate but too slow — how would you optimize it?
61. The system is too expensive — what would you optimize?
62. What happens if the vector store is unavailable?
63. How would you process millions of documents reliably?
64. How would you prevent duplicate ingestion?
65. How would you handle stale or updated documents?
66. What should happen when no relevant evidence is found?

## System Design
67. Design a production enterprise RAG system.
68. Where would you enforce authorization?
69. How would you scale ingestion and query serving independently?
70. What are the main RAG production trade-offs?