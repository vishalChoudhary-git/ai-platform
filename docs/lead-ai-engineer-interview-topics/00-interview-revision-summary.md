# Lead AI Engineer Interview — Revision Summary

**Purpose:** Fast revision of the concepts covered across the interview-preparation topics. Each topic is reduced to a definition, one mental model, and the highest-value interview distinctions.

> Use the full topic files for deeper explanations and question banks. This file is the quick-revision layer.

---

## Topic 1 — Production Python

**Definition:** Production Python means using Python fundamentals with clear typing, error handling, async I/O, abstractions, dependency injection and testable architecture.

**Mental model:**
```text
Input → validation → service/business logic → repository/provider → result
```

**Remember:** `enumerate()` for rank/index, `lambda` for small callbacks, type hints communicate intent, and async is mainly for I/O-bound work.

---

## Topic 2 — Async / Await & HTTP Clients

**Definition:** Async programming allows an application to make progress on other work while waiting for I/O operations such as HTTP, DB, vector-store, embedding or LLM calls.

**Mental model:**
```text
async def → await I/O → event loop can run other work
```

**Remember:** `asyncio.gather()` for independent concurrent operations; use timeouts, bounded retries/backoff, rate/concurrency limits, connection reuse and cancellation handling.

---

## Topic 3 — Pydantic, Validation & Type Safety

**Definition:** Pydantic parses and validates runtime data into typed Python models.

**Mental model:**
```text
Raw / untrusted input → Pydantic → validated model → service
```

**Remember:** type hints ≠ runtime validation; `Field()` for declarative constraints/metadata; `field_validator` for custom field rules; model-level validation for cross-field rules. Validation does not replace authorization or business rules.

---

## Topic 4 — Repository, ABC & Dependency Injection

**Definition:** ABC defines a contract, dependency injection supplies implementations, repositories abstract persistence, and services own application/business orchestration.

**Mental model:**
```text
Service
 ├── Repository
 ├── Provider
 └── Strategy
```

**Remember:** dependency inversion lowers coupling and improves testability; do not put business decisions in repositories.

---

## Topic 5 — Strategy / Plugin & Extensible Architecture

**Definition:** Strategy encapsulates interchangeable behavior behind a common contract; factories/registries centralize creation or selection.

**Mental model:**
```text
Contract
   ↓
Implementation A | Implementation B | Implementation C
```

**Remember:** Strategy = interchangeable behavior; Factory = object creation/selection; Open/Closed = extend without rewriting the core workflow.

---

## Topic 6 — Python Data Structures, Comprehensions & Sorting

**Definition:** Core Python data structures and collection operations used to transform, rank and aggregate data cleanly.

**Mental model:**
```text
collect → filter → transform → sort → rank
```

**Remember:** list membership is typically O(n); set/dict membership is typically O(1) average; sorting is O(n log n); `sorted()` returns a new list, `.sort()` mutates the list.

---

## Topic 7 — Python OOP, Decorators, Generators & Context Managers

**Definition:** OOP organizes behavior around objects; decorators wrap behavior; context managers manage setup/cleanup; generators produce values lazily.

**Mental model:**
```text
Class → object
Decorator → wrap behavior
Context manager → enter → work → cleanup
Generator → yield values lazily
```

**Remember:** composition = HAS-A, inheritance = IS-A; `@decorator` is equivalent to assigning `func = decorator(func)`; `functools.wraps` preserves metadata; async context managers use `__aenter__`/`__aexit__`.

---

## Topic 8 — FastAPI, APIs, Validation, Middleware & Errors

**Definition:** FastAPI provides the HTTP/API layer for request routing, validation, dependency injection, middleware, responses and error handling.

**Mental model:**
```text
HTTP → Router → Validation/DI → Service → Repository/Provider → Response
```

**Remember:** path = resource identity; query = filtering/options; body = structured payload; authentication = who are you; authorization = what are you allowed to do. Long-running work belongs in durable queues/workers rather than only in-process background tasks.

---

## Topic 9 — LLM Fundamentals

**Definition:** An LLM is a trained model that generates output by predicting tokens based on input context.

**Mental model:**
```text
Prompt/context → tokenizer → model inference → generated tokens
```

**Remember:** tokens affect cost/latency/context limits; temperature changes sampling variability; top-p limits probability mass; a large context window does not mean all context should be supplied.

---

