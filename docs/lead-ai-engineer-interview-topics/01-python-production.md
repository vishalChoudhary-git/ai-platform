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

We will start with basic hands-on examples and progressively increase difficulty:

```text
Python basics
    ↓
Functions + type hints
    ↓
Pydantic
    ↓
Async / await
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

## Next in Topic 1

- Pydantic models and validators
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
- [ ] Pydantic
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
