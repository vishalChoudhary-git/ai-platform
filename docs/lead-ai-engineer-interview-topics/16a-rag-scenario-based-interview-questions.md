# Topic 16A — RAG Scenario-Based Engineering Interview Questions

**Status:** Complete

> These are intentionally **scenario-based engineering questions**, not definition questions. The goal is to reason about how a RAG system fails, how to prove the root cause, and how to redesign it.

## How to answer scenario questions

Use this pattern:

```text
1. Identify the failure symptom
2. Break the RAG pipeline into stages
3. Measure each stage
4. Isolate the bottleneck/root cause
5. Apply the smallest appropriate change
6. Re-run evaluation
7. Verify quality + latency + cost did not regress
```

A strong Lead AI Engineer answer should avoid immediately saying **"change the prompt"** or **"use a better embedding model"** without first identifying the failure stage.

---

# Scenario 1 — RAG suddenly starts giving incorrect answers

### Question

Your RAG system has been working well for months. Suddenly, users report that answers are incorrect.

**What is the first thing you investigate? How would you prove the root cause?**

### Interview thinking

Do not immediately blame the LLM.

Break the request into:

```text
Query
  ↓
Query embedding
  ↓
Vector / keyword retrieval
  ↓
RRF
  ↓
Reranking
  ↓
Context construction
  ↓
LLM
  ↓
Answer
  ↓
Validation / citation
```

First check whether the **correct evidence is still being retrieved**.

Then compare the current system against a known-good baseline:

```text
Before change / known-good period
              vs
Current production
```

Inspect:

- retrieval results
- retrieval scores/ranks
- RRF output
- reranker output
- final context
- model/prompt version
- document/index changes
- embedding-model changes
- metadata/permission filters

### How to prove the root cause

Use a fixed evaluation set and compare each stage.

```text
Same queries
     ↓
Old configuration → metrics
Current configuration → metrics
```

If Recall@K dropped significantly after an indexing/embedding change, retrieval is a strong candidate.

If retrieval is unchanged but the final answer quality dropped after a model/prompt change, investigate generation.

### Strong interview answer

> "I'd first determine whether this is a retrieval failure or a generation failure. I'd run representative failing queries through the pipeline and inspect the retrieved chunks, RRF/reranker output and final context. I'd compare those results with a known-good baseline and check recent changes to documents, embeddings, prompts and models. Then I'd use stage-level metrics such as Recall@K and answer faithfulness/correctness to prove where the regression occurred rather than guessing."

---

# Scenario 2 — Retriever returns relevant documents, but answer quality is poor

### Question

Your retriever returns relevant documents, but the generated answer is still poor.

**What could be going wrong between retrieval and generation?**

### Investigate

```text
Relevant chunks retrieved
        ↓
       ???
        ↓
Poor answer
```

Potential problems:

- relevant chunk was retrieved but ranked too low
- reranker removed or demoted useful evidence
- context construction omitted important chunks
- too many irrelevant chunks were included
- context ordering is poor
- duplicated chunks consume context
- important information is truncated
- prompt does not clearly separate evidence from instructions
- model misunderstands conflicting context
- context exceeds an effective context budget
- structured output/validation is incorrect

### Debugging approach

Save the exact context sent to the LLM for a failing request.

```text
Retrieved chunks
       ↓
RRF result
       ↓
Reranker result
       ↓
Final context
       ↓
LLM input
```

Then ask:

> **Was the evidence that supports the correct answer actually present in the final LLM context?**

If yes, the problem is likely in context construction, prompting or generation.

If no, investigate reranking/context selection.

### Strong interview answer

> "If retrieval is relevant but answers are poor, I'd inspect the pipeline between retrieval and generation. In particular, I'd check whether the useful evidence survives reranking and context construction, whether irrelevant or conflicting chunks dominate the context, and whether important content is truncated. I'd capture the exact LLM input and compare it with the retrieved evidence before changing the model or prompt."

---

# Scenario 3 — You changed the embedding model

### Question

You replace your embedding model with a newer model.

**How would you know whether the change actually improved the RAG system? What metrics would you measure before and after?**

### Do not evaluate only the final answer

Create a fixed evaluation dataset:

```text
Query
Expected relevant chunks/documents
Expected answer
Expected citations
```

Run both systems against exactly the same queries:

```text
                 Evaluation Set
                       ↓
             ┌─────────┴─────────┐
             ↓                   ↓
       Old embeddings       New embeddings
             ↓                   ↓
        Retrieval            Retrieval
             ↓                   ↓
        RAG answer            RAG answer
```

### Retrieval metrics

