# Topic 1 — Python Coding Test: Production Python

## Status

**In progress**

## Goal

Prepare for the Python coding test with a production-oriented focus rather than spending time on large amounts of generic LeetCode practice.

## Learning approach

Keep basic Python syntax short and connect concepts to the actual `ai-platform` codebase whenever possible.

```text
Python basics
    ↓
Functions + type hints
    ↓
Async / await + HTTPX
    ↓
Pydantic
    ↓
Abstractions + dependency injection
    ↓
Strategy / plugin patterns
    ↓
Chunking + RRF
    ↓
Production AI coding exercise
```

## Covered so far

### Python basics

- lists and dictionaries
- loops and conditions
- filtering
- `.append()`
- `sorted()` / `.sort()`
- `key=lambda`
- `max(..., key=...)`
- `enumerate()`

### Functions + type hints

```python
def get_high_score_documents(
    documents: list[dict],
    threshold: float = 0.8,
) -> list[str]:
    if threshold < 0 or threshold > 1:
        raise ValueError("threshold must be between 0 and 1")

    high_score_documents = []

    for doc in documents:
        if doc["score"] >= threshold:
            high_score_documents.append(doc["id"])

    return high_score_documents
```

Important patterns:

```text
list[str]         → list of strings
tuple[str, float] → tuple with two typed values
str | None        → string or None
def f(x: int) -> bool → typed parameter and return value
```

### `*args` and `**kwargs`

```text
*args     → variable number of positional arguments
**kwargs  → variable number of keyword arguments
```

Know the concept; do not spend excessive preparation time here.

### Async / await

```python
import asyncio

async def fetch_document(doc_id: str):
    await asyncio.sleep(1)
    return f"Document {doc_id}"

async def main():
    results = await asyncio.gather(
        fetch_document("doc1"),
        fetch_document("doc2"),
        fetch_document("doc3"),
    )
    print(results)

asyncio.run(main())
```

Key idea: async is valuable primarily for I/O-bound work such as HTTP APIs, databases, vector stores, embedding APIs and LLM calls.

### Async HTTP with HTTPX

```python
import httpx

async def fetch_user(user_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"https://api.example.com/users/{user_id}"
        )
        response.raise_for_status()
        return response.json()
```

Production points:

- timeout
- bounded retries
- exponential backoff
- handling 429 and transient 5xx errors
- rate limiting
- connection reuse
- logging and tracing

# Project-connected design patterns

For interview preparation, we will learn design patterns from the code that already exists in `ai-platform`, rather than relying mainly on toy `ExpenseRepository` examples.

## ABC + abstraction: `StorageProvider`

Our project defines `StorageProvider` in `app/core/storage/base.py` using `ABC` and `abstractmethod`. The contract exposes async `upload_document`, `download_document`, and `delete_document` operations and keeps storage-specific details out of the abstraction.

A concrete implementation is `CloudflareR2StorageProvider` in `app/core/storage/cloudflare_r2.py`. It implements the storage contract and contains the R2/S3-specific details.

```text
Document/ingestion service
          ↓
   StorageProvider        ← abstraction / contract
          ↓
CloudflareR2StorageProvider
          ↓
      Cloudflare R2
```

### Interview framing

> "In my AI platform, I abstracted document storage behind `StorageProvider` so application code depends on a storage capability rather than directly on Cloudflare R2. The concrete provider owns vendor-specific details. This gives us a clean replacement and testing boundary."

This is the kind of answer we should give instead of only explaining what an ABC is.

## Dependency Injection: actual FastAPI wiring

The project demonstrates dependency injection in `app/features/documents/api/dependencies.py`.

`get_document_service()` obtains a `DocumentRepository` and a `StorageProvider` and passes them into `DocumentService`. `get_ingestion_service()` similarly injects its repository, chunk repository and storage dependency.

```text
FastAPI dependency layer
        ↓
DocumentService(repository, storage)
        ↓
 repository + StorageProvider
```

The service therefore does not need to construct `CloudflareR2StorageProvider` itself.

### Why DI matters

- lower coupling
- easier unit testing
- replaceable implementations
- clearer ownership of construction/wiring

## Repository pattern: actual retrieval example

Our `RetrievalService` accepts dependencies through its constructor:

```python
class RetrievalService:
    def __init__(
        self,
        repository: RetrievalRepository,
        embedding_provider: EmbeddingProvider,
        reranker: Reranker | None = None,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.reranker = reranker
```

The service does not instantiate these infrastructure components itself.

```text
RetrievalService
   ├── RetrievalRepository
   ├── EmbeddingProvider
   └── Reranker (optional)
```

### Repository vs Service

**Repository:** data access/persistence concerns.

