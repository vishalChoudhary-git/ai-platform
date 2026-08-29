# Topic 14 — Reranking & Retrieval Optimization

**Status:** Complete

## Mental model

```text
Retriever → find candidates
RRF       → combine candidates
Reranker  → choose/order the best candidates
```

## Retriever vs reranker

**Retriever:** optimized for fast candidate generation over a large corpus.

**Reranker:** optimized for more precise relevance scoring over a much smaller candidate set.

Typical pipeline:

```text
1M chunks
   ↓
Vector / Keyword retrieval
   ↓
20–100 candidates
   ↓
Reranker
   ↓
Top 5–10
```

## Bi-encoder vs cross-encoder

### Bi-encoder

Query and documents are embedded separately, then compared using vector similarity. This is suitable for first-stage retrieval because document embeddings can be precomputed.

### Cross-encoder / reranker

The model receives the query and candidate together and scores their relevance. It can model query-document interaction more deeply, but is more expensive, so it is normally applied only to a small candidate set.

## Why rerank after RRF?

```text
Vector Search
      +
Keyword Search
      ↓
     RRF
      ↓
Hybrid candidate pool
      ↓
   Reranker
      ↓
Final Top-K
```

RRF combines complementary retrieval signals. The reranker then performs a more precise relevance judgment on the fused candidates.

## Candidate size trade-off

A larger candidate pool can improve recall, but it increases reranker latency and cost. Choose the smallest candidate set that provides sufficient recall based on evaluation.

```text
candidate_top_k ↑
    ↓
recall may improve
    ↓
reranking work ↑
    ↓
latency / cost ↑
```

## Reranker score vs vector score

Do not treat them as interchangeable. A vector similarity score and a reranker score come from different scoring mechanisms and have different meanings.

## Reranker is not mandatory

A reranker is an engineering trade-off. It may be unnecessary when the corpus is small, latency requirements are extremely strict, or first-stage retrieval is already good enough.

## Filtering before reranking

Authorization and metadata constraints should be enforced before expensive reranking where possible:

```text
permission / metadata filtering
        ↓
retrieval
        ↓
RRF
        ↓
reranking
```

This avoids ranking content the user is not allowed to access and reduces wasted computation.

## Failure and fallback

If reranking is unavailable, a production system may fall back to RRF ordering when acceptable rather than making the entire RAG request fail. This should be an explicit product/reliability decision.

## Evaluation

Compare:

```text
Hybrid → Top-K
```

against:

```text
Hybrid → Reranker → Top-K
```

Measure retrieval quality, answer quality, latency and cost. A reranker should not be assumed to improve every workload.

## Project connection

`ai-platform` uses a `Reranker` abstraction so retrieval orchestration does not depend on a specific reranking implementation. This follows the same abstraction and dependency-injection principles used elsewhere in the platform.

## Likely interview questions

### Why did you add reranking to your RAG pipeline?

> Initial retrieval is optimized for efficient candidate generation. We fuse complementary retrieval signals with RRF and use a reranker on the smaller candidate set for more precise query-document relevance scoring before selecting the final context.

### Why not use a cross-encoder over the whole corpus?

> It is computationally expensive because it evaluates the query and document together. First-stage retrieval narrows the search space, then the cross-encoder is used only on a manageable candidate set.

### How do you choose candidate size?

> I would benchmark candidate depth against retrieval recall, final answer quality, reranking latency and cost, and choose the smallest candidate pool that maintains the required quality.

### Can reranking make retrieval worse?

> Yes. Poor model fit, domain mismatch or a weak candidate set can result in worse final ordering. This is why reranking must be evaluated rather than assumed to help.

### What is the difference between retrieval and reranking?

> Retrieval prioritizes broad, fast candidate discovery; reranking prioritizes precise ordering of a much smaller set.

## Checklist

- [x] retriever vs reranker
- [x] bi-encoder
- [x] cross-encoder
- [x] candidate generation
- [x] candidate depth trade-offs
- [x] RRF → reranker ordering
- [x] latency/cost trade-offs
- [x] metadata/authorization filtering before reranking
- [x] fallback thinking
- [x] evaluation
- [x] project-based explanation
