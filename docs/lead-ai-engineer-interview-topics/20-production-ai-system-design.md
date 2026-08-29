# Topic 20 — Production AI System Design & Scalability

**Status:** Complete

## Focus
Requirements, component boundaries, API gateways, orchestration, storage, queues, horizontal scaling, caching, multi-region considerations and capacity planning.

## Interview outcomes
Design a production GenAI platform from requirements through deployment and explain trade-offs.

## 1. Start with requirements

Don't start by naming technologies. Clarify functional and non-functional requirements.

### Functional

```text
upload documents
search documents
ask questions
return citations
support multiple tenants
```

### Non-functional

```text
scale
latency
availability
security
cost
data residency
```

## 2. High-level production RAG architecture

```text
                         Clients
                            │
                            ▼
                     API Gateway / LB
                            │
                            ▼
                       FastAPI API
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
        Document APIs                 Chat / RAG
              │                           │
              ▼                           ▼
       Ingestion Service           Retrieval Service
              │                           │
              ▼                           ▼
          Job Queue                 Vector + Keyword
              │                           │
              ▼                           ▼
          Workers                         RRF
              │                           │
       ┌──────┴──────┐                    ▼
       ▼             ▼                 Reranker
     Parser        Chunker                │
       │             │                    ▼
       └──────┬──────┘                Context
              │                           │
              ▼                           ▼
          Embeddings                    LLM
              │                           │
              ▼                           ▼
      PostgreSQL/pgvector            Response
```

## 3. Synchronous vs asynchronous work

User-facing chat/query paths are usually synchronous from the client's perspective:

```text
query → retrieval → reranking → LLM → response
```

Document ingestion is a strong candidate for asynchronous processing because parsing, OCR, chunking, embedding and indexing can be long-running.

```text
Upload
  ↓
store document
  ↓
create job
  ↓
return job_id
  ↓
worker processes asynchronously
```

## 4. Queue-based ingestion

```text
API
 ↓
Queue
 ↓
Worker
 ↓
Parser
 ↓
Chunker
 ↓
Embedding
 ↓
Index
```

A queue provides:

- decoupling
- buffering
- retries
- horizontal worker scaling
- backpressure

## 5. Backpressure

If incoming work exceeds processing capacity:

```text
incoming jobs = 1000/sec
worker capacity = 200/sec
```

A queue buffers work rather than allowing unbounded execution and memory growth.

## 6. Horizontal scaling

Keep API servers stateless where practical so they can scale behind a load balancer:

```text
             Load Balancer
             /     |     \
         API-1   API-2   API-3
```

Stateless application instances make traffic distribution and replacement easier.

## 7. Shared state

Do not rely on local process memory for durable application state when horizontally scaling.

```text
API servers
     ↓
Redis / database / durable store
```

This applies to conversation state, job state and other data that must survive instance changes.

## 8. Storage architecture

### Object storage

Store large raw documents in object storage when appropriate.

### PostgreSQL

Store metadata and relational entities such as:

```text
documents
users
tenants
permissions
jobs
metadata
```

### pgvector

Store or index embeddings alongside PostgreSQL data when this architecture fits the workload.

## 9. Caching

Possible cache layers include:

```text
query embeddings
retrieval results
semantic cache
LLM responses
configuration
```

Each cache needs a suitable freshness/invalidation strategy.

## 10. Multi-tenancy

Relevant data and retrieval should respect tenant and permission boundaries:

```text
query
 ↓
tenant / authorization constraints
 ↓
retrieval
 ↓
RRF / reranking
```

Do not treat authorization as a post-processing step after exposing unauthorized candidates to the application.

## 11. Idempotency

Ingestion jobs can be retried or duplicated.

Use deterministic identifiers, versioning and idempotent writes so retries do not produce duplicate logical data.

Example:

```text
same document version
+
same chunk
→ same deterministic chunk ID
```

## 12. Rate limits and provider capacity

External providers may impose limits on:

```text
requests/sec
tokens/minute
concurrency
```

Production systems should use bounded concurrency, queues, rate limiting and controlled retries rather than creating retry storms.

## 13. Capacity planning

For a given target load, estimate:

```text
API instances
DB capacity
vector-search capacity
queue throughput
worker count
LLM provider limits
embedding throughput
Redis capacity
```

Scale the actual bottleneck rather than automatically scaling every component.

## 14. Bottleneck analysis

Example:

```text
API           = 20 ms
Vector DB     = 30 ms
Reranker      = 250 ms
LLM           = 1000 ms
```

The LLM and reranker dominate the critical path, so optimizing a 20 ms API layer is unlikely to materially improve end-to-end latency.

## 15. Resilience boundaries

Assume components can fail:

```text
LLM provider
Vector DB
Queue
Embedding API
Object storage
```

Define explicit behavior for each failure rather than allowing one dependency failure to bring down the whole platform.

Examples include bounded retries, timeouts and compatible fallbacks.

Detailed resilience patterns are covered in Topic 21.

## 16. Observability

### Logs

Capture useful request-level context such as:

```text
request_id
tenant_id
model
errors
latency
```

### Metrics

Track aggregate signals such as:

```text
request rate
error rate
p95/p99 latency
cache hit rate
retrieval latency
reranker latency
LLM latency
token usage
```

### Traces

Follow an individual request across the pipeline:

```text
API
 ↓
Embedding
 ↓
Vector Search
 ↓
Keyword Search
 ↓
RRF
 ↓
Reranker
 ↓
LLM
```

AI-specific observability should also expose retrieval/ranking data and token/model information where appropriate.

## 17. Multi-region

Multi-region can help with:

- availability
- lower latency
- disaster recovery
- data residency requirements

But it adds complexity around replication, consistency, routing and failover.

Use it when the requirements justify that complexity.

## 18. Project connection

Our `ai-platform` architecture provides concrete examples of the separation described above:

```text
FastAPI
 ↓
Services
 ↓
Repositories / Providers
 ↓
PostgreSQL + pgvector / object storage / external AI services
```

The document-ingestion path is naturally suited to asynchronous worker processing, while query/RAG processing is latency-sensitive. Provider abstractions such as `StorageProvider`, `EmbeddingProvider` and `Reranker` help keep application logic independent of infrastructure implementations.

## 19. Interview approach for system design

When asked to design a production AI system:

```text
1. Clarify requirements
2. Define scale
3. Draw high-level architecture
4. Separate sync vs async paths
5. Define data flow
6. Define storage
7. Define retrieval
8. Discuss caching
9. Discuss scaling
10. Discuss failures
11. Discuss security
12. Discuss observability
13. Discuss cost
```

## High-value interview questions

### How would you design a scalable RAG system?

> Start with requirements and scale, then separate the API/query path from asynchronous ingestion. Use queues/workers for long-running ingestion, stateless API instances behind a load balancer, appropriate storage for raw files and metadata/vectors, retrieval plus reranking for queries, and add caching, authorization, resilience and observability around the critical dependencies.

### Why use a message queue for ingestion?

> It decouples request handling from long-running work, provides buffering and backpressure, enables worker scaling and gives us a place to implement retries and failure handling.

### How would you handle 10,000 document uploads?

> Store the documents, create ingestion jobs and process them with horizontally scalable workers. Control concurrency, use provider-aware rate limits, make processing idempotent and track job status separately from the upload request.

### How do you horizontally scale FastAPI?

> Keep the application tier stateless and run multiple instances behind a load balancer. Shared state belongs in external durable systems such as databases or caches rather than local process memory.

### How do you make document ingestion idempotent?

> Use deterministic document/chunk identifiers, versioning and idempotent database/index writes so retrying the same logical job doesn't create duplicate data.

### How would you debug a slow RAG request?

> Trace the request across query embedding, vector and keyword retrieval, RRF, reranking and LLM generation, then identify which stage dominates latency and optimize that bottleneck. I would also inspect cache hit rate and provider/network latency.

### What would you monitor in production?

> Availability, error rate, p95/p99 latency, queue depth, retrieval/reranker/LLM latency, token usage, cache hit rate, provider failures and AI-specific signals such as retrieved candidates and model selection.

### When would you use multi-region?

> When availability, latency, disaster recovery or data residency requirements justify the added operational complexity.

## Checklist

- [x] requirements-first system design
- [x] high-level architecture
- [x] synchronous vs asynchronous paths
- [x] queues and workers
- [x] backpressure
- [x] horizontal scaling
- [x] stateless services
- [x] object storage + relational/vector storage
- [x] caching
- [x] multi-tenancy
- [x] idempotency
- [x] rate limits
- [x] capacity planning
- [x] bottleneck analysis
- [x] resilience boundaries
- [x] observability
- [x] multi-region trade-offs
- [x] project-based explanation