Track:

- Recall@K
- Precision@K
- MRR
- NDCG@K

### Generation metrics

Track:

- faithfulness / groundedness
- answer correctness
- answer relevance
- citation correctness

### Production metrics

Also compare:

- latency
- token usage
- cost
- failure rate

### Important point

An embedding model is not automatically better just because it is newer.

```text
Better embedding
        ↓
should produce
        ↓
better measured retrieval / answer quality
```

### Strong interview answer

> "I'd use a fixed evaluation set and run the old and new embedding configurations against the same queries. I'd compare retrieval metrics such as Recall@K, MRR and NDCG, then compare final answer faithfulness and correctness. I'd also check latency and cost. I would only keep the new embedding model if it provides a meaningful quality improvement without unacceptable operational regression."

---

# Scenario 4 — One question requires five different documents

### Question

A user asks a question that requires information from **five different documents**.

**How would you design retrieval and context construction?**

### Problem

A naive top-K retrieval can return:

```text
Doc A → 5 chunks
Doc B → 3 chunks
Doc C → 2 chunks
```

while completely missing Doc D and Doc E.

The answer may therefore have excellent local relevance but incomplete evidence.

### Possible approach

Use retrieval depth larger than the final context size:

```text
Query
  ↓
Hybrid retrieval
  ↓
Large candidate pool
  ↓
RRF
  ↓
Reranking
  ↓
Diversity / document coverage
  ↓
Final context
```

Depending on the question, introduce **document-level coverage** so that the system does not spend the entire context budget on one document.

For example:

```text
Doc A → 2 useful chunks
Doc B → 1 useful chunk
Doc C → 1 useful chunk
Doc D → 1 useful chunk
Doc E → 1 useful chunk
```

The exact allocation should be evaluated rather than hard-coded universally.

### Context construction

Preserve provenance:

```text
[Doc A - Page 10]
...

[Doc B - Page 4]
...

[Doc C - Page 18]
...
```

This helps the model reason over multiple sources and allows trustworthy citations.

### Strong interview answer

> "I'd retrieve a sufficiently large candidate pool, then rerank it and consider document coverage so one document doesn't consume the entire context budget. I'd preserve document/page provenance in the final context. For multi-document questions, I'd evaluate both retrieval recall and whether the final context contains evidence from all required sources."

---

# Scenario 5 — RAG works at 10,000 documents but now has 1 million

### Question

Your RAG system works perfectly with 10,000 documents.

Now the corpus grows to **1 million documents**.

**What breaks first, and how would you redesign the architecture?**

### Think in terms of scale

Potential bottlenecks include:

```text
Ingestion
Embedding generation
Vector index size
Keyword index size
Storage
Search latency
Reranking cost
Metadata filtering
Network traffic
LLM context size
Observability volume
```

The important point is that you should not simply increase `top_k`.

### Retrieval architecture

Use an indexed retrieval system designed for large-scale search:

```text
1M+ documents
      ↓
Partition / shard where appropriate
      ↓
Metadata / tenant filtering
      ↓
Vector + keyword retrieval
      ↓
RRF
      ↓
Bounded candidate set
      ↓
Reranker
      ↓
Small final Top-K
```

### Control expensive operations

The expensive stages should operate on progressively smaller sets:

```text
1,000,000 documents
        ↓
indexed retrieval
        ↓
100 candidates
        ↓
reranking
        ↓
5–10 chunks
        ↓
LLM
```

Do not run a cross-encoder/reranker across the entire corpus.

### Ingestion scalability

For large ingestion workloads:

- batch embedding requests
- use asynchronous workers
- queue ingestion jobs
- avoid re-embedding unchanged content
- process documents incrementally
- make ingestion idempotent

### Strong interview answer

> "At one million documents, I'd look first at indexing, retrieval latency, storage and the cost of downstream candidate processing. I'd use scalable vector and lexical indexes, enforce tenant/metadata filters early, keep first-stage retrieval efficient, and pass only a bounded candidate set to the reranker. I'd also make ingestion asynchronous and incremental, with batching and change detection so unchanged documents are not reprocessed."

---

# Scenario 6 — Correct document is not retrieved

### Question

A user asks a question, but the correct document is not present in the retrieved results.

**What would you do?**

### Debug systematically

```text
Query
 ↓
Did parsing preserve the information?
 ↓
Did chunking preserve the relevant context?
 ↓
Did the embedding represent the query/content well?
 ↓
Did vector search find it?
 ↓
Did keyword search find it?
 ↓
Did metadata filters accidentally exclude it?
 ↓
Did RRF/reranking remove or demote it?
```

