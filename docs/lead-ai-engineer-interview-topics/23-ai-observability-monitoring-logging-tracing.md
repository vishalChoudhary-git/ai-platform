# Topic 23 — AI Observability, Monitoring, Logging & Tracing

**Status:** Complete

## Goal

Be able to explain how we observe a production AI/RAG system, debug failures quickly, and measure both system health and AI quality.

## 1. What is observability?

> **Observability is the ability to understand the internal behavior of a system from the data it emits.**

Traditional production observability is built around three primary signals:

```text
Logs    → what happened?
Metrics → how often / how much?
Traces  → where did it happen across the request?
```

For AI systems, we need an additional layer:

```text
AI quality / evaluation
→ was the system actually useful and correct?
```

So the AI mental model becomes:

```text
System health
   +
Request execution
   +
AI behavior / quality
   ↓
Production observability
```

---

# 2. Logs

## Definition

Logs are timestamped records of discrete events.

Examples:

```text
request_started
retrieval_completed
reranker_failed
llm_timeout
```

Use logs when you need detailed event-level information.

## Good production logs

Include structured fields such as:

```text
request_id
tenant_id
user_id (when appropriate and safe)
service
operation
model
provider
latency
status
error type
```

Prefer structured JSON logs over arbitrary strings when possible.

Example:

```json
{
  "event": "llm_request_failed",
  "request_id": "req-123",
  "provider": "provider-a",
  "model": "model-x",
  "status_code": 429,
  "retry_count": 2
}
```

### Important security point

Do not blindly log:

- secrets/API keys
- authorization tokens
- sensitive document content
- unnecessary personal data
- complete prompts/responses when that creates privacy or security risk

Log identifiers and metadata where possible, and apply redaction/access controls to sensitive data.

---

# 3. Metrics

## Definition

Metrics are numeric measurements aggregated over time.

Examples:

```text
request_count
error_rate
p95_latency
queue_depth
cache_hit_rate
tokens_used
```

### Common metric types

#### Counter
Only increases.

```text
requests_total += 1
```

#### Gauge
Can increase or decrease.

```text
queue_depth = 42
```

#### Histogram
Tracks distributions such as latency.

```text
request latency
→ p50 / p95 / p99
```

For interviews, know the purpose of each rather than memorizing metric-library APIs.

---

# 4. Traces

## Definition

A trace represents one request/workflow as it travels through multiple components.

Mental model:

```text
Trace: req-123
│
├── API request       10ms
├── Query embedding   40ms
├── Vector search     30ms
├── Keyword search    25ms
├── RRF                2ms
├── Reranker          120ms
└── LLM              950ms
```

Each operation is a **span**.

So:

```text
Trace
  └── Spans
```

A trace answers:

> **Where did this particular request spend time or fail?**

---

# 5. Correlation IDs / Request IDs

A correlation ID connects logs and operations belonging to the same request or workflow.

```text
Incoming request
      ↓
request_id = req-123
      ↓
API log
      ↓
retrieval log
      ↓
reranker log
      ↓
LLM log
```

This allows an engineer to reconstruct the request path from distributed services.

### Trace ID vs request ID

They can be used similarly, but conceptually:

```text
Request ID
→ application-level identifier

Trace ID
→ distributed tracing identifier
```

In many systems they can be propagated together or mapped together.

---

# 6. Why tracing matters especially for RAG

An incorrect answer does not automatically mean the LLM is the problem.

A trace lets us inspect:

```text
Query
 ↓
Embedding
 ↓
Vector retrieval
 ↓
Keyword retrieval
 ↓
RRF
 ↓
Reranker
 ↓
Context construction
 ↓
LLM
```

This lets us separate:

```text
Retrieval failure
        vs
Generation failure
```

Example:

```text
Wrong answer
      ↓
Correct chunk never retrieved
      → retrieval problem

Correct chunk retrieved
      ↓
LLM still answers incorrectly
      → generation/context problem
```

This is one of the most important observability ideas for RAG.

---

# 7. AI-specific metrics

Traditional infrastructure metrics are necessary but not sufficient.

Track AI-specific signals such as:

```text
input tokens
output tokens
total tokens
cost/request
model selected
provider
TTFT
completion latency
retrieval candidate count
reranker latency
cache hit rate
fallback rate
```

For retrieval specifically:

```text
vector top-K
keyword top-K
candidate overlap
RRF ranking
reranker output
```

For quality/evaluation:

```text
Context Precision
Context Recall
Faithfulness
Answer Relevance
Answer Correctness
citation accuracy
```

---

# 8. Token and cost observability

A production AI platform should be able to answer:

> **How much did this request cost and why?**

A useful request-level record can include:

```text
provider
model
input tokens
output tokens
estimated cost
```

Then aggregate by:

```text
tenant
model
provider
endpoint
feature
team
```

This allows cost attribution and identifies expensive workloads.

---

# 9. Latency observability

Do not monitor only total request latency.

Break it down:

```text
Total latency
   =
embedding
+ vector search
+ keyword search
+ RRF
+ reranking
+ prompt construction
+ LLM TTFT
+ generation
```

Use percentiles:

```text
p50 → typical
p95 → slower tail
p99 → extreme tail
```

For user-facing AI systems, p95/p99 can reveal degradation that averages hide.

---

# 10. TTFT vs total latency

**TTFT = Time To First Token**.

```text
Request
 ↓
TTFT
 ↓
first visible token
 ↓
remaining generation
 ↓
complete response
```

Streaming can improve perceived responsiveness by lowering time-to-first-visible-output even if total generation time does not change much.

Therefore monitor both:

```text
TTFT
Total latency
```

---

# 11. Error observability

Track more than `500` errors.

Classify failures:

```text
client errors
rate limits
validation failures
timeouts
provider failures
database failures
tool failures
retrieval failures
```

Useful metrics:

```text
error rate
retry count
fallback count
provider-specific failure rate
```

A spike in `429` responses may indicate rate limiting rather than an application bug.

---

# 12. Cache observability

For a cache, track:

```text
hit rate
miss rate
latency
eviction rate
stale-hit rate (when relevant)
```

For semantic caching, also monitor:

```text
similarity threshold behavior
false-hit / bad reuse rate
freshness/invalidation issues
```

A high cache hit rate is not enough if cached answers are stale or incorrect.

---

# 13. Queue / worker observability

For asynchronous ingestion:

```text
queue depth
oldest job age
processing rate
failure rate
retry count
worker utilization
job duration
```

Mental model:

```text
Queue healthy?
   ↓
Are jobs arriving?
   ↓
Are workers processing them?
   ↓
Are failures/retries growing?
   ↓
Are jobs becoming stale?
```

---

# 14. AI quality observability

This is the difference between traditional observability and AI observability.

Infrastructure can be healthy while the AI system is performing badly.

Example:

```text
API latency     ✅
Database health ✅
LLM availability ✅

But:
retrieval quality ❌
hallucination rate ❌
citation accuracy ❌
```

Therefore production monitoring needs both:

```text
Operational health
        +
AI quality
```

---

# 15. LangSmith tracing

LangSmith is an observability/evaluation platform commonly used with LangChain/LangGraph applications.

Conceptually:

```text
Application / Agent
        ↓
LangChain / LangGraph execution
        ↓
Tracing
        ↓
LangSmith
```

A trace can represent a complex AI execution such as:

```text
Agent
 ↓
LLM
 ↓
Tool call
 ↓
Retriever
 ↓
Reranker
 ↓
LLM
 ↓
Final answer
```

This is useful for understanding agent/tool/RAG execution rather than only recording a final response.

### Interview positioning

Do not frame LangSmith as a replacement for all infrastructure observability.

Think:

```text
Cloud / OpenTelemetry / infra monitoring
→ infrastructure + distributed system health

LangSmith
→ LLM/agent traces, prompts, tool calls, runs, evaluations
```

They can complement each other.

---

# 16. OpenTelemetry mental model

For general distributed tracing, OpenTelemetry provides a vendor-neutral instrumentation model.

```text
Application
   ↓
OpenTelemetry instrumentation
   ↓
traces / metrics / logs
   ↓
collector/backend
```