## Topic 10 — Embeddings & Vector Search

**Definition:** An embedding is a numerical representation of content that captures semantic relationships in a vector space.

**Mental model:**
```text
Text → embedding model → vector → similarity search
```

**Remember:** embed meaningful document chunks and the complete query; vector dimension is the number of values; normalization makes vector direction comparable; cosine and dot product are equivalent for ranking when vectors are unit-normalized.

---

## Topic 11 — RAG Architecture

**Definition:** RAG retrieves external knowledge and supplies it as context to an LLM so generation can be grounded in retrieved information.

**Mental model:**
```text
Ingestion: Parse → Chunk → Embed → Store
Query: Query → Retrieve → Fuse → Rerank → Context → LLM → Answer
```

**Remember:** separate ingestion-time from query-time work; preserve provenance; retrieval quality and generation quality should be evaluated separately.

---

## Topic 12 — Chunking & Document Intelligence

**Definition:** Chunking divides a parsed document into retrieval-oriented units while preserving useful structure and metadata.

**Mental model:**
```text
Document → Parse/normalize → structure-aware chunking → embeddings
```

**Remember:** fixed, semantic, structure-aware and table-aware strategies serve different documents; overlap is an independent parameter; chunking is a retrieval optimization problem, not just `text.split()`.

---

## Topic 13 — Hybrid Search

**Definition:** Hybrid search combines complementary semantic/vector and lexical/keyword retrieval signals.

**Mental model:**
```text
                 Query
                /     \
        Vector search  Keyword/BM25
                \       /
                   RRF
                    ↓
                Candidates
```

**Remember:** vector retrieval handles semantic similarity; keyword retrieval is strong for exact identifiers, codes, names, numbers and rare terms. Parallelize independent searches when possible.

---

## Topic 14 — Reranking

**Definition:** Reranking applies a more precise relevance model to a much smaller candidate set returned by first-stage retrieval.

**Mental model:**
```text
Large corpus → fast retrieval → 20–100 candidates → reranker → final Top-K
```

**Remember:** bi-encoder = efficient first-stage retrieval; cross-encoder/reranker = deeper query-document interaction but more expensive. Larger candidate pools can improve recall while increasing latency/cost.

---

## Topic 15 — RRF

**Definition:** Reciprocal Rank Fusion combines multiple ranked result lists using rank position instead of directly adding raw scores.

**Mental model:**
```text
Vector ranked list + Keyword ranked list → RRF → combined ranking
```

**Formula:** `RRF(d) = Σ 1 / (k + rank(d))`

**Remember:** RRF solves score-scale incompatibility; it does not understand semantics or replace retrieval/reranking.

---

## Topic 16 — Grounding, Hallucination & Citations

**Definition:** Grounding means generated claims are supported by trusted supplied evidence; hallucination is unsupported or incorrect generation.

**Mental model:**
```text
Authorized evidence → context → LLM → grounded answer → trusted citation metadata
```

**Remember:** RAG reduces hallucination but does not eliminate it; faithfulness ≠ correctness; abstain when evidence is insufficient; citations should come from trusted provenance rather than invented source references.

---

## Topic 17 — Repository status

**Status:** No corresponding topic file was found in the repository during review.

**Mental model:**
```text
Missing file → do not invent historical notes → define/update topic explicitly later
```

**Remember:** The master summary records this gap rather than fabricating content.

---

## Topic 18 — LLM Cost & Latency Optimization

**Definition:** Optimize AI systems across quality, latency and cost by measuring first, identifying bottlenecks, changing the right layer and re-measuring.

**Mental model:**
```text
Measure → identify bottleneck → optimize → re-measure → verify quality
```

**Remember:** parallelize independent I/O; reduce tokens/context; use caching carefully; choose the cheapest model that meets quality; streaming improves perceived latency and TTFT, not necessarily total computation.

---

## Topic 19 — Model Serving & Routing

**Definition:** Model serving exposes models for inference; model routing selects the appropriate model/provider for a workload.

**Mental model:**
```text
Application → Gateway → Router → Provider/Model → Response
```

**Remember:** gateway ≠ router; retry = same provider/model; fallback = compatible alternative; use quotas, rate limits, bounded concurrency and canary rollouts.

---

## Topic 20 — Production AI System Design

**Definition:** Designing a production AI system means connecting functional requirements with scale, latency, availability, security, storage, resilience and observability.

