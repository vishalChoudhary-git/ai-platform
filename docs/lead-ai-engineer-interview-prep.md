# Lead AI Engineer Interview Preparation — Revision Guide

## How we will use this document

This is the **master roadmap and revision index** for the Lead AI Engineer interview preparation.

Each topic has its own Markdown file under:

`docs/lead-ai-engineer-interview-topics/`

We will expand the individual topic file as we complete it. This master file should stay easy to scan and contain the roadmap, links, status and high-level guidance rather than all the detailed theory.

### Preparation approach

For Python and coding, we will start with basic hands-on examples and progressively increase difficulty. We will optimize for **interview coverage and production relevance**, not for completing a large generic LeetCode syllabus.

For every topic:

```text
Learn → Basic example → Medium example → AI/RAG example
       → Production considerations → Interview questions
       → Coding/design exercise → Review → Update topic file
```

## Topic Map

| # | Topic | Status |
|---|---|---|
| 1 | [Python Coding Test — Production Python](lead-ai-engineer-interview-topics/01-python-production.md) | **Complete** |
| 2 | [Async / Await, asyncio & HTTP Clients](lead-ai-engineer-interview-topics/02-async-await-http-clients.md) | **Complete** |
| 3 | [Pydantic Models, Validation & Type Safety](lead-ai-engineer-interview-topics/03-pydantic-validation-type-safety.md) | **Complete** |
| 4 | [Repository Pattern, ABC & Dependency Injection](lead-ai-engineer-interview-topics/04-repository-abc-dependency-injection.md) | **Complete** |
| 5 | [Strategy / Plugin Pattern & Extensible Architecture](lead-ai-engineer-interview-topics/05-strategy-plugin-extensible-architecture.md) | **Complete** |
| 6 | [Python Data Structures, Comprehensions & Sorting](lead-ai-engineer-interview-topics/06-python-data-structures-comprehensions-sorting.md) | **Complete** |
| 7 | [Python OOP, Decorators, Generators & Context Managers](lead-ai-engineer-interview-topics/07-python-oop-decorators-generators-context-managers.md) | Planned |
| 8 | [FastAPI — APIs, Validation, Middleware & Error Handling](lead-ai-engineer-interview-topics/08-fastapi-apis-validation-middleware-errors.md) | Planned |
| 9 | [LLM Fundamentals — Tokens, Context, Temperature & Inference](lead-ai-engineer-interview-topics/09-llm-fundamentals.md) | Planned |
| 10 | [Embeddings & Vector Search Fundamentals](lead-ai-engineer-interview-topics/10-embeddings-vector-search.md) | Planned |
| 11 | [RAG Architecture — End-to-End Pipeline](lead-ai-engineer-interview-topics/11-rag-architecture-end-to-end.md) | Planned |
| 12 | [Chunking Strategies & Document Intelligence](lead-ai-engineer-interview-topics/12-chunking-document-intelligence.md) | Planned |
| 13 | [Hybrid Search — Vector + Keyword Retrieval](lead-ai-engineer-interview-topics/13-hybrid-search-vector-keyword.md) | Planned |
| 14 | [Reranking & Retrieval Optimization](lead-ai-engineer-interview-topics/14-reranking-retrieval-optimization.md) | Planned |
| 15 | [RRF — Reciprocal Rank Fusion](lead-ai-engineer-interview-topics/15-rrf-reciprocal-rank-fusion.md) | Planned |
| 16 | [RAG Hallucination, Grounding & Citations](lead-ai-engineer-interview-topics/16-rag-grounding-hallucination-citations.md) | Planned |
| 17 | [LLM Cost & Latency Optimization](lead-ai-engineer-interview-topics/18-llm-cost-latency-optimization.md) | Planned |
| 18 | [LLM / Model Serving Architecture & Model Routing](lead-ai-engineer-interview-topics/19-model-serving-routing.md) | Planned |
| 19 | [Production AI System Design & Scalability](lead-ai-engineer-interview-topics/20-production-ai-system-design.md) | Planned |
| 20 | [Resilience — Retry, Timeout, Circuit Breaker & Fallback](lead-ai-engineer-interview-topics/21-resilience-retry-timeout-circuit-breaker-fallback.md) | Planned |
| 21 | [Safe Deployment — CI/CD, Canary, Blue-Green & Rollback](lead-ai-engineer-interview-topics/22-safe-deployment-ci-cd-canary-blue-green.md) | Planned |
| 22 | [AI Observability, Monitoring, Logging & Tracing](lead-ai-engineer-interview-topics/23-ai-observability-monitoring-logging-tracing.md) | Planned |
| 23 | [Docker, Kubernetes & Cloud Deployment](lead-ai-engineer-interview-topics/24-docker-kubernetes-cloud-deployment.md) | Planned |
| 24 | [AWS for AI Engineering](lead-ai-engineer-interview-topics/25-aws-for-ai-engineering.md) | Planned |
| 25 | [Security & Multi-Tenancy](lead-ai-engineer-interview-topics/26-security-multi-tenancy-lead-manager.md) | Planned |
| 26 | [Lead/Manager Round — Leadership, Ownership & Behavioral Engineering](lead-ai-engineer-interview-topics/26-lead-manager-round.md) | Planned |
| 27 | [RAG Evaluation & Observability — Ragas + LangSmith](lead-ai-engineer-interview-topics/27-rag-evaluation-observability-ragas-langsmith.md) | **Added / Planned** |
| 28 | [LangChain](lead-ai-engineer-interview-topics/28-langchain.md) | **Added / Planned** |
| 29 | [LangGraph](lead-ai-engineer-interview-topics/29-langgraph.md) | **Added / Planned** |

> RAG evaluation/observability, LangChain and LangGraph are explicit high-priority additions based on interview feedback and the role's AI-agent focus.

## Interview feedback — update to preparation priorities

The interview included deep questions around:

- Pydantic
- query parameters vs path parameters
- Python `typing` module
- decorators
- dataclasses
- context managers
- RAG pipeline
- RRF

These are now **high-priority revision checkpoints**. Topic 7 has been expanded to explicitly cover decorators, dataclasses and context managers. We will also make API parameter design and the `typing` module part of the FastAPI/Python revision.

## LangChain + LangGraph strategy

We will **learn these frameworks even though they are not yet production technologies in the existing project**. We should not claim hands-on experience we do not have. Instead, prepare to explain the concepts and clearly connect them to our architecture.

Current official positioning: LangChain is a higher-level agent framework with model/tool integrations and prebuilt agent architecture, while LangGraph is a lower-level orchestration runtime for stateful, long-running agent workflows. LangChain agents are built on LangGraph, and LangSmith is used for tracing/evaluation. citeturn104074search1turn104074search0

## Related coding practice

Hands-on coding exercises are kept separately so this file remains a clean revision index:

- [Lead AI Engineer Interview — Coding Tests](lead-ai-engineer-interview-coding-tests.md)

## Current focus

**Next: Topic 7 — Python OOP, Decorators, Generators & Context Managers**

We will continue using the same approach: learn the important interview concepts, connect them to the `ai-platform` codebase where relevant, then do only the coding exercises that add real interview value.
