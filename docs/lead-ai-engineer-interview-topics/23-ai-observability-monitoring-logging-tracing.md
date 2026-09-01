# Topic 23 — AI Observability, Monitoring, Logging & Tracing

**Status:** Complete

## Focus
Logs, metrics, traces, correlation IDs, latency, throughput, errors, token usage, cost, retrieval quality, cache hit rate and AI-specific quality signals.

## 1. Observability vs Monitoring

> **Monitoring tells us whether the system is healthy through predefined signals; observability gives us enough telemetry to understand why a system behaved the way it did.**

Simple mental model:

```text
Logs    → what happened?
Metrics → how much / how often?
Traces  → where did it happen?
AI eval → was the result actually good?
```

## 2. Logs

Logs record discrete events.

Useful fields:

```text
request_id
trace_id
tenant_id
service
operation
model/provider
error
latency
status
```

Use structured logs rather than large unstructured strings so they are searchable and aggregatable.

Do not log secrets, tokens, sensitive document content or unnecessary PII.

## 3. Metrics

Metrics are numeric time-series signals used for dashboards, alerting and capacity analysis.

Core service metrics:

```text
request rate
error rate
p50/p95/p99 latency
throughput
queue depth
CPU/memory
```

AI-specific metrics:

```text
token usage
model latency
TTFT
LLM error rate
provider fallback rate
retrieval latency
reranker latency
cache hit rate
```

## 4. Traces

A trace follows one request across multiple components. A trace contains spans representing individual operations.

Example:

```text
Trace
 ├── API request
 ├── Query embedding
 ├── Vector search
 ├── Keyword search
 ├── RRF
 ├── Reranker
 └── LLM generation
```

This is particularly useful for finding which stage caused latency or failure.

## 5. Correlation IDs

A correlation/request ID allows logs and downstream operations to be connected to one logical request.

```text
HTTP request
   ↓ request_id / trace_id
Service
   ↓
Retriever
   ↓
Reranker
   ↓
LLM
```

The same identifier should be propagated across relevant service boundaries where practical.

## 6. Why tracing matters in RAG

A bad answer does not automatically mean the LLM is the problem.

Trace:

```text
Query
 ↓
Parsing / query transformation
 ↓
Embedding
 ↓
Vector results
 ↓
Keyword results
 ↓
RRF
 ↓
Reranker
 ↓
Final context
 ↓
LLM
 ↓
Answer
```

This lets us identify where quality or latency degraded.

## 7. RAG observability

Useful retrieval telemetry includes:

```text
retriever type
candidate count
vector top-K
keyword top-K
candidate overlap
RRF ordering
reranker latency
final top-K
source/chunk IDs
```

Avoid logging full sensitive document text by default.

## 8. LLM observability

Track:

```text
model/provider
input tokens
output tokens
estimated cost
TTFT
total generation latency
finish/error status
retry count
fallback provider
```

This supports cost analysis, capacity planning and model comparison.

## 9. LangChain callbacks

LangChain components expose execution lifecycle hooks that can be used for observability and instrumentation.

Conceptually:

```text
Runnable / Model / Tool
       ↓
callbacks / handlers
       ↓
logs / metrics / traces
```

Callbacks are useful for observing events without embedding logging code into every model/tool implementation.

## 10. LangChain tracing

For a composed pipeline or agent:

```text
Agent
 ↓
Model
 ↓
Tool
 ↓
Retriever
 ↓
Model
```

tracing can capture nested execution so a single request can be inspected end-to-end.

This is particularly valuable for debugging agent loops because the developer can see the sequence of model calls and tool calls instead of only the final answer.

## 11. LangSmith

> **LangSmith is an observability, tracing and evaluation platform from the LangChain ecosystem for inspecting LLM/agent application runs and evaluating their behavior.**

Mental model:

```text
AI application
      ↓
LangChain / LangGraph / SDK
      ↓
Tracing instrumentation
      ↓
LangSmith
      ↓
Runs / traces / datasets / evaluations
```

LangSmith can be used beyond the exact same framework codebase; the core value is application observability and evaluation rather than being the LLM itself.

## 12. What does a LangSmith trace help answer?

For an agent request:

```text
Why was this tool selected?
Which tools were called?
What arguments were produced?
How long did each step take?
How many model calls happened?
How many tokens were used?
Where did the workflow fail?
```

For RAG:

```text
Which chunks were retrieved?
What was the final context?
Which model generated the answer?
How much latency/cost came from each stage?
```

## 13. Evaluation vs Observability

These are related but different.

```text
Observability
→ understand what the system did

Evaluation
→ determine how good the result was
```

Example:

```text
Trace says:
Retriever returned 20 chunks

Evaluation says:
Only 3 were actually relevant
```

Production AI systems need both.