For an AI system, the trace can span:

```text
API
 ↓
Embedding API
 ↓
Database
 ↓
Reranker
 ↓
LLM
```

The important interview concept is **vendor-neutral distributed telemetry** rather than memorizing SDK syntax.

---

# 17. What should we put into a trace?

A useful AI trace can include metadata such as:

```text
request_id
trace_id
tenant
endpoint
model/provider
latency
tokens
cost
retrieval count
selected chunks
reranker result
cache status
tool name
error/fallback
```

Be careful with actual content:

```text
Prompt / retrieved text / model output
→ capture only when policy allows it
→ redact sensitive information
→ apply retention/access controls
```

---

# 18. Debugging a slow RAG request

Use the trace rather than guessing.

```text
1. Find trace by request_id / trace_id
2. Inspect total latency
3. Identify slow span
4. Compare p95/p99 behavior
5. Inspect retries/cache misses
6. Inspect provider latency
7. Fix bottleneck
8. Re-measure
```

Example:

```text
API              15ms
Embedding        40ms
Vector search    30ms
Keyword search   25ms
RRF               2ms
Reranker         300ms  ← bottleneck
LLM              700ms
```

Don't optimize the 2ms RRF step because it is easy to change. Optimize the actual bottleneck.

---

# 19. Debugging a wrong answer

A useful diagnostic sequence is:

```text
Wrong answer
    ↓
Was correct evidence retrieved?
       /        \
     NO          YES
     ↓            ↓
retrieval       generation/context
problem         problem
```

### If not retrieved

Inspect:

```text
parser
chunking
embedding
vector search
keyword search
metadata filters
RRF
candidate depth
reranker
```

### If correctly retrieved

Inspect:

```text
context construction
prompt
context ordering
model behavior
structured output
```

This is far more useful than immediately switching LLM models.

---

# 20. SLO / SLA / SLI

These terms are worth knowing.

### SLI — Service Level Indicator

The measured signal.

```text
p95 latency = 1.8 sec
```

### SLO — Service Level Objective

The target.

```text
95% of requests < 2 sec
```

### SLA — Service Level Agreement

A contractual commitment, usually with consequences if targets are not met.

Mental model:

```text
SLI → measurement
SLO → target
SLA → contractual promise
```

For AI systems, an SLO might cover:

```text
availability
latency
error rate
```

Quality metrics may also be tracked as product/evaluation objectives.

---

# 21. Alerting

Do not alert on every log entry.

Alert when a metric crosses an actionable threshold or anomaly condition.

Examples:

```text
p95 latency > SLO
error rate > threshold
queue age > threshold
provider 429 spike
LLM fallback rate spikes
cache hit rate collapses
```

Good alerts should be:

```text
actionable
specific
low-noise
```

---

# 22. Dashboard design

A useful AI production dashboard can have sections:

```text
REQUEST HEALTH
- traffic
- success/error rate
- p95/p99 latency

AI PERFORMANCE
- TTFT
- generation latency
- tokens
- cost

RETRIEVAL
- retrieval latency
- candidate count
- reranker latency

CACHE
- hit/miss rate

PROVIDERS
- errors
- 429s
- fallback rate

QUALITY
- faithfulness
- answer correctness
- citation accuracy
```

---

# 23. Observability vs monitoring

These terms are related but not identical.

```text
Monitoring
→ watching known health signals

Observability
→ ability to investigate unexpected behavior
```

Monitoring might tell us:

```text
p95 latency = 4 seconds
```

Observability helps us answer:

```text
Why?
→ reranker latency increased
→ provider latency increased
→ retries increased
```

---

# 24. Project connection — AI Platform

Our architecture naturally exposes multiple observability boundaries:

```text
FastAPI
 ↓
Service
 ↓
Retrieval
 ├── embedding
 ├── vector search
 ├── keyword search
 ├── RRF
 └── reranker
 ↓
RAG / LLM
```

Useful request-level identifiers and metrics should flow through these boundaries.

At the RAG level, preserve enough information to inspect:

```text
query
retrieval candidates
RRF ranking
reranker output
selected context
model/provider
tokens
latency
citations
```