**Mental model:**
```text
Clients → API → services
                 ├→ async ingestion queue/workers
                 └→ query/retrieval → reranking → LLM
```

**Remember:** start with requirements, separate synchronous query from asynchronous ingestion, use stateless API instances, durable shared state, backpressure, idempotency and observability.

---

## Topic 21 — Resilience

**Status:** Planned in repository.

**Definition:** Runtime resilience patterns protect services from transient and cascading failures.

**Mental model:**
```text
Dependency call → timeout/retry → circuit breaker/fallback → graceful result
```

**Key terms:** bounded retry, exponential backoff, timeout, circuit breaker, fallback, idempotency, bulkhead, graceful degradation.

---

## Topic 22 — Safe Deployment

**Status:** Planned in repository.

**Definition:** Safe deployment reduces release risk through automation, tests, controlled rollout and rapid rollback.

**Mental model:**
```text
Code → CI/tests → artifact → canary/blue-green → quality gate → rollout/rollback
```

**Key terms:** CI/CD, canary, blue-green, model/version rollout, quality gates, rollback.

---

## Topic 23 — AI Observability

**Status:** Planned in repository.

**Definition:** Observability makes system behavior measurable and traceable through logs, metrics and traces, plus AI-specific quality/cost signals.

**Mental model:**
```text
Request → logs + metrics + trace → diagnose behavior and bottleneck
```

**Key terms:** correlation/request IDs, p95/p99 latency, throughput, error rate, tokens, cost, retrieval quality, cache hit rate.

---

## Topic 24 — Docker, Kubernetes & Cloud Deployment

**Status:** Planned in repository.

**Definition:** Container and orchestration concepts package, deploy, expose, health-check and scale AI services.

**Mental model:**
```text
Code → Docker image → container → Kubernetes pod/deployment → service/ingress → autoscaling
```

**Key terms:** image, container, registry, pod, deployment, service, ingress, health checks, resource limits, autoscaling.

---

## Topic 25 — AWS for AI Engineering

**Status:** Planned in repository.

**Definition:** Map AI-platform requirements to AWS primitives while explaining security, scaling and operational trade-offs.

**Mental model:**
```text
API/compute + storage + database + networking + IAM/secrets + monitoring
```

**Key services:** EC2, ECS/EKS, Lambda, S3, RDS, DynamoDB, VPC, load balancers, API Gateway, IAM, Secrets Manager, KMS, CloudWatch.

---

## Topic 25B — Security & Multi-Tenancy

**Status:** Repository file is named under `26-...` but its content is titled Topic 25.

**Definition:** Security in an AI/RAG platform ensures authentication, authorization, tenant isolation, secret protection and controlled data access.

**Mental model:**
```text
Identity → authorization/tenant scope → trusted retrieval/tool boundary → service → data
```

**Remember:** tenant and permission filters must constrain retrieval/action access before sensitive data is exposed; LLM intent is never authorization.

---

## Topic 26 — Lead / Manager Round

**Status:** Planned in repository.

**Definition:** Lead interviews evaluate technical ownership, judgment, communication, prioritization and leadership behavior.

**Mental model:**
```text
Situation → Action → Trade-off/Judgment → Result → Learning
```

**Remember:** prepare concise STAR-style stories covering ownership, incidents, disagreements, mentoring, prioritization and stakeholder management.

---

## Topic 27 — RAG Evaluation & Observability

**Status:** Planned in repository.

**Definition:** RAG evaluation measures retrieval quality, generation quality and production behavior using repeatable datasets and metrics.

**Mental model:**
```text
Golden dataset → retrieval metrics + generation metrics + system metrics → regression/monitoring
```

**Key terms:** Context Precision, Context Recall, Faithfulness, Response Relevancy, Answer Correctness, citation accuracy, LLM-as-judge, human evaluation, offline/online evaluation.

---

## Topic 28 — LangChain

**Definition:** LangChain is a framework/ecosystem providing abstractions and integrations for building LLM applications.

**Mental model:**
```text
Application
    ↓
LangChain abstractions
    ├→ models
    ├→ prompts/messages
    ├→ structured output
    ├→ tools
    ├→ retrievers/RAG
    └→ agents
```

**Remember:** LangChain ≠ LLM; it can support both ingestion and retrieval/RAG; a production system may still keep ingestion, security and domain-specific retrieval logic application-owned.