**Service:** application/business orchestration such as retrieval, filtering, reranking, context construction or invoking another service.

Do not put business decisions into a repository just because they involve data.

## Strategy pattern: actual `Reranker`

Our `app/retrieval/reranking.py` defines `Reranker` as an abstract base class with an async `rerank()` contract.

```python
class Reranker(ABC):
    @abstractmethod
    async def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        ...
```

A concrete implementation exists in `app/retrieval/openrouter_nemotron_reranker.py`.

```text
              Reranker
                 ↓
        ┌────────┴─────────┐
        ↓                  ↓
OpenRouter/Nemotron   future implementation
```

The retrieval service only needs the `Reranker` contract. This is a real Strategy-style boundary because the reranking behavior/provider can be changed independently of retrieval orchestration.

### Interview framing

> "Our retrieval service depends on the `Reranker` abstraction, not on a specific reranking model. That lets us change the reranking implementation without rewriting the retrieval orchestration."

## One useful distinction

```text
ABC / interface
    → defines the contract

Dependency Injection
    → supplies the implementation

Repository pattern
    → abstracts persistence/data access

Strategy pattern
    → abstracts interchangeable behavior/algorithms
```

These concepts often work together, but they are not interchangeable terms.

## Our retrieval service — several patterns in one place

`app/retrieval/services/retrieval_service.py` is particularly useful for interview preparation because it combines:

- constructor dependency injection
- type hints
- async methods
- `enumerate()` for ranking
- dictionary-based candidate merging
- RRF scoring
- `sorted(..., key=..., reverse=True)`
- optional strategy via `Reranker | None`

It also demonstrates project-level reasoning: the service can perform retrieval with or without reranking, while the reranker implementation remains replaceable.

# Pydantic — theory for revision

## Mental model

```text
Raw / untrusted input
        ↓
     Pydantic
        ↓
Validated Python model
        ↓
Service / business logic
```

## Why Pydantic?

Python type hints describe expected types but do not by themselves enforce runtime validation. Pydantic parses and validates actual input using model declarations.

### Interview answer

> "Type hints communicate intent and support static analysis, while Pydantic provides runtime parsing and validation. I use it at API and service boundaries where input cannot be trusted."

## Basic model

```python
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
```

## Field validation

```python
from pydantic import BaseModel, field_validator

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, value: int) -> int:
        if value <= 0 or value > 100:
            raise ValueError("top_k must be between 1 and 100")
        return value
```

Use validators for business constraints beyond basic type declarations.

## Enum

```python
from enum import Enum

class SearchType(str, Enum):
    VECTOR = "vector"
    HYBRID = "hybrid"
```

Use an enum when the application supports a controlled set of values.

## Nested models

```python
class UserContext(BaseModel):
    user_id: str
    tenant_id: str

class ChatRequest(BaseModel):
    query: str
    context: UserContext
```

## Optional values

```python
document_id: str | None = None
```

## Pydantic in an AI application

```python
class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    search_type: SearchType = SearchType.HYBRID
    document_ids: list[str] | None = None
```

We can also use Pydantic models for structured application/LLM outputs:

```python
class Answer(BaseModel):
    answer: str
    citations: list[str]
    confidence: float
```

## Interview distinctions

**Pydantic vs type hints:** type hints describe intent/static expectations; Pydantic provides runtime parsing/validation.

**Pydantic vs dataclass:** dataclasses are primarily data containers; Pydantic focuses on data parsing and validation.

**Where to validate:** validate at application boundaries first, then let internal services work with trusted models.

**What validation does not solve:** authorization, database constraints, security, business authorization rules and downstream failure handling still matter.

# Next in Topic 1

- Complete Strategy / Plugin section using the document parser architecture.
- Cover chunking implementation.
- Cover RRF implementation.
- Add testing and mocking.
- Finish with a production-style Python coding simulation.

# Revision checklist

- [x] Lists / dictionaries / loops / conditions
- [x] Filtering and list building
- [x] Sorting and `key=lambda`
- [x] `enumerate()`
- [x] Functions
- [x] Default arguments
- [x] Type hints
- [x] Basic `raise ValueError`
- [x] `*args` / `**kwargs` concepts
- [x] `async def` / `await`
- [x] `asyncio.gather()`
- [x] `httpx.AsyncClient`
- [x] Pydantic theory
- [x] ABC / abstraction — project example
- [x] Dependency injection — project example
- [x] Strategy concept — project example
- [ ] Pydantic hands-on exercise
- [ ] Full parser Strategy/Plugin implementation
- [ ] Chunking
- [ ] RRF
- [ ] Testing / mocking
- [ ] Production coding simulation