At the platform level, also monitor:

```text
queue depth
worker failures
database health
object storage failures
cache health
provider errors
```

---

# 25. One complete mental model

```text
                         USER REQUEST
                              ↓
                         request_id
                         trace_id
                              ↓
                            API
                              ↓
                    ┌───────────────────┐
                    │       TRACE       │
                    └───────────────────┘
                              ↓
                    Query / Embedding
                              ↓
             ┌────────────────┴────────────────┐
             ↓                                 ↓
       Vector Search                     Keyword Search
             └────────────────┬────────────────┘
                              ↓
                             RRF
                              ↓
                          Reranker
                              ↓
                        Context Build
                              ↓
                             LLM
                              ↓
                    Answer + Citations
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
      LOGS                 METRICS               TRACE
   what happened?       how much/often?      where/why?
        └─────────────────────┼─────────────────────┘
                              ↓
                       AI QUALITY/EVAL
                              ↓
              Faithfulness / Correctness / Relevance
```

---

# High-value interview questions

## What is observability?

> Observability is the ability to understand a system's internal behavior from its emitted telemetry. In an AI system, I combine logs, metrics and distributed traces with AI-specific signals such as token usage, retrieval behavior, model selection and quality metrics.

## Logs vs metrics vs traces?

> Logs provide detailed event information, metrics provide aggregated numeric signals over time, and traces show the path of an individual request across components.

## What is a span?

> A span represents one operation within a distributed trace, such as vector search, reranking or an LLM call.

## How do you debug a slow RAG request?

> I would locate the request trace, break down latency by span, identify the bottleneck, inspect retries/cache misses/provider latency, fix the dominant component and re-measure p95/p99 latency.

## How do you debug a wrong RAG answer?

> First check whether the correct evidence was retrieved. If not, investigate parsing, chunking and retrieval. If the correct evidence was retrieved, investigate context construction, prompting and model behavior. I would not immediately blame the LLM.

## What AI-specific metrics would you monitor?

> Tokens, cost, TTFT, generation latency, model/provider, retrieval candidate counts, reranker latency, cache hit rate, fallback rate and evaluation signals such as faithfulness, relevance, correctness and citation accuracy.

## What is LangSmith used for?

> LangSmith provides tracing, debugging and evaluation capabilities for LLM, agent and retrieval workflows, making it useful for inspecting model calls, tool calls and multi-step AI execution. It complements rather than necessarily replaces infrastructure observability.

## What is OpenTelemetry?

> A vendor-neutral observability framework for instrumenting and exporting telemetry such as traces, metrics and logs across distributed systems.

## How do you prevent sensitive data from leaking into logs/traces?

> Treat prompts, documents and model outputs as potentially sensitive. Redact or avoid capturing unnecessary content, control access and retention, and follow the application's data-governance requirements.

## What is SLI vs SLO vs SLA?

> SLI is the measured indicator, SLO is the target for that indicator, and SLA is the contractual commitment to a customer.

---

# Interview summary

Remember this:

```text
LOGS
→ detailed events

METRICS
→ aggregate health

TRACES
→ request journey

AI METRICS
→ model/retrieval/cost behavior

AI EVALUATION
→ quality
```

And the Lead-level debugging principle:

> **Don't guess which component is broken. Instrument the pipeline, locate the failing or expensive stage, change one thing, and verify the result with both operational and quality metrics.**

## Checklist

- [x] observability definition
- [x] logs
- [x] structured logging
- [x] metrics
- [x] counters / gauges / histograms
- [x] traces / spans
- [x] correlation IDs / request IDs
- [x] trace IDs
- [x] AI-specific metrics
- [x] token/cost tracking
- [x] latency / p95 / p99
- [x] TTFT
- [x] error classification
- [x] cache metrics
- [x] queue/worker metrics
- [x] AI quality metrics
- [x] LangSmith tracing
- [x] OpenTelemetry concept
- [x] sensitive-data handling
- [x] debugging slow RAG
- [x] debugging wrong answers
- [x] SLI / SLO / SLA
- [x] alerting
- [x] dashboards
- [x] monitoring vs observability
- [x] project connection