## 14. OpenTelemetry

OpenTelemetry is a vendor-neutral observability standard/ecosystem for traces, metrics and logs.

Mental model:

```text
Application
 ↓
OpenTelemetry instrumentation
 ↓
Telemetry backend
```

This can be useful when an organization already has a centralized observability stack and does not want AI telemetry isolated from the rest of the platform.

## 15. Alerts

Alert on symptoms and actionable thresholds rather than every minor fluctuation.

Examples:

```text
p99 latency > threshold
error rate > threshold
queue depth growing continuously
provider 5xx spike
LLM cost anomaly
fallback rate spike
```

AI systems may also use quality-related alerting where reliable online signals exist.

## 16. SLI / SLO / SLA

### SLI
A measured indicator.

Example:

```text
p95 chat latency
```

### SLO
The target for that indicator.

```text
99% of chat requests under X seconds
```

### SLA
A contractual commitment to customers, often with consequences if the commitment is missed.

Mental model:

```text
SLI → measurement
SLO → engineering target
SLA → contractual commitment
```

## 17. AI-specific quality monitoring

Operational health is not the same as AI quality.

A system can be:

```text
HTTP 200 ✅
Latency ✅
CPU ✅
```

while still producing a bad answer.

Track quality signals such as:

```text
retrieval relevance
context precision/recall
faithfulness
aer? answer correctness
citation accuracy
user feedback
```

Do not rely on one metric to represent overall AI quality.

## 18. Debugging workflow

A good production debugging sequence:

```text
1. Find request/trace ID
2. Inspect service latency/errors
3. Inspect retrieval results
4. Inspect fusion/reranking
5. Inspect final context
6. Inspect model request/response metadata
7. Determine whether failure is retrieval, orchestration or generation
8. Fix bottleneck/root cause
9. Re-evaluate quality and latency
```

## 19. Security of telemetry

Observability systems themselves are sensitive.

Protect:

```text
API keys
access tokens
customer documents
PII
prompts containing secrets
tool arguments with sensitive values
```

Use redaction, access controls, retention policies and least-privilege access.

## 20. Interview questions

### What is observability?

> The ability to understand a system's internal behavior from its emitted telemetry, primarily logs, metrics and traces.

### Logs vs metrics vs traces?

> Logs capture discrete events, metrics provide aggregated numerical signals, and traces follow an individual request across components through spans.

### Why use correlation IDs?

> To connect logs and downstream operations belonging to the same logical request so failures and latency can be traced end-to-end.

### Why is tracing useful for RAG?

> It lets us identify whether an issue originated in retrieval, fusion, reranking, context construction, or model generation instead of treating the final answer as the only observable output.

### What are LangChain callbacks?

> Lifecycle hooks/handlers that allow execution events from models, tools and other components to be observed or instrumented.

### What is LangSmith?

> An observability and evaluation platform for tracing LLM/agent application runs, inspecting execution steps, collecting datasets and evaluating application behavior.

### LangSmith vs LangChain?

> LangChain is the application framework/ecosystem for LLM applications; LangSmith is the observability/evaluation platform used to inspect and evaluate those applications.

### LangSmith vs OpenTelemetry?

> LangSmith is specialized for LLM/agent application tracing and evaluation, while OpenTelemetry is a vendor-neutral telemetry standard/ecosystem for general application observability. They can coexist.

### What would you monitor in a RAG system?

> Retrieval latency and candidate quality, reranker latency, final context size, LLM latency/TTFT, token usage, cost, errors, cache hit rate and AI-quality metrics such as faithfulness and retrieval relevance.

### How do you debug a bad AI answer?

> Start with the trace and determine whether the correct evidence was retrieved. Then inspect filtering, fusion, reranking and context before deciding whether the model-generation stage is responsible.

## Mental model

```text
                         REQUEST
                            ↓
                     Trace / request ID
                            ↓
     ┌──────────────────────┼──────────────────────┐
     ↓                      ↓                      ↓
   Logs                  Metrics                 Trace
     │                      │                      │
what happened?        how much/how often?    where did it happen?
                            │                      │
                            └──────────┬───────────┘
                                       ↓
                              AI-specific signals
                                       ↓
                         Retrieval / LLM / cost / quality
                                       ↓
                              LangSmith / OTel
```

## Checklist

- [x] observability vs monitoring
- [x] structured logs
- [x] metrics
- [x] traces and spans
- [x] correlation IDs
- [x] RAG tracing
- [x] LLM/token/cost telemetry
- [x] LangChain callbacks
- [x] LangSmith tracing
- [x] observability vs evaluation
- [x] OpenTelemetry
- [x] alerting
- [x] SLI/SLO/SLA
- [x] AI-quality monitoring
- [x] debugging workflow
- [x] telemetry security
