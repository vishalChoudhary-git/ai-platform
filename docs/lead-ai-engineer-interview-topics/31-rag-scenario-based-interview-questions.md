# RAG Scenario-Based Interview Questions

**Purpose:** Practice the kind of engineering scenarios that test whether you can diagnose, evaluate, scale and operate a RAG system — not just describe the RAG pipeline.

> Try answering these without Googling first. Explain **what you would investigate, what evidence you would collect, what change you would make, and how you would prove the change worked**.

---

## 1. RAG suddenly starts giving incorrect answers

Your RAG system was working well in production, but answer quality suddenly drops.

**What is the first thing you investigate?**  
**How would you prove that you found the root cause?**

Think in stages:

```text
Query → Retrieval → RRF → Reranking → Context → Generation → Validation
```

Do not immediately assume the LLM is the problem.

---

## 2. Retriever returns relevant documents, but answers are poor

Your retriever returns highly relevant chunks, but the final answer is still incorrect or incomplete.

**What could be going wrong between retrieval and generation?**

Consider:

- reranking
- context construction
- context ordering
- too much irrelevant context
- missing chunks needed to answer the question
- prompt/instructions
- model behavior
- output validation

---

## 3. You changed the embedding model

You replace the embedding model with a newer/better model.

**How would you know whether the change actually improved the RAG system?**  
**What metrics would you measure before and after?**

Compare at least:

```text
Retrieval quality
→ Recall@K / Precision@K / MRR / NDCG

Generation quality
→ faithfulness / answer correctness / relevance

Production
→ latency / cost / error rate
```

The important point is: **do not call the new embedding model better just because it is newer.**

---

## 4. One question requires information from five documents

A user asks a question that requires combining information from five different documents.

**How would you design retrieval and context construction?**

Think about:

- retrieving enough candidates to cover all five sources
- document/chunk diversity
- metadata and provenance
- deduplication
- reranking
- context ordering
- context/token limits
- preserving citations for each claim

---

## 5. RAG works with 10,000 documents but now has 1 million

Your RAG system performs well with 10,000 documents. The corpus grows to 1 million.

**What breaks first?**  
**How would you redesign the architecture?**

Consider:

- vector index/search performance
- keyword index
- database scaling
- ingestion throughput
- embedding generation
- storage
- metadata filtering
- partitioning/sharding
- caching
- async workers
- observability

The interviewer is testing whether you can move from a prototype architecture to a production architecture.

---

## 6. The correct document is not retrieved

A user asks a question and you know the answer exists in the knowledge base, but the correct document is not in the retrieved candidates.

**What would you try before giving up?**

Possible strategies:

- query rewriting
- query expansion
- hybrid retrieval
- keyword search for exact terms
- adjust retrieval depth
- review similarity thresholds
- inspect chunking
- inspect embeddings
- metadata filtering
- ask a clarifying question
- return **insufficient information** when evidence is still unavailable

A production system must know when it does not have enough evidence.

---

## 7. Your RAG answer looks correct but is actually wrong

The response sounds convincing and cites documents, but the answer is factually incorrect.

**How would you debug it?**

Break the pipeline into stages:

```text
Query
  ↓
Retrieval
  ↓
Reranking
  ↓
Context
  ↓
Generation
  ↓
Validation
```

Inspect each stage independently and determine whether the failure is:

- retrieval failure
- ranking failure
- context construction failure
- generation failure
- validation/evaluation failure

---

## 8. Hallucinations suddenly increase

Your RAG system previously had low hallucination rates, but hallucinations increase after a release.

**What could cause this, and how would you reduce it?**

Think beyond prompting:

- retrieval quality regression
- bad chunking/indexing
- reranker regression
- irrelevant context
- missing evidence
- context truncation
- model/provider change
- prompt regression
- citation/provenance problems
- missing abstention behavior

Possible mitigations:

```text
Better retrieval
+ reranking
+ context validation
+ grounding instructions
+ trusted citations
+ unsupported-answer refusal
+ evaluation/regression tests
```

---

## 9. Latency suddenly increases

Users complain that the RAG assistant became slow after adding hybrid search and reranking.

