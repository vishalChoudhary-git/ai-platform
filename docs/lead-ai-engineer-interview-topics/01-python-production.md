# Topic 1 — Python Coding Test: Production Python

## Status

**In progress**

## Goal

Prepare for the Python coding test with a production-oriented focus rather than spending time on large amounts of generic LeetCode practice.

## What we identified from the job posting and preparation screenshots

- Async / await and HTTP clients
- Pydantic models and validation
- Repository pattern + ABC
- Strategy / Plugin pattern
- Document chunking
- Reciprocal Rank Fusion (RRF)
- Python collections, functions, type hints and exceptions
- Production-quality code, testing and error handling

## Learning approach

We will start with basic hands-on examples and progressively increase difficulty, but keep the basic-syntax portion short because the interview has many topics to cover.

```text
Python basics
    ↓
Functions + type hints
    ↓
Async / await + HTTPX
    ↓
Pydantic
    ↓
Repository + Strategy patterns
    ↓
Chunking + RRF
    ↓
Production AI coding exercise
```

## Covered so far

### Python basics

We practiced:

- lists and dictionaries
- loops and conditions
- filtering
- `.append()`
- `sorted()` / `.sort()`
- `key=lambda`
- `max(..., key=...)`
- `enumerate()`

### Functions + type hints

Example:

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
list[str]                 → list of strings
tuple[str, float]         → tuple with two typed values
str | None                → string or None
def f(x: int) -> bool     → typed parameter and return value
```

### `*args` and `**kwargs`

```text
*args     → variable number of positional arguments
**kwargs  → variable number of keyword arguments
```

Know the concept; do not spend excessive preparation time here.

### Async / await

Basic concurrency pattern:

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

---

# Pydantic — Theory for Revision

## What is Pydantic?

Pydantic is a Python data-validation and data-modeling library built around type annotations. It is especially useful at application boundaries, where raw or untrusted data needs to become a validated Python object.

Mental model:

```text
Raw request / JSON
        ↓
    Pydantic model
        ↓
validated Python data
        ↓
business/service logic
```

## Why Pydantic when we already have type hints?

Python type hints describe expected types, but they do not by themselves perform runtime validation. Pydantic uses model declarations to parse and validate actual input at runtime.

Good interview answer:

> Type hints communicate intent and support static analysis, while Pydantic provides runtime parsing and validation. I would use Pydantic at API and service boundaries where input cannot be trusted.

## Basic model

```python
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
```

Create a model:

```python
request = SearchRequest(
    query="What was the revenue?",
    top_k=10,
)
```

Access fields using normal attributes:

```python
request.query
request.top_k
```

## Field validation

For business constraints, a field validator can enforce rules:

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

Conceptually:

```text
top_k = 5       → valid
top_k = 100     → valid
top_k = 0       → invalid
top_k = 101     → invalid
```

## Enum values

Use an Enum when only a controlled set of values is valid.

```python
from enum import Enum

class SearchType(str, Enum):
    VECTOR = "vector"
    HYBRID = "hybrid"
```

Then:

```python
class SearchRequest(BaseModel):
    query: str
    search_type: SearchType = SearchType.HYBRID
    top_k: int = 5
```

This prevents arbitrary search modes from flowing through the application.

## Optional values

```python
document_id: str | None = None
```

Means the value can be a string or `None`.

## Nested models

Production APIs often contain nested structures:

```python
from pydantic import BaseModel

class UserContext(BaseModel):
    user_id: str
    tenant_id: str

class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    context: UserContext
```

The nested model is validated as well.

## Pydantic in our AI platform

Possible request model:

```python
class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    search_type: SearchType = SearchType.HYBRID
    document_ids: list[str] | None = None
```

Possible structured application/LLM output:

```python
class Answer(BaseModel):
    answer: str
    citations: list[str]
    confidence: float
```

The main benefit is predictable structured data instead of arbitrary dictionaries moving between layers.

## Pydantic vs dataclass

A dataclass is primarily a convenient Python data container. Pydantic is focused on parsing and validating data, making it especially useful at API and external-data boundaries.

## Pydantic vs type hints

Type hints document expected types and support IDEs/static analysis. Pydantic adds runtime validation and model parsing.

## Where should validation happen?

Validate at the application boundary first. Internal services should ideally work with trusted, well-defined models rather than repeatedly validating the same raw input.

## What validation does not solve

Validation does not replace authorization, database constraints, security controls, business rules, or downstream error handling.

## Pydantic revision checklist

- [ ] `BaseModel`
- [ ] typed fields
- [ ] default values
- [ ] `field_validator`
- [ ] `Enum`
- [ ] `str | None`
- [ ] nested models
- [ ] request/response models
- [ ] validation at application boundaries
- [ ] Pydantic vs type hints
- [ ] Pydantic vs dataclasses

## Next in Topic 1

- Repository pattern + ABC
- Strategy / Plugin pattern
- Chunking implementation
- RRF implementation
- Testing and mocking
- Final production-style Python coding simulation

## Revision checklist

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
- [ ] Pydantic hands-on exercise
- [ ] Repository / ABC
- [ ] Strategy / Plugin
- [ ] Chunking
- [ ] RRF
- [ ] Testing / mocking
- [ ] Production coding simulation

## Interview reminders

### Async vs CPU-bound work

Async improves concurrency for I/O-bound operations. It does not automatically make CPU-heavy computation faster.

### `sort()` vs `sorted()`

- `list.sort()` modifies the existing list.
- `sorted()` returns a new sorted list.

### Why type hints?

They improve readability, IDE support and static analysis. They do not by themselves enforce runtime types.

### Mutable default argument

Avoid:

```python
def add_document(document, documents=[]):
    ...
```

Prefer a `None` default and initialize inside the function.