### Possible fallback strategies

Depending on the product:

- query rewriting
- query expansion
- hybrid retrieval
- broader candidate depth
- adjusted similarity threshold
- alternate retrieval strategy
- clarification question
- explicit insufficient-information response

Do not blindly lower similarity thresholds. That can increase noisy retrieval.

### Strong interview answer

> "I'd first identify why the document was missed rather than immediately lowering thresholds. I'd inspect parsing, chunking, embeddings, vector and keyword results, metadata filters and reranking. Depending on the failure, I could use query rewriting, hybrid retrieval or a broader candidate pool. If we still don't have sufficient evidence, the system should abstain rather than fabricate an answer."

---

# Scenario 7 — RAG answer looks correct but is actually wrong

### Question

The response sounds convincing and contains a citation, but the answer is actually wrong.

**How would you debug it?**

### Pipeline investigation

```text
Query
  ↓
Retrieval
  ↓
RRF
  ↓
Reranking
  ↓
Context
  ↓
Generation
  ↓
Citation
  ↓
Validation
```

A citation alone does not prove correctness.

Check:

1. Was the cited chunk actually relevant?
2. Did the chunk support the exact claim?
3. Was there conflicting evidence in another document?
4. Did reranking select the wrong source?
5. Did the model infer information not present in the source?
6. Is the source itself outdated or incorrect?

### Key distinction

```text
Citation exists
      ≠
Citation supports the claim
```

### Strong interview answer

> "I'd verify whether the citation actually supports the specific claim, not just whether a citation exists. I'd trace the answer back through retrieval, reranking and context construction, then compare the generated claim against the source text and check for conflicting or stale documents. This separates citation presence from true grounding and correctness."

---

# Scenario 8 — Reranker improves quality but latency becomes unacceptable

### Question

After adding a reranker, answer quality improves by 5%, but p95 latency doubles.

**Would you keep it?**

### Answer: not automatically

This is a quality/latency/cost trade-off.

Measure:

```text
Without reranker
→ quality / p95 / cost

With reranker
→ quality / p95 / cost
```

Then investigate whether the candidate set is too large.

```text
100 candidates
      ↓
reranker
```

may become:

```text
30 candidates
      ↓
reranker
```

if evaluation shows that recall remains sufficient.

Other options:

- use a faster reranker
- rerank only difficult queries
- reduce candidate depth
- cache repeated queries
- move some work to a faster infrastructure path
- evaluate whether the 5% quality gain is worth the latency budget

### Strong interview answer

> "I'd treat the 5% improvement as a measured trade-off, not an automatic win. I'd benchmark different candidate sizes and determine whether we can retain most of the quality improvement with lower reranking cost. The final decision depends on the product's latency SLA and quality requirements."

---

# Scenario 9 — Hybrid search does not improve results

### Question

You add keyword search + RRF to a vector-only RAG system, but evaluation shows almost no quality improvement.

**What do you do?**

Do not assume hybrid search must help.

Investigate:

```text
Vector results
Keyword results
       ↓
Candidate overlap
       ↓
RRF ranking
       ↓
Reranking
       ↓
Final Top-K
```

Questions to ask:

- Do the evaluation queries actually contain lexical/exact-match cases?
- Is keyword search configured correctly?
- Is the corpus mostly semantic natural-language content?
- Is RRF changing the candidate ranking?
- Is the reranker undoing any useful difference?
- Is the additional latency justified?

### Strong interview answer

> "I'd compare the hybrid pipeline against the vector-only baseline on the same evaluation set. If the workload doesn't contain many exact-match queries, hybrid retrieval may provide little benefit. I'd inspect keyword recall, candidate overlap and RRF output before deciding whether to keep the added complexity."

---

# Scenario 10 — Production quality degrades after a document update

### Question

A customer updates an important policy document. Shortly afterward, the assistant starts returning answers based on the old policy.

**Where would you investigate?**

Think about the complete indexing lifecycle:

```text
Document updated
      ↓
Change detected?
      ↓
Re-parse
      ↓
Re-chunk
      ↓
Re-embed
      ↓
Index updated
      ↓
Old chunks removed/deactivated?
      ↓
Cache invalidated?
      ↓
Retrieval
```

Potential problems:

- change detection failed
- old embeddings remain indexed
- stale chunks were not deleted/deactivated
- indexing job failed
- cache returned an old answer
- document version metadata is incorrect
- retrieval does not prioritize the latest version

### Strong interview answer

> "I'd trace the document update through the indexing pipeline and verify that the new version was parsed, chunked, embedded and indexed, and that the old version was removed or deactivated. I'd also inspect cache invalidation because even correct retrieval can still be hidden by a stale cached response."

