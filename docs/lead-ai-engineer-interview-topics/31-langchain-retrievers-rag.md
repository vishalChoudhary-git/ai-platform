# LangChain Concepts 9–10 — Retrievers & RAG

**Status:** Complete

## Concept 9 — Retrievers

### Definition

> **A Retriever is an abstraction that takes a query and returns relevant documents.**

The abstraction does not require one particular retrieval algorithm.

```text
Query
  ↓
Retriever
  ↓
Relevant Documents
```

Possible implementations include:

- vector/semantic retrieval
- keyword/lexical retrieval
- hybrid retrieval
- database search
- web search
- custom retrieval logic

### Retriever vs Vector Search

```text
Vector Search
→ one retrieval strategy based on embeddings/similarity

Retriever
→ higher-level contract: query → relevant documents
```

A Retriever may use vector search internally, but the terms are not interchangeable.

### Retriever vs Vector Store

```text
Vector Store
→ stores/searches vectors and associated data

Retriever
→ exposes the document-retrieval interface
```

A vector store can be used as the backing implementation of a Retriever.

### Retriever vs Reranker

```text
Retriever
→ fast candidate generation

Reranker
→ more precise ordering of a smaller candidate set
```

Typical flow:

```text
1M chunks
   ↓
Vector / Keyword Search
   ↓
20–100 candidates
   ↓
Reranker
   ↓
Top 5–10
```

### Hybrid retrieval

A custom Retriever can encapsulate a complete retrieval strategy:

```text
Custom Retriever
   ├── Vector Search
   ├── Keyword Search
   ├── RRF
   └── optional Reranker
   ↓
Documents
```

Important:

> **LangChain provides the Retriever abstraction and many implementations/integrations; the developer can implement a custom Retriever when the retrieval strategy is application-specific.**

### Tool vs Retriever

```text
Tool
→ model-facing capability

Retriever
→ retrieval abstraction
```

A Tool can internally call a Retriever:

```text
Agent
  ↓
search_policy Tool
  ↓
Retriever
  ↓
Documents
```

### Authorization

Relevance is not a security boundary.

```text
User identity / permissions
        ↓
Trusted authorization scope
        ↓
Retriever
        ↓
Only authorized candidates
```

Do not rely on the LLM to decide which documents a user may access.

### Mental model

```text
                    QUERY
                      ↓
                  RETRIEVER
                      ↓
              Relevant Documents
                      ↓
                 Reranker
                      ↓
                Final Top-K
```

---

## Concept 10 — RAG

### Definition

> **RAG (Retrieval-Augmented Generation) is an application pattern where relevant external knowledge is retrieved and supplied as context to an LLM before generation.**

```text
User Question
      ↓
Retrieve knowledge
      ↓
Context construction
      ↓
LLM
      ↓
Grounded answer
```

### RAG is bigger than a Retriever

Retriever is one component. A production RAG pipeline may include:

```text
Query
 ↓
Authorization / filters
 ↓
Query processing
 ↓
Vector + keyword retrieval
 ↓
RRF
 ↓
Reranking
 ↓
Context selection
 ↓
Prompt
 ↓
LLM
 ↓
Answer + citations
```

### Ingestion vs query time

**Ingestion:** prepare the knowledge base.

```text
Document
 ↓
Parse
 ↓
Normalize
 ↓
Chunk
 ↓
Embed
 ↓
Index / Store
```

**Query time:** retrieve and generate.

```text
Question
 ↓
Query embedding / retrieval
 ↓
RRF / reranking
 ↓
Context
 ↓
LLM
```

### LangChain's role

LangChain can provide integrations/abstractions for loaders, splitters, embeddings, vector stores, retrievers, prompts and models. It does **not** mean LangChain must own the entire production RAG architecture.

Keep infrastructure and domain boundaries explicit where appropriate:

```text
Document processing
→ application / dedicated ingestion pipeline

Retrieval
→ Retriever / application retrieval service

Generation
→ Chat Model

Orchestration
→ Runnable / agent / LangGraph as needed
```

### RAG and Reranking

```text
Retriever
   ↓
Candidates
   ↓
Reranker
   ↓
Final context
   ↓
LLM
```

Reranking is optional and should be justified by evaluation, latency and cost.

### RAG and hallucination

RAG can reduce unsupported generation but does not guarantee correctness.

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

Separate retrieval quality from generation quality when debugging.

### RAG and citations

Preserve provenance on retrieved documents/chunks:

```text
document_id
page_number
section
chunk_id
source
```

Prefer generating citations from trusted retrieval metadata rather than asking the model to invent source references.

### No-answer behavior

If the retrieved evidence does not support an answer:

```text
No sufficient evidence
        ↓
Abstain / say information is insufficient
```

Do not force a confident answer from unsupported context.

### RAG vs Fine-tuning

```text
RAG
→ changes the context supplied at inference time

Fine-tuning
→ changes model behavior/parameters through additional training
```

### RAG vs Agentic RAG

**Fixed RAG:**

```text
Question → Retrieve → Prompt → LLM → Answer
```

**Agentic RAG:**

```text
Question
 ↓
Agent
 ↓
Need knowledge?
 ├── No → Answer
 └── Yes → Search Tool → Retriever → Agent
```

### Interview questions

#### What is a Retriever?

> A Retriever is an abstraction that accepts a query and returns relevant documents. The underlying strategy can be vector, keyword, hybrid, database or custom retrieval.

#### Retriever vs Vector Store?

> A Vector Store is the storage/search mechanism for vectors and associated data, while a Retriever exposes the higher-level document retrieval contract.

#### How does RAG work?

> We retrieve relevant external knowledge, optionally fuse and rerank the candidates, construct context, and provide that context to the LLM so it can generate a grounded response.

#### Does LangChain own the whole RAG pipeline?

> No. It provides useful components and integrations, but production systems can keep ingestion, retrieval strategy, security, persistence and domain logic in application-owned services.

#### Does RAG eliminate hallucinations?

> No. Retrieval can fail, source data can be wrong, or the model can misinterpret correct evidence. RAG is a grounding technique, not a guarantee of truth.

#### How would you debug a bad RAG answer?

> First check whether the correct evidence was retrieved. Then inspect filtering, fusion, reranking and context construction before changing the model.

### Final mental model

```text
                RAG
                 │
      ┌──────────┴──────────┐
      ↓                     ↓
 RETRIEVAL             GENERATION
      ↓                     ↓
Vector / Keyword       Prompt + Context
      ↓                     ↓
     RRF                  Chat Model
      ↓                     ↓
  Reranker               Answer
      ↓
 Context
```

## Key takeaway

> **Retriever = query → documents. RAG = retrieve useful knowledge + construct context + generate with an LLM. LangChain provides abstractions for these pieces, but your application can own the actual production strategy.**