**How would you locate the bottleneck?**

Measure each stage:

```text
Query embedding
Vector search
Keyword search
RRF
Reranking
Context construction
LLM TTFT
LLM generation
```

Then consider:

- parallel vector + keyword retrieval
- smaller candidate set
- reranking only where it improves quality
- caching
- context compression
- connection reuse
- batching where appropriate
- streaming for perceived latency

Do not optimize a stage before measuring it.

---

## 10. When should you choose hybrid search?

Your system uses vector search only.

Users report poor results for queries containing invoice IDs, account numbers, error codes and exact product names.

**Would you add keyword search? Why?**

Explain when:

```text
Vector → semantic meaning / paraphrases
Keyword → exact terms / identifiers / codes / numbers
Hybrid → complementary signals
```

Then explain why you might use RRF before reranking.

---

## 11. When should you choose a reranker?

Your first-stage retriever returns relevant documents, but the top few chunks are not always the most relevant to the exact question.

**Would you add a reranker? Why?**

Discuss the trade-off:

```text
More candidates
   ↓
Potentially better recall
   ↓
More reranking work
   ↓
Higher latency/cost
```

The right answer is not "always use a reranker." Evaluate whether the quality improvement justifies the cost.

---

## 12. Reranker improves relevance but makes the system too slow

After adding a cross-encoder reranker, answer quality improves but p95 latency becomes unacceptable.

**How would you optimize it without immediately removing the reranker?**

Consider:

- reduce reranker candidate depth
- improve first-stage retrieval
- rerank only selected workloads
- use a faster/smaller reranker
- parallelize independent work before reranking
- cache repeated queries/results
- benchmark quality vs latency

Choose the smallest candidate pool that maintains the required quality.

---

## 13. Retrieval metrics improve but answer quality does not

After a retrieval change:

```text
Recall@K ↑
Precision@K ↑
```

but users report no improvement in answer quality.

**What would you investigate?**

Possible explanations:

- retrieved evidence is relevant but insufficient
- reranker changes ordering poorly
- context construction is weak
- too many chunks are passed to the LLM
- important evidence is truncated
- model cannot correctly synthesize multiple chunks
- generation/prompt is the bottleneck

Remember: **better retrieval does not automatically mean better answers.**

---

## 14. A document was updated, but RAG still returns the old answer

A policy document changes from version A to version B, but users still receive answers based on version A.

**How would you investigate and fix it?**

Trace:

```text
Source document
 ↓
Parsing
 ↓
Chunking
 ↓
Embedding
 ↓
Index
 ↓
Cache
 ↓
Retrieval
 ↓
LLM
```

Consider stale chunks, failed re-indexing, duplicate versions, cache invalidation and document version metadata.

---

## 15. Retrieval returns too many irrelevant chunks

Top-K is increased to improve recall, but the LLM now receives a large amount of noisy context and answer quality decreases.

**What would you change?**

Consider:

- reranking
- context compression
- better chunking
- metadata filtering
- reducing final Top-K
- better candidate/final-K separation
- query rewriting

Explain the trade-off between recall and context noise.

---

## 16. The answer requires information that is split across chunks

A financial statement has a table in one chunk and the explanatory notes in another.

The system retrieves only one of them.

**How would you improve the pipeline?**

Consider:

- structure-aware/table-aware chunking
- preserving document relationships
- parent-child retrieval
- retrieving neighboring/related chunks
- metadata
- multi-document or multi-chunk synthesis

The key question is whether the chunking strategy preserved the relationships required by the query.

---

## 17. Different tenants have documents with the same names

Two customers both have a document called `policy.pdf`.

**How would you ensure Tenant A can never retrieve Tenant B's chunks?**

Discuss:

- tenant ID in metadata
- authorization-aware retrieval
- database/index filtering
- service-layer authorization
- defense in depth
- testing isolation

Important:

> The LLM must never be responsible for deciding whether a user is allowed to see a document.

---

## 18. Your vector database becomes unavailable

The RAG API is healthy, but the vector database is down.

**What should the user experience be?**

Discuss:

