# Topic 15 — RRF: Reciprocal Rank Fusion

**Status:** Complete

## Mental model

> RRF is a ranking method used to combine results from multiple retrieval systems using rank positions instead of directly combining raw scores.

```text
Vector Search
      +
Keyword Search
      ↓
     RRF
      ↓
Combined ranking
```

## Formula

```text
RRF(d) = Σ 1 / (k + rank(d))
```

Where `d` is the document/chunk, `rank` is its position in a retrieval list, and `k` is the smoothing constant.

Our current implementation uses `k = 60`. Treat this as a tunable parameter and validate it with retrieval evaluation rather than assuming it is universally optimal.

### Effect of `k`

Larger `k` makes the contribution decay more gradually as rank increases. Smaller `k` makes top ranks relatively more dominant.

## Why RRF?

Vector and keyword retrieval produce scores on different scales and with different meanings. Directly adding those raw scores is not necessarily valid without normalization/calibration.

RRF avoids that cross-retriever score-scale problem by using rank positions.

## Example

```text
Vector:
1. A
2. B
3. C

Keyword:
1. C
2. A
3. D
```

For `A`:

```text
RRF(A) = 1/61 + 1/62
```

For `B`:

```text
RRF(B) = 1/62
```

For `C`:

```text
RRF(C) = 1/63 + 1/61
```

A chunk appearing highly in multiple retrieval lists receives multiple contributions and is therefore promoted.

## Duplicate handling

When the same chunk appears in vector and keyword results, merge it by a stable identifier such as `chunk_id` and accumulate the RRF contributions rather than returning duplicate candidates.

A dictionary is a natural structure for this:

```python
candidates[result.chunk_id] = result
```

## Why `enumerate()` appears here

Ranks are commonly assigned with:

```python
for rank, result in enumerate(results, start=1):
    ...
```

This is the direct project connection for the `enumerate()` interview question.

```text
enumerate()
    ↓
rank
    ↓
RRF contribution
```

## RRF vs weighted score fusion

Weighted fusion can be designed as a combination of normalized/calibrated scores. RRF instead combines rank positions.

```text
Weighted score fusion → combine scores
RRF                  → combine ranks
```

A weighted RRF variant can also assign different importance to retrievers, but the weights should be evaluation-driven.

## Candidate depth

If each retriever returns only a very small top-K, a relevant chunk outside that depth never reaches RRF. Increasing candidate depth can improve recall but increases downstream work, especially reranking.

```text
candidate depth ↑
      ↓
recall may improve
      ↓
RRF/reranking work ↑
      ↓
latency/cost ↑
```

## RRF before reranking

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

RRF is candidate fusion. Reranking is a later, more precise relevance-ranking stage.

## What RRF does not do

RRF does not understand semantic meaning, replace embeddings, replace keyword retrieval or replace reranking. Its job is to fuse ranked lists.

## Debugging RRF

When a relevant chunk is missing from the final results, inspect:

```text
1. Did vector search retrieve it?
2. Did keyword search retrieve it?
3. What rank did it receive?
4. Did it enter the RRF candidate pool?
5. What RRF score did it receive?
6. Did the reranker push it down?
```

This separates retrieval-recall problems from fusion/reranking problems.

## RRF score meaning

An RRF score is a fusion score used for ranking candidates. It is not a probability, relevance percentage, or the same thing as a vector similarity score.

## Project connection

Our `ai-platform` retrieval flow uses vector and keyword results, assigns ranks, accumulates RRF contributions by chunk ID, sorts the fused candidates, and optionally sends the candidate pool to the reranker.

## Likely interview questions

### Why not simply add vector and keyword scores?

> Their score scales and semantics differ, so direct addition requires reliable normalization/calibration. RRF avoids that dependency by combining rank positions.

### Why did you choose `k = 60`?

> It is our current configuration, but I would treat it as a tunable parameter and validate it against representative retrieval queries and evaluation metrics.

### Why does RRF work well for hybrid search?

> It lets independently ranked retrieval systems contribute evidence without requiring their raw scores to be directly comparable.

### What if the relevant result isn't in either list?

> RRF cannot recover it. That is a first-stage retrieval recall problem, so I would inspect embeddings, keyword retrieval, chunking, filtering and candidate depth.

### Can RRF be weighted?

> Yes, a weighted variant can give different importance to retrievers, but the weights should be determined through evaluation.

## Checklist

- [x] RRF definition
- [x] formula
- [x] `k` parameter
- [x] rank-based fusion
- [x] duplicate handling
- [x] `enumerate()` project connection
- [x] score fusion vs rank fusion
- [x] weighted RRF concept
- [x] candidate depth
- [x] RRF → reranker
- [x] debugging
- [x] score interpretation
