# RAG Scenario-Based Interview Questions — Answers

**Purpose:** Interview-ready answers for the scenario questions in `31-rag-scenario-based-interview-questions.md`. The goal is to answer like an engineer: identify the failing stage, collect evidence, form a hypothesis, change one important variable, and prove the result with metrics.

---

## 1. RAG suddenly starts giving incorrect answers

### Answer

I would first determine whether the regression is in **retrieval or generation**, rather than immediately blaming the LLM.

I would compare recent production traces with a known-good period and inspect:

```text
Query → Retrieval → RRF → Reranking → Context → Generation → Validation
```

For the same failing queries, I would compare retrieved chunks, scores/ranks, reranker output, final context and model response against the previous version.

Then I would form a hypothesis—for example, a parser/indexing change caused different chunks to be embedded—and reproduce it on a fixed evaluation set. If the old configuration succeeds and the new configuration fails on the same queries, that gives evidence for the regression.

**Interview answer:**
> "I would first localize the failure boundary. I would compare the same queries across the old and new pipeline, inspect retrieval and final context before generation, and use offline evaluation plus production traces to prove which stage regressed."

---

## 2. Retriever returns relevant documents, but answers are poor

### Answer

If retrieval is genuinely relevant, I would investigate everything between retrieval and generation:

- Did the reranker push the useful chunk down?
- Are we passing too many irrelevant chunks?
- Is important evidence missing because we selected too few final chunks?
- Is context ordered poorly?
- Was relevant context truncated because of the model context limit?
- Can the LLM synthesize information from multiple chunks?
- Are the grounding instructions and output schema correct?

I would inspect the **exact final context sent to the LLM**, not just the retriever output.

**Interview answer:**
> "If retrieval is good but the answer is poor, I would inspect reranking, context construction, truncation, ordering and generation separately. I want to prove that the evidence the retriever found actually reached the model in a usable form."

---

## 3. You changed the embedding model

### Answer

I would not decide based on the model being newer or having better benchmark claims. I would create a fixed evaluation set containing representative queries and known relevant chunks.

Run old and new embeddings against the **same queries and corpus**, then compare:

```text
Retrieval:
Recall@K
Precision@K
MRR
NDCG

Generation:
Faithfulness
Answer correctness
Answer relevance

Production:
Latency
Cost
Error rate
```

For a fair comparison, I would also re-embed the corpus with the new model before evaluating the production-style index because query and document embeddings need to come from the same embedding space/model configuration.

**Interview answer:**
> "I would run an A/B-style offline evaluation on the same corpus and query set, compare retrieval and answer metrics, then validate latency and cost. The new embedding model is better only if the measured system-level results justify the trade-off."

---

## 4. One question requires information from five documents

### Answer

I would treat this as a **multi-source retrieval and synthesis** problem.

First, retrieve enough candidates to give the five documents a chance to appear. I would preserve document IDs and metadata, deduplicate chunks, and ensure the reranker does not accidentally eliminate all evidence from one required source.

Then construct context with clear provenance:

```text
Document A
  relevant chunks
Document B
  relevant chunks
...
Document E
  relevant chunks
```

I would respect the model context limit and preserve citations so each claim can be traced back to its source.

**Interview answer:**
> "I would optimize for evidence coverage, not just top-K similarity. I would retrieve enough candidates, preserve source diversity and provenance, rerank carefully, then build a bounded context that allows the model to synthesize evidence from all required documents."

---

## 5. RAG works with 10,000 documents but now has 1 million

### Answer

I would first identify whether the bottleneck is **search latency, database capacity, ingestion, embedding generation, storage or filtering**.

At one million documents, I would focus on:

- properly indexed vector search
- efficient keyword indexes
- metadata/tenant filtering at the database boundary
- partitioning where appropriate
- horizontal database scaling
- asynchronous ingestion workers
- batched embedding generation
- caching for repeated queries
- observability for search latency and saturation

I would avoid prematurely introducing complexity. I would load-test the current architecture and scale the actual bottleneck.

**Interview answer:**
> "The first question is whether the scale problem is data scale or query scale. I would benchmark vector and keyword search, ingestion and filtering, then introduce indexing, partitioning, horizontal scaling and async workers where measurements show the need."