---

# Scenario 11 — Answers are good but users complain about missing information

### Question

The answers are usually correct, but users say the system often misses important details.

**What would you investigate?**

This may be a **recall** problem rather than a generation problem.

Check:

```text
Recall@K
↓
Were all relevant chunks retrieved?
```

Potential causes:

- candidate depth too small
- poor chunking
- query/document vocabulary mismatch
- vector-only retrieval misses exact terms
- metadata filters are too restrictive
- reranker candidate pool is too small

Potential fixes:

```text
better chunking
query rewriting
hybrid retrieval
larger first-stage candidate pool
better filtering logic
reranker tuning
```

But validate each change against the evaluation set.

---

# Scenario 12 — The system retrieves too much irrelevant context

### Question

The retriever has high recall, but the LLM receives too many irrelevant chunks and answer quality is inconsistent.

**How would you improve it?**

Think:

```text
High recall
   ↓
large candidate pool
   ↓
poor precision
   ↓
noisy context
```

Possible solution:

```text
Broad retrieval
      ↓
RRF
      ↓
Reranker
      ↓
Context compression / filtering
      ↓
Small high-quality context
      ↓
LLM
```

The objective is not simply maximum recall or minimum context. It is the right balance for the workload.

---

# Rapid-Fire Scenario Questions

Use these for self-testing without looking at the answers above.

1. Your RAG suddenly becomes inaccurate after a deployment. What do you inspect first?
2. Retrieval is correct but the LLM answer is wrong. What stage do you inspect?
3. Recall@10 improves but answer quality gets worse. How is that possible?
4. Your reranker improves NDCG but doubles p95 latency. What would you tune?
5. Keyword search finds exact invoice IDs that vector search misses. What architecture would you use?
6. A question requires five documents but Top-10 contains chunks from only one document. What would you change?
7. The correct document exists but retrieval never finds it. What fallback strategies could you use?
8. A customer updates a document but the assistant still uses the old version. What could be stale?
9. Your embedding model change improves retrieval but increases cost. How do you decide whether to keep it?
10. Your RAG works for 10,000 documents but becomes slow at 1 million. Which components do you scale first?
11. Your citations exist but do not actually support the answer. How do you detect this?
12. Hybrid search adds latency but provides no measurable quality improvement. Would you keep it?
13. Reranking improves quality only for difficult queries. Should every query be reranked?
14. A user has access to 100 documents but retrieval returns a highly relevant document from another tenant. Where should the problem be fixed?
15. The model says "I don't know" even though the correct chunk was retrieved. What would you inspect?

---

# Lead Engineer Mental Model

When given any RAG production scenario, think in this order:

```text
                  USER QUERY
                      ↓
                 QUERY LAYER
                      ↓
             ┌────────┴────────┐
             ↓                 ↓
          VECTOR            KEYWORD
          SEARCH             SEARCH
             └────────┬────────┘
                      ↓
                     RRF
                      ↓
                  RERANKER
                      ↓
             AUTHORIZED CHUNKS
                      ↓
             CONTEXT CONSTRUCTION
                      ↓
                     LLM
                      ↓
              ANSWER + CITATIONS
                      ↓
                  VALIDATION
                      ↓
                  EVALUATION
             ┌────────┼────────┐
             ↓        ↓        ↓
          Quality   Latency   Cost
```

The key interview principle is:

> **Don't guess the failing component. Instrument the pipeline, isolate the failure, change one thing, and prove the improvement with evaluation.**

## Project connection — ai-platform

These scenarios map directly to the architecture we have been discussing:

```text
Storage / ingestion
        ↓
Parsing + chunking
        ↓
Embeddings
        ↓
Vector + keyword retrieval
        ↓
RRF
        ↓
Reranker abstraction
        ↓
Permission / metadata filtering
        ↓
RAG context
        ↓
LLM
```

The interview goal is not to memorize every optimization. It is to demonstrate that you can **diagnose, measure, and evolve a production RAG system**.

## Checklist

- [x] sudden RAG quality regression
- [x] retrieval-good / generation-bad scenario
- [x] embedding-model evaluation
- [x] multi-document retrieval
- [x] 10K → 1M scaling
- [x] missing-document fallback
- [x] convincing but incorrect answer
- [x] reranker latency trade-off
- [x] hybrid search evaluation
- [x] stale document/index/cache scenario
- [x] recall vs precision diagnosis
- [x] noisy-context scenario
- [x] rapid-fire interview questions
- [x] production debugging mental model
