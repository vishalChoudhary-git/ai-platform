# Topic 18 — LLM Cost & Latency Optimization

**Status:** Complete

## Core principle

> Measure first, identify the bottleneck, optimize it, then re-measure and verify that quality has not regressed.

Production AI optimization is a balance of **quality, latency and cost** rather than cost alone.

## Where latency comes from

```text
User Query
   ↓
Query Embedding
   ↓
Vector Search + Keyword Search
   ↓
RRF
   ↓
Reranker
   ↓
Context Construction
   ↓
LLM
   ↓
Response
```

Measure each stage independently before deciding what to optimize.

## Parallelism

Independent I/O operations can run concurrently:

```python
vector_results, keyword_results = await asyncio.gather(
    vector_search(query),
    keyword_search(query),
)
```

This can reduce wall-clock latency compared with sequential calls.

## Token reduction

Large prompts increase input token usage and can increase latency/cost. Reduce unnecessary context through:

- better retrieval
- reranking
- context compression
- concise prompts
- limiting unnecessary conversation history

Example:

```text
20 retrieved chunks
        ↓
rerank/compress
        ↓
5 useful chunks
        ↓
LLM
```

## Semantic caching

A semantic cache can return a previous result for a sufficiently similar query instead of invoking the LLM again.

```text
Query
  ↓
Semantic cache
  ├── hit  → cached response
  └── miss → LLM → store result
```

### Exact vs semantic cache

**Exact cache:** requires an exact key/request match.

**Semantic cache:** compares query meaning/similarity and can reuse a response for semantically similar requests.

Semantic caching is more flexible but requires careful similarity thresholds and freshness/invalidation rules.

## Cache invalidation

Caching must account for knowledge freshness.

If a document changes, an old answer may become stale. Strategies can include:

- TTL
- document/content versioning
- cache namespaces
- explicit invalidation
- index/version keys

Core interview point:

> Caching is only safe when freshness and invalidation are part of the design.

## Model selection

Do not default every request to the largest model.

```text
simple extraction/classification → smaller model
complex reasoning               → stronger model
embedding                        → embedding model
reranking                        → reranker model
```

Choose the **cheapest model that satisfies the required quality**.

## Model routing

A router can select a model based on task complexity, latency, cost or capability:

```text
Query
  ↓
Router
  ├── simple → Model A
  └── complex → Model B
```

## Streaming

Streaming mainly improves **perceived latency**. It does not necessarily reduce total computation.

Important metrics:

```text
TTFT = Time To First Token
Total latency = time until generation completes
```

A fast TTFT can make an application feel responsive even when total generation time remains significant.

## Batching

For workloads such as embedding many chunks, batching can reduce network round trips and improve throughput.

```text
100 individual calls
        ↓
multiple batches
```

Trade-offs include batch size, memory use and waiting time.

## Embedding reuse

Do not regenerate embeddings for unchanged content unnecessarily. Deterministic identifiers/content hashes can help detect whether a chunk actually changed and needs re-embedding.

## Retrieval optimization

LLM latency is only one part of the request. Measure:

```text
embedding latency
vector DB latency
keyword latency
RRF time
reranker latency
network overhead
LLM TTFT
LLM generation time
```

## Candidate size

A larger retrieval candidate set can improve recall but increases reranker work.

```text
candidate size ↑
     ↓
recall may improve
     ↓
reranker work ↑
     ↓
latency/cost ↑
```

Choose candidate depth using evaluation rather than intuition.

## Prompt optimization

Reduce:

- unnecessary instructions
- repeated context
- redundant conversation history
- verbose templates

But do not optimize token count at the expense of clarity, grounding or correctness.

## Cost per request

Think in terms of total request cost:

```text
embedding cost
+ retrieval infrastructure
+ reranking cost
+ LLM input tokens
+ LLM output tokens
```

Then estimate:

```text
monthly cost ≈ requests × average cost/request
```

## Quality vs latency vs cost

Optimization is a multi-objective problem.

```text
                 Quality
                    ▲
                    │
                    │
Cost ◄──────────────┼──────────────► Latency
```

A cheaper/faster configuration is not necessarily better if it causes unacceptable quality loss.

## Project connection

In the AI Knowledge Assistant project, context compression reduces unnecessary context sent to the model, while Redis-backed semantic caching can avoid repeated model calls for semantically similar queries. These are concrete examples of cost and latency optimization.

## Likely interview questions

### How would you reduce LLM cost?

> Reduce unnecessary input/output tokens, use semantic caching where appropriate, route simple tasks to smaller models, batch suitable workloads, reuse embeddings and avoid unnecessary LLM calls.

### How would you reduce RAG latency?

> Measure every stage, parallelize independent I/O, optimize vector retrieval, limit reranking candidates, cache repeated work, compress context and use streaming to improve perceived responsiveness.

### Does streaming reduce total inference time?

> Not necessarily. Streaming mainly reduces time-to-first-visible-output and improves perceived latency.

### Exact cache vs semantic cache?

> Exact caching matches the same request; semantic caching can reuse results for sufficiently similar requests but requires similarity thresholds and freshness/invalidation strategies.

### How do you handle cache invalidation?

> Tie cache entries to a freshness/version strategy such as TTL or document/index versioning, and explicitly invalidate entries when underlying knowledge changes when required.

### Why not always use the cheapest model?

> Because optimization must preserve the required quality. I choose the cheapest model that meets the quality and capability requirements.

### How would you optimize a slow RAG pipeline?

> Instrument the pipeline first, identify the actual bottleneck, then optimize retrieval, parallelism, candidate size, caching, context size or model configuration and re-measure both performance and quality.

## Checklist

- [x] latency decomposition
- [x] async parallelism
- [x] token reduction
- [x] context compression
- [x] exact caching
- [x] semantic caching
- [x] cache invalidation
- [x] model selection
- [x] model routing
- [x] streaming / TTFT
- [x] batching
- [x] embedding reuse
- [x] candidate-size tuning
- [x] prompt optimization
- [x] cost per request
- [x] quality/latency/cost trade-offs
- [x] project example