---

## 6. The correct document is not retrieved

### Answer

I would inspect the query and retrieval candidates first. Then I would try progressively stronger retrieval strategies:

```text
Original query
 ↓
Query rewrite / expansion
 ↓
Hybrid retrieval
 ↓
Increase candidate depth
 ↓
Check metadata filters
 ↓
Inspect chunking + embeddings
```

If the query contains an exact identifier, keyword retrieval may recover something vector search misses. If the issue is terminology, query expansion or rewriting can help.

If evidence still cannot be found, I would **abstain or ask a clarifying question** rather than generate an unsupported answer.

**Interview answer:**
> "I would determine whether the failure is query formulation, filtering, chunking, embedding or retrieval strategy. I would try rewriting and hybrid retrieval, but if evidence is still insufficient, the system should say so rather than hallucinate."

---

## 7. Your RAG answer looks correct but is actually wrong

### Answer

I would trace the exact request through every stage:

```text
Query
 ↓
Retrieval
 ↓
Reranking
 ↓
Final Context
 ↓
Generation
 ↓
Validation
```

I would verify whether the cited source actually supports the claim. A citation alone does not prove correctness.

Possible failures include:

- wrong chunk retrieved
- correct chunk but wrong reranker ordering
- context omitted/truncated
- model misunderstood the evidence
- answer validation accepted an unsupported claim

**Interview answer:**
> "I would not debug the final text in isolation. I would trace the evidence chain and verify whether every important claim is supported by the retrieved context. That lets me distinguish retrieval failure from generation or validation failure."

---

## 8. Hallucinations suddenly increase

### Answer

I would compare hallucination rates before and after the release and correlate them with pipeline changes.

I would investigate:

- retrieval regression
- parser/chunking changes
- reranker changes
- prompt changes
- model/provider changes
- context truncation
- missing evidence
- citation/provenance failures

Mitigation should be layered:

```text
Better retrieval
+ reranking
+ context validation
+ grounding instructions
+ citations/provenance
+ unsupported-answer refusal
+ regression evaluation
```

**Interview answer:**
> "I would treat hallucination as a system problem, not just a prompt problem. First I would establish whether the model received sufficient evidence, then improve retrieval and context quality and add validation and abstention for unsupported answers."

---

## 9. Latency suddenly increases

### Answer

I would instrument each stage and look at **p50/p95/p99**, not only average latency.

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

If vector and keyword retrieval are independent, run them concurrently. If reranking dominates, reduce candidate depth or use a faster model after checking quality impact. I would also consider caching, connection reuse, context reduction and streaming.

**Interview answer:**
> "I would measure the latency budget by stage first. Then I would optimize the dominant component—for example parallel retrieval, smaller reranker candidate sets or caching—while checking that quality does not regress."

---

## 10. When should you choose hybrid search?

### Answer

I would choose hybrid search when the data and query distribution benefit from both **semantic similarity and exact lexical matching**.

```text
Vector → concepts, meaning, paraphrases
Keyword → IDs, codes, names, numbers, exact terms
Hybrid → complementary coverage
```

For example, a query containing `AC-93821` and "revenue decline" benefits from keyword matching for the account ID and semantic retrieval for the natural-language concept.

I would typically fuse the result lists with RRF before reranking because the two retrieval methods may produce scores on different scales.

**Interview answer:**
> "I would not add hybrid search just because it is popular. I would add it when evaluation shows that lexical signals recover relevant exact-match cases that semantic retrieval misses."

---

## 11. When should you choose a reranker?

### Answer

A reranker is useful when first-stage retrieval has reasonable recall but the ordering of the top candidates is not good enough for the final context.

The pattern is:

```text
Fast retrieval
→ larger candidate set
→ expensive reranking
→ small final Top-K
```

The trade-off is latency and cost. I would compare answer quality with and without reranking and determine whether the improvement justifies the additional inference cost.

**Interview answer:**
> "I use the first-stage retriever for scalable candidate generation and a reranker for fine-grained relevance. I would add it when evaluation shows meaningful quality improvement for an acceptable latency and cost budget."

---

## 12. Reranker improves relevance but makes the system too slow

### Answer

I would optimize the candidate pipeline before removing the reranker.

