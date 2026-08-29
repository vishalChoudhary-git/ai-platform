# Topic 19 — LLM / Model Serving Architecture & Model Routing

**Status:** Complete

## Focus
Model serving layers, provider abstraction, model routing, workload-based model selection, fallback providers, quotas, concurrency, batching and inference APIs.

## Interview outcomes
Design a model-serving layer that balances quality, latency, cost and resilience.

## 1. What is model serving?

> Model serving is the infrastructure that makes a machine-learning or LLM model available to applications through an API or other inference interface.

Hosted model:

```text
Application
   ↓
Model Provider API
   ↓
Model inference
   ↓
Response
```

Self-hosted model:

```text
Application
   ↓
Inference API / Server
   ↓
GPU infrastructure
   ↓
Model
   ↓
Response
```

## 2. Hosted vs self-hosted

### Hosted
Examples include OpenAI, Azure-hosted models and other managed providers.

**Advantages:**
- no GPU infrastructure to operate
- easier scaling
- faster model adoption
- less operational overhead

**Trade-offs:**
- provider dependency
- API cost and rate limits
- network latency
- privacy/data-governance considerations

### Self-hosted

**Advantages:**
- more infrastructure/model control
- can satisfy specific privacy or customization requirements
- potentially better economics at sufficient scale

**Trade-offs:**
- GPU cost
- deployment and scaling complexity
- model loading/cold starts
- infrastructure monitoring and maintenance

## 3. Model Gateway

A model gateway provides a common internal interface between application services and model providers.

```text
Application
     ↓
Model Gateway
     ↓
Provider adapters
 ┌──────┼──────┐
OpenAI Azure  Other
```

A gateway can centralize:

- authentication
- quotas/rate limits
- provider abstraction
- routing
- logging/tracing
- policy enforcement

## 4. Model routing

> Model routing decides which model/provider should handle a particular workload.

Example:

```text
Simple extraction
    ↓
Small / cheaper model

Complex reasoning
    ↓
Stronger model
```

Routing can consider:

- task type
- quality requirement
- latency requirement
- cost budget
- context-length requirement
- tool/structured-output support
- provider availability
- tenant policies
- rate limits

## 5. Gateway vs Router

**Gateway:** common interface and policy boundary.

**Router:** decision logic for selecting a model/provider.

A router can be implemented inside the gateway.

```text
Application
    ↓
Gateway
    ↓
Router
    ↓
Model / Provider
```

## 6. Provider abstraction

The same abstraction pattern used elsewhere in the platform can be applied to LLMs:

```text
LLMProvider
   ├── OpenAIProvider
   ├── AzureOpenAIProvider
   └── OtherProvider
```

The application depends on the interface rather than a provider-specific SDK.

This is the same architectural principle as:

```text
StorageProvider
EmbeddingProvider
Reranker
BaseParser
```

## 7. Model routing in a RAG platform

A RAG platform typically has different model workloads:

```text
Query
 ↓
Embedding model
 ↓
Retrieval
 ↓
Reranker model
 ↓
Generation LLM
```

These should not automatically use the same model. Each workload can have its own provider/model choice.

## 8. Retry vs fallback

### Retry

Retry the same provider/model after a transient failure.

```text
Model A
 ↓
temporary failure
 ↓
retry Model A
```

### Fallback

Switch to another compatible provider/model.

```text
Model A
 ↓
failure
 ↓
Model B
```

A fallback must be compatible enough in capability, context length and output contract. Silent degradation is not always acceptable.

## 9. Quotas and rate limits

Providers may limit:

- requests per second
- tokens per minute
- concurrent requests

A serving layer can enforce limits before requests reach the provider.

```text
Incoming requests
      ↓
Rate / concurrency limiter
      ↓
Provider
```

This prevents uncontrolled request bursts and retry storms.

## 10. Concurrency control

Unlimited concurrent model requests can cause provider throttling or, for self-hosted models, GPU memory/compute pressure.