### LangChain core concepts learned

**Model Interface:** traditional LLM = text-oriented; chat model = messages in / AIMessage out.

**PromptTemplate:** reusable parameterized prompt; ChatPromptTemplate constructs structured chat messages.

**Structured Output:** model response constrained to a schema so probabilistic output can cross into typed application logic; schema correctness ≠ semantic correctness.

**Runnable:** protocol/interface for a single executable/composable unit of work.

**Chain:** workflow built by combining Runnables. Preferred mental model:

> **In LangChain, a `Runnable` is a protocol (an interface) for a single unit of work, while a `Chain` is the actual sequence or workflow built by combining those Runnables together.**

**Tools:** model-facing capabilities with name, description, input schema and execution implementation.

**Tool Calling:** model emits a structured request for a tool; runtime validates and executes it; result returns as a ToolMessage; model can continue or finish.

**Retriever:** abstraction `query → relevant documents`; underlying strategy may be vector, keyword, hybrid, database or custom.

**RAG:** retrieve external knowledge, construct context, invoke the model and generate a grounded answer.

---

## Topic 29 — LangGraph

**Definition:** LangGraph is an orchestration framework/runtime for explicit stateful workflows, especially complex agent workflows with branching, loops, persistence and human-in-the-loop requirements.

**Mental model:**
```text
State
  ↓
Node → Edge → Node
  ↘ Conditional Edge ↗
```

**Repository status:** Planned. Detailed learning is next.

---

## Topic 30 — LangChain Tools

**Definition:** A Tool is a controlled, model-facing capability that exposes an application operation to an LLM/agent.

**Mental model:**
```text
Agent/LLM
   ↓
Tool request
   ↓
validation + authentication + authorization + policy
   ↓
Tool adapter
   ↓
Service
   ↓
Repository / API client
   ↓
Result → ToolMessage → Agent/LLM
```

**Remember:** Tool ≠ Controller; Tool should normally delegate to the service layer. Reuse existing application capabilities by sharing the service, not by calling a Controller directly. LLM intent is not authorization.

---

# Cross-topic mental model

```text
                         USER
                           ↓
                        FASTAPI
                           ↓
                    Auth + Validation
                           ↓
                        SERVICE
              ┌────────────┼─────────────┐
              ↓            ↓             ↓
         Retrieval       Agent        Other logic
              ↓            ↓
       Vector/Keyword    Chat Model
              ↓            ↓
             RRF       Tool Calling
              ↓            ↓
          Reranker       Tools
              ↓            ↓
           Context      Service/API
              └──────┬─────┘
                     ↓
                    LLM
                     ↓
                 Response
```

---

# Highest-value interview distinctions

```text
ABC              = contract
DI               = supplies implementation
Repository       = persistence/data access
Service          = business/application orchestration
Strategy         = interchangeable behavior

Embedding        = semantic vector representation
Vector Search    = semantic retrieval technique
Keyword/BM25     = lexical retrieval technique
RRF              = rank fusion
Reranker         = fine-grained relevance ranking
Retriever        = query → relevant documents
RAG              = retrieval + context + generation

Runnable         = single executable/composable unit
Chain            = workflow built from units
Tool             = model-facing capability
Tool Calling     = mechanism for requesting a tool
Agent            = dynamic decision-making loop
LangGraph        = explicit stateful agent/workflow orchestration

Authentication   = who are you?
Authorization    = what are you allowed to do?
Validation       = is this input structurally/business-valid?
```

# Lead-level principles

1. Separate interfaces from implementations.
2. Keep business logic in services, not controllers or model prompts.
3. Treat LLM-generated tool arguments as untrusted input.
4. Enforce authorization in trusted application code.
5. Separate ingestion from query-time RAG where appropriate.
6. Evaluate retrieval and generation separately.
7. Optimize quality, latency and cost together.
8. Measure before optimizing.
9. Choose abstractions based on the actual problem complexity.
10. Do not claim framework production experience that has not been acquired.

# Current learning status

```text
Topics 1–16  → detailed notes completed
Topic 17     → missing from repository
Topics 18–20 → detailed notes completed
Topics 21–27 → repository placeholders/planned
Topic 28     → LangChain concepts in progress
Topic 29     → LangGraph planned / next major learning block
Topic 30     → LangChain Tools in progress
```