Possible steps:

1. Measure reranker p50/p95 latency.
2. Reduce the candidate set while monitoring Recall@K and answer quality.
3. Improve first-stage retrieval so fewer candidates need reranking.
4. Evaluate a smaller/faster reranker.
5. Cache repeated queries where appropriate.
6. Rerank only workloads where the quality gain matters.

**Interview answer:**
> "I would find the smallest reranker candidate pool that preserves the required quality. I would benchmark quality versus latency rather than assuming the largest candidate set is best."

---

## 13. Retrieval metrics improve but answer quality does not

### Answer

This means retrieval may no longer be the main bottleneck.

I would inspect:

- whether the retrieved evidence is sufficient, not merely relevant
- reranker ordering
- final context size
- context truncation
- context ordering
- multi-chunk synthesis
- prompt/grounding behavior
- model capability

For example, Recall@K can improve because the correct chunk is somewhere in the candidate set, while the final Top-K sent to the LLM still excludes it.

**Interview answer:**
> "Retrieval metrics measure retrieval, not the whole RAG system. I would trace whether the improved candidates survive reranking and context construction and then evaluate answer faithfulness and correctness separately."

---

## 14. A document was updated, but RAG still returns the old answer

### Answer

I would trace the document lifecycle:

```text
Source
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
Generation
```

I would check whether re-indexing succeeded, whether old and new versions coexist, whether document version metadata is correct, and whether a cache contains stale results.

The fix should include reliable document versioning and an ingestion/indexing process that makes updates observable and idempotent.

**Interview answer:**
> "I would not assume retrieval is stale. I would trace the document from source to index and verify version metadata, ingestion status, duplicate versions and cache invalidation."

---

## 15. Retrieval returns too many irrelevant chunks

### Answer

Increasing Top-K improves recall but can increase context noise. I would separate **candidate K** from **final K**.

```text
Retriever → larger candidate set
              ↓
           Reranker
              ↓
         small final K
              ↓
             LLM
```

I would also consider metadata filtering, better chunking, context compression and query rewriting.

**Interview answer:**
> "I would not solve every recall problem by increasing the final Top-K. I would retrieve broadly, rerank selectively, and send only the most useful evidence to the LLM."

---

## 16. The answer requires information split across chunks

### Answer

This is often a chunking and retrieval-boundary problem.

If a table and its explanatory notes are separated, I would consider:

- structure-aware/table-aware chunking
- preserving parent-child relationships
- retrieving neighboring chunks
- metadata linking related chunks
- multi-chunk synthesis

The goal is to preserve the relationships needed to answer the query rather than treating every chunk as completely independent.

**Interview answer:**
> "I would first check whether the chunking strategy destroyed a relationship required for the answer. If so, I would preserve document structure and retrieve related or neighboring chunks rather than simply making every chunk larger."

---

## 17. Different tenants have documents with the same names

### Answer

Tenant isolation must be enforced **before or at retrieval**, not by asking the LLM to filter results.

Every chunk should carry tenant/authorization metadata, and retrieval should apply the corresponding filter:

```text
User identity
 ↓
Authorization
 ↓
Tenant/document filters
 ↓
Retrieval
 ↓
RAG
```

I would also test isolation explicitly, including attempts to query another tenant's known document names or IDs.

**Interview answer:**
> "The LLM should never decide authorization. Tenant and permission constraints belong at the application and data-access boundary, with defense-in-depth and isolation tests."

---

## 18. Your vector database becomes unavailable

### Answer

I would fail fast with bounded timeouts rather than creating an unbounded retry storm.

Depending on product requirements, I would use:

- timeout
- limited retry with exponential backoff
- circuit breaker
- cached results where safe
- keyword fallback if available
- graceful error response
- alerting and dependency metrics

I would clearly distinguish a temporary dependency failure from **no relevant documents found**.

**Interview answer:**
> "I would use bounded retries and circuit breaking, then degrade gracefully if the product allows it. I would not hide a database outage by endlessly retrying requests."

---

## 19. LLM provider becomes unavailable

### Answer

I would put model access behind an abstraction or gateway so application code is not tightly coupled to one provider.

