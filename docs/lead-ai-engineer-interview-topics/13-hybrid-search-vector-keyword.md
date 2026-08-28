# Topic 13 — Hybrid Search: Vector + Keyword Retrieval

**Status:** Complete

## Focus
Dense vector retrieval, lexical/BM25-style retrieval, parallel search, metadata filtering, rank fusion, and choosing hybrid retrieval.

## Mental model

```text
                         User Query
                             |
                +------------+------------+
                |                         |
                v                         v
          Vector Search              Keyword Search
          semantic match             lexical/exact match
                |                         |
                +------------+------------+
                             v
                            RRF
                             |
                             v
                       Hybrid Candidates
                             |
                          Reranker
                             |
                          Final Top-K
```

## Why hybrid search?

Vector search is strong at semantic meaning and paraphrased natural-language questions. Keyword/lexical search is strong at exact terms, identifiers, codes, names, numbers and rare domain-specific expressions.

```text
Vector search
→ semantic similarity

Keyword search
→ lexical/exact matching
```

Using both gives complementary retrieval signals.

## Vector search vs keyword search

### Vector search

Example:

```text
Query: "How much money did the company make?"

Document: "Net revenue reached $25M."
```

The wording differs, but the meaning is related. Semantic retrieval can still find the relevant chunk.

### Keyword search

Example:

```text
Query: "INV-784392"
```

Exact lexical matching is useful for identifiers and rare terms.

## BM25

BM25 is a common lexical retrieval algorithm. At a high level, it scores documents based on query-term relevance while accounting for term frequency and document length.

For interview purposes, know the purpose rather than memorizing the full formula.

## When each signal is especially useful

### Vector search

- natural-language questions
- paraphrases
- conceptual queries
- semantic relationships

### Keyword search

- exact identifiers
- product IDs
- invoice/account numbers
- error codes
- legal clauses
- technical terms
- dates and numbers
- exact phrases

### Mixed query

```text
"Why did account AC-93821 revenue decline?"
```

`AC-93821` benefits from lexical matching while `revenue decline` benefits from semantic matching.

## Parallel retrieval

Vector and keyword searches are independent operations for the same query, so they can run concurrently in an async service:

```python
vector_results, keyword_results = await asyncio.gather(
    vector_search(query),
    keyword_search(query),
)
```

This connects directly to the async/await concepts from earlier topics.

## Why RRF after hybrid retrieval?

The two retrievers can produce scores on different scales, so blindly adding raw scores is not necessarily meaningful.

RRF works from rank positions instead:

```text
Vector ranked list
        +
Keyword ranked list
        ↓
       RRF
        ↓
combined ranking
```

This lets a chunk receive contributions from both retrievers without requiring cross-retriever score calibration.

See Topic 15 for the deeper RRF discussion.

## Why not simply concatenate result lists?

Concatenation creates duplicates and does not provide a principled combined ranking. Fusion should account for the relative rank of an item in each retrieval result set.

## Weighted fusion

A system can also use weighted signals, for example giving semantic retrieval more influence than lexical retrieval. If combining raw scores, score normalization/calibration becomes important because the raw score distributions may not be comparable.

RRF is attractive when we want a simple rank-based fusion mechanism without requiring comparable score scales.

## Metadata and permission filtering

In an enterprise RAG system, retrieval should respect tenant, document and permission constraints.

Conceptually:

```text
Query
 ↓
metadata / permission constraints
 ↓
retrieval
 ↓
RRF
 ↓
reranking
```

Avoid treating authorization as a cosmetic post-processing step. The retrieval boundary should only expose candidates the caller is allowed to access.

## Candidate overlap

A useful diagnostic is overlap between the vector and keyword candidate sets.

```text
Vector top-20
Keyword top-20
Overlap = 12
```

Low overlap is not automatically bad; it may mean the retrievers are providing complementary signals. High overlap may mean they are finding similar results. Overlap is a diagnostic signal, not a standalone quality metric.

## Tuning hybrid retrieval

Potential parameters include:

- vector candidate depth
- keyword candidate depth
- RRF constant
- metadata filters
- similarity threshold
- reranker candidate size
- lexical/BM25 configuration

Use an evaluation dataset rather than tuning blindly:

```text
Evaluation set
    ↓
run retrieval experiments
    ↓
measure retrieval + answer quality
    ↓
compare latency/cost
    ↓
choose configuration
```

## Debugging hybrid retrieval

Inspect each stage independently:

```text
Query
 ↓
Vector results
 ↓
Keyword results
 ↓
Candidate overlap
 ↓
RRF ranking
 ↓
Reranker ranking
 ↓
Final chunks
```

This helps identify whether poor results originate in semantic retrieval, lexical retrieval, fusion or reranking.

## Project connection — ai-platform

Our retrieval architecture combines semantic/vector retrieval with keyword retrieval, fuses the ranked results using RRF, and can then pass the candidate set through a reranker. This is an example of using multiple complementary retrieval signals before expensive fine-grained reranking.

## High-value interview questions

### Why hybrid search instead of vector search alone?

> Vector search is strong at semantic similarity, but exact identifiers, codes, names, numbers and rare technical terms can benefit from lexical retrieval. Combining both improves coverage across different query types.

### What is BM25?

> A common lexical retrieval algorithm that scores documents based on query-term relevance, term frequency and document length.

### Why not add vector and keyword scores directly?

> Their raw score distributions may have different scales and meanings, so direct addition can be misleading without normalization/calibration. Rank-based fusion such as RRF avoids that dependency.

### Why RRF?

> It combines ranked lists using rank contributions, allowing complementary retrievers to influence the final ordering without requiring their raw scores to be directly comparable.

### Can vector and keyword retrieval run concurrently?

> Yes. When the operations are independent and asynchronous, `asyncio.gather()` can execute them concurrently and reduce retrieval latency.

### When would keyword search be more useful than vector search?

> Exact identifiers, codes, names, numbers, rare terms and exact phrase matching are common cases.

### What does candidate overlap tell you?

> It tells you how similar or complementary the retrieval signals are. It is useful for diagnosis, but it is not by itself a measure of retrieval quality.

### What happens after RRF?

> We can rerank the fused candidate set with a stronger relevance model and then select the final top-K context for the RAG generation step.

### How would you tune hybrid retrieval?

> I'd vary candidate depths, fusion parameters and reranking size and compare them on representative evaluation queries, measuring retrieval quality, answer quality, latency and cost.

### How would you debug poor hybrid retrieval?

> Inspect vector results, keyword results, overlap, RRF scores/ranks, reranker output and final context separately so we can identify which stage is losing relevance.

## Checklist

- [x] vector vs keyword retrieval
- [x] semantic vs lexical matching
- [x] BM25 concept
- [x] exact identifiers/use cases
- [x] mixed-query reasoning
- [x] parallel retrieval with `asyncio.gather()`
- [x] RRF connection
- [x] raw-score normalization issue
- [x] metadata/permission filtering
- [x] candidate overlap
- [x] tuning
- [x] debugging
- [x] project-based interview answers