- timeout
- bounded retry/backoff
- circuit breaker
- fallback strategy
- cached responses where safe
- graceful degradation
- observability/alerting
- whether keyword retrieval can temporarily serve as a fallback

Do not turn a dependency outage into an unbounded retry storm.

---

## 19. LLM provider becomes unavailable

Your application depends on one LLM provider and the provider starts returning errors.

**How would you design the system to remain available?**

Think about:

```text
LLM Gateway
    ↓
Model Router
    ├── Provider A
    └── Provider B
```

Discuss timeouts, retries, circuit breaking, compatible fallback models, rate limits and quality differences between providers.

---

## 20. Users ask questions outside the knowledge base

Users frequently ask questions that are not covered by the indexed documents.

**How should the RAG system behave?**

A strong answer should include:

```text
Retrieve evidence
      ↓
Is evidence sufficient?
   /           \
 yes            no
 ↓               ↓
answer       abstain / clarify
```

The goal is not to answer every question. The goal is to avoid unsupported answers.

---

## 21. RAG quality degrades after a parser change

You replace the PDF parser and retrieval quality drops significantly.

**How would you identify whether parsing caused the regression?**

Compare:

```text
Old parser → parsed output → chunks → retrieval
New parser → parsed output → chunks → retrieval
```

Inspect:

- extracted text
- headings
- tables
- page boundaries
- metadata
- chunk boundaries
- missing content
- embedding/index counts

A retrieval problem can originate much earlier in the pipeline.

---

## 22. You need to support 100× more queries

The number of documents stays roughly constant, but query traffic increases by 100×.

**What would you scale first?**

Think about:

- stateless API replicas
- connection pools
- vector DB capacity
- keyword search capacity
- LLM/provider rate limits
- caching
- async workloads
- concurrency limits
- queues/backpressure
- horizontal scaling

Distinguish **data scale** from **request scale**.

---

## 23. You have excellent offline metrics but poor production results

Your evaluation dataset shows strong Recall@K, NDCG and faithfulness, but production users report poor answers.

**Why might offline evaluation disagree with production?**

Consider:

- evaluation dataset does not represent real queries
- query distribution changed
- stale production data
- permission/filtering differences
- latency/timeouts
- long-tail queries
- multi-turn conversation effects
- missing user feedback signals

This is why offline evaluation and production observability both matter.

---

## 24. You need to choose between quality, latency and cost

You have three configurations:

```text
A → highest quality, highest cost, highest latency
B → balanced
C → lowest cost and latency, lower quality
```

**How would you decide which one to deploy?**

Do not answer purely from intuition. Define the product requirement and compare:

```text
Quality
Latency
Cost
Reliability
```

Then run representative evaluation and load tests.

---

# Interview Answer Framework

For almost any RAG scenario, use this structure:

```text
1. Clarify the symptom
        ↓
2. Break the pipeline into stages
        ↓
3. Measure each stage
        ↓
4. Identify the failing boundary
        ↓
5. Form a hypothesis
        ↓
6. Change one important variable
        ↓
7. Re-run evaluation
        ↓
8. Compare quality + latency + cost
        ↓
9. Roll out safely
        ↓
10. Monitor production behavior
```

## High-value phrases to remember

- **"I would measure before changing the architecture."**
- **"First I would determine whether this is a retrieval or generation failure."**
- **"I would reproduce the issue on a representative evaluation set."**
- **"I would compare the old and new configuration using the same queries."**
- **"I would measure both quality and production metrics."**
- **"I would change one major variable at a time so I can attribute the improvement."**
- **"If the system does not have sufficient evidence, it should abstain rather than hallucinate."**
- **"Authorization must happen at the application/data boundary, not through the LLM."**

---

# Quick Practice Set

Before an interview, practice these five first:

1. **RAG answers suddenly become wrong — where do you start and how do you prove the cause?**
2. **Retriever is relevant but generation is poor — what happens between retrieval and generation?**
3. **How do you prove a new embedding model improved the system?**
4. **How do you design RAG for 1 million documents?**
5. **How do you reduce RAG latency without sacrificing too much quality?**