```text
Application
    ↓
LLM Gateway / Model Router
    ├── Provider A
    └── Provider B
```

The router can use health, timeout, rate-limit and availability signals to select a compatible fallback model. I would validate that the fallback supports the required context size, structured output and quality level.

**Interview answer:**
> "I would use provider/model abstraction and health-aware routing. Failover should consider compatibility and quality, not just whether another API is reachable."

---

## 20. Users ask questions outside the knowledge base

### Answer

The system should have an explicit **insufficient-evidence path**.

```text
Retrieve evidence
      ↓
Evidence sufficient?
   /           \\
 yes            no
 ↓               ↓
answer       abstain / clarify
```

The threshold should be evaluated rather than chosen blindly. I would use retrieval confidence, evidence coverage and/or validation to decide whether the system has enough support.

**Interview answer:**
> "A production RAG system should know when it does not have evidence. I would prefer a clear 'insufficient information' response or clarification over a confident unsupported answer."

---

## 21. RAG quality degrades after a parser change

### Answer

I would compare the old and new parser outputs using the same source documents.

```text
Old parser → parsed output → chunks → embeddings → retrieval
New parser → parsed output → chunks → embeddings → retrieval
```

I would inspect extracted text, headings, tables, page boundaries, metadata, chunk counts and missing content.

If parsed output changed significantly, the parser can be the root cause even though the visible failure appears to be retrieval.

**Interview answer:**
> "I would compare parser output before looking only at vector search. Parsing is upstream of chunking and embeddings, so lost tables, headings or text can directly create a retrieval regression."

---

## 22. You need to support 100× more queries

### Answer

This is primarily **request scale**, not corpus scale.

I would scale stateless API instances horizontally and inspect downstream bottlenecks:

- vector DB capacity
- keyword search capacity
- connection pools
- embedding service
- LLM rate limits
- concurrency limits
- caching
- queues/backpressure

I would use load testing to determine which dependency saturates first.

**Interview answer:**
> "Because the corpus is roughly constant, I would focus on query throughput. I would horizontally scale stateless services and then scale or protect the vector DB, search service and LLM provider based on measured saturation."

---

## 23. Excellent offline metrics but poor production results

### Answer

I would question whether the evaluation set represents production.

Possible reasons:

- production query distribution differs
- long-tail queries are missing
- evaluation data is stale
- production permissions/filters differ
- latency/timeouts affect real requests
- multi-turn context is not represented
- user expectations differ from benchmark labels

I would sample production queries safely, add representative cases to the evaluation set, and compare offline metrics with production feedback and traces.

**Interview answer:**
> "Offline evaluation tells me how the system performs on my test distribution. If production disagrees, I would investigate distribution shift, stale data, filtering, latency and long-tail queries, then improve the evaluation set."

---

## 24. You need to choose between quality, latency and cost

### Answer

I would start from the product SLA rather than choosing the highest-quality architecture automatically.

For each configuration I would compare:

```text
Quality
Latency
Cost
Reliability
```

For example, if the product requires p95 under a particular threshold, configuration A may be unacceptable even if its answer quality is highest.

I would run representative offline evaluation and load testing, then choose the configuration that satisfies the required quality and latency within the cost budget.

**Interview answer:**
> "I would define the acceptable quality, latency and cost boundaries first. Then I would use the same evaluation and load-test workloads to select the configuration that meets the product SLA rather than optimizing a single metric."

---

# Five questions to master first

If time is limited, practice these until you can answer naturally:

1. **RAG suddenly becomes wrong — where do you start and how do you prove the cause?**
2. **Retriever is relevant but generation is poor — what happens between retrieval and generation?**
3. **How do you prove a new embedding model improved the system?**
4. **How do you reduce RAG latency without sacrificing too much quality?**
5. **How do you design RAG for one million documents?**

## Reusable interview framework

```text
Clarify symptom
      ↓
Break pipeline into stages
      ↓
Measure each stage
      ↓
Find failing boundary
      ↓
Form hypothesis
      ↓
Change one major variable
      ↓
Re-run evaluation
      ↓
Compare quality + latency + cost
      ↓
Roll out safely
      ↓
Monitor production
```

**Core principle:** Do not say only what you would change. Explain **how you would prove that the change fixed the problem**.