Use bounded concurrency, queues or admission control.

```text
Requests
   ↓
Concurrency limiter
   ↓
Controlled model calls
```

## 11. Batching

Batching groups compatible inference work to improve throughput and reduce per-request overhead.

Useful for:

- embeddings
- offline inference
- document ingestion
- classification

Interactive generation may prioritize latency over large batches.

## 12. Latency vs throughput

**Latency:** how long one request takes.

**Throughput:** how many requests/items can be processed over time.

Batching may improve throughput while increasing waiting time or individual latency depending on the serving design.

## 13. Self-hosted model serving

Conceptually:

```text
                 Load Balancer
                /      |      \
               /       |       \
          GPU Node  GPU Node  GPU Node
              ↓          ↓         ↓
         Inference  Inference  Inference
           Server      Server     Server
              \          |         /
               \         |        /
                    Model
```

Important operational concerns:

- GPU memory
- GPU utilization
- queue depth
- tokens/sec
- concurrency
- model loading
- autoscaling
- health checks

## 14. Model versioning and rollout

For a new model version, don't necessarily switch all traffic immediately.

```text
95% → v1
5%  → v2
```

Monitor quality and operational metrics before increasing traffic.

This leads into canary deployment and rollback concepts.

## 15. AI-specific observability

Track at least:

```text
requested model
selected model
provider
latency
TTFT
input/output tokens
cost
errors
retry count
fallback usage
```

For self-hosted models also consider:

```text
GPU utilization
GPU memory
queue depth
tokens/sec
```

## 16. Model selection is an engineering trade-off

Do not simply choose the largest model.

Consider:

```text
quality
latency
cost
reliability
context requirements
privacy
throughput
```

Use the cheapest/fastest model that satisfies the required quality for that workload.

## 17. Project connection

Our existing platform uses provider abstractions such as `EmbeddingProvider`, `Reranker` and `StorageProvider`. The same pattern can be extended to LLM providers so application services are not tightly coupled to a specific model vendor.

A future model layer could look like:

```text
Application
    ↓
LLMProvider / Gateway
    ↓
Model Router
    ↓
Provider + Model
```

We should distinguish this architectural design from claiming that a full multi-provider model gateway is already production code in the current project.

## Likely interview questions

### What is model serving?

> The infrastructure that exposes a model for inference to applications through an API or serving interface.

### Hosted vs self-hosted models?

> Hosted models reduce infrastructure operations and simplify scaling, while self-hosting gives more control but adds GPU, deployment and scaling complexity. I would choose based on quality, cost at expected scale, latency, privacy, customization and operational requirements.

### What is model routing?

> Selecting a model/provider based on workload characteristics such as task type, quality, latency, cost and availability.

### Gateway vs router?

> The gateway provides a common interface and policy boundary; the router makes the model/provider selection decision.

### How would you handle provider failure?

> Use bounded retries for transient failures and a compatible fallback provider/model when appropriate, with monitoring of fallback frequency and output quality.

### How do you prevent one tenant from exhausting model capacity?

> Tenant quotas, rate limits, concurrency limits, priority queues and budget controls.

### Latency vs throughput?

> Latency measures time per request; throughput measures the volume of work processed over time.

### How would you deploy a new model safely?

> Canary a small percentage of traffic, monitor quality and operational metrics, then progressively increase traffic or roll back.

### How would you choose between two models?

> Benchmark them on representative workloads and compare quality, latency, cost, reliability and required capabilities rather than choosing solely by model size.

## Checklist

- [x] model serving
- [x] hosted vs self-hosted
- [x] model gateway
- [x] model router
- [x] provider abstraction
- [x] workload-based routing
- [x] retry vs fallback
- [x] quotas and rate limits
- [x] concurrency
- [x] batching
- [x] latency vs throughput
- [x] self-hosted inference concepts
- [x] model versioning/canary
- [x] observability
- [x] project connection
