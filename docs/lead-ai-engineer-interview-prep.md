# Lead AI Engineer Interview Preparation --- Revision Guide

## How we will use this document

This is our living revision document. We will keep the full topic map at
the beginning and expand one topic at a time. After each completed
topic, we will update this document with concepts, examples, interview
questions, coding exercises, mistakes and revision notes.

**Python approach:** start with basic hands-on examples, then
progressively increase difficulty. We will not jump straight into
complex LeetCode-style problems.

## Topic Map

1.  Python Coding Test --- Production Python

2.  Async / Await, asyncio & HTTP Clients

3.  Pydantic Models, Validation & Type Safety

4.  Repository Pattern, ABC & Dependency Injection

5.  Strategy / Plugin Pattern & Extensible Architecture

6.  Python Data Structures, Comprehensions & Sorting

7.  Python OOP, Decorators, Generators & Context Managers

8.  FastAPI --- APIs, Validation, Middleware & Error Handling

9.  LLM Fundamentals --- Tokens, Context, Temperature & Inference

10. Embeddings & Vector Search Fundamentals

11. RAG Architecture --- End-to-End Pipeline

12. Chunking Strategies & Document Intelligence

13. Hybrid Search --- Vector + Keyword Retrieval

14. Reranking & Retrieval Optimization

15. RRF --- Reciprocal Rank Fusion

16. RAG Hallucination, Grounding & Citations

17. RAG Evaluation & Observability --- Ragas + LangSmith

18. LLM Cost & Latency Optimization

19. LLM / Model Serving Architecture & Model Routing

20. Production AI System Design & Scalability

21. Resilience --- Retry, Timeout, Circuit Breaker & Fallback

22. Safe Deployment --- CI/CD, Canary, Blue-Green & Rollback

23. AI Observability, Monitoring, Logging & Tracing

24. Docker, Kubernetes & Cloud Deployment

25. AWS for AI Engineering

26. Security, Multi-Tenancy & Lead/Manager Engineering

27. **RAG Evaluation & Observability --- Ragas + LangSmith** *(added
    topic)*

------------------------------------------------------------------------

# Topic 1 --- Python Coding Test: Production Python

The screenshots for this role strongly suggest production/application
Python rather than only algorithm puzzles. Topic 1 therefore covers
async APIs, Pydantic, repository and strategy patterns, chunking, RRF,
Python fundamentals and production-quality coding.

## 1. Async / await + HTTP clients

### Core idea

`async def` defines a coroutine. `await` pauses that coroutine while an
I/O operation is in progress, allowing other asynchronous work to run.

Basic example:

``` python
import asyncio

async def get_data():
    await asyncio.sleep(1)
    return "data"

async def main():
    result = await get_data()
    print(result)

asyncio.run(main())
```

### Concurrent operations

``` python
import asyncio

async def fetch_a():
    await asyncio.sleep(1)
    return "A"

async def fetch_b():
    await asyncio.sleep(1)
    return "B"

async def main():
    a, b = await asyncio.gather(fetch_a(), fetch_b())
    print(a, b)

asyncio.run(main())
```

### HTTP client pattern

``` python
import httpx

async def fetch_embeddings(texts: list[str], api_key: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.example.com/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "input": texts,
                "model": "text-embedding-3-small",
            },
        )
        response.raise_for_status()
        return response.json()
```

### Must know

-   `async def`
-   `await`
-   `async with`
-   `asyncio.gather()`
-   `httpx.AsyncClient`
-   I/O-bound vs CPU-bound work
-   timeout
-   retry and exponential backoff
-   HTTP 429/5xx handling
-   rate limiting

**Interview answer:** AI applications spend substantial time waiting for
model APIs, embedding services, databases and other I/O. Async can
improve concurrency and throughput for those operations. Async does not
automatically make CPU-heavy work faster.

## 2. Pydantic models + validation

``` python
from pydantic import BaseModel

class Expense(BaseModel):
    id: str
    amount: float
```

Enum:

``` python
from enum import Enum

class ExpenseStatus(str, Enum):
    SUBMITTED = "submitted"
    INFORMATION_REQUIRED = "information_required"
    APPROVED = "approved"
```

Validation:

``` python
from pydantic import BaseModel, field_validator

class Expense(BaseModel):
    id: str
    amount: float

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("amount must be positive")
        return value
```

AI-platform example:

``` python
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

**Interview answer:** Pydantic is useful at API and service boundaries
because it validates untrusted input and converts it into well-defined
typed models.

## 3. Repository pattern + ABC

``` python
from abc import ABC, abstractmethod

class DocumentRepository(ABC):

    @abstractmethod
    async def get_by_id(self, document_id: str):
        ...
```

Concrete implementation:

``` python
class PostgresDocumentRepository(DocumentRepository):

    async def get_by_id(self, document_id: str):
        ...
```

Architecture:

``` text
ChatService
    |
    v
DocumentRepository
    |
    +-- PostgresDocumentRepository
    +-- MockDocumentRepository
```

Why use it?

-   separation of concerns
-   dependency inversion
-   replaceable persistence implementation
-   easier unit testing

## 4. Strategy / Plugin pattern

``` python
from abc import ABC, abstractmethod

class DocumentParser(ABC):

    @abstractmethod
    async def parse(self, file_bytes: bytes):
        ...
```

Implementations:

``` python
class LiteParser(DocumentParser):

    async def parse(self, file_bytes: bytes):
        ...


class ManagedParser(DocumentParser):

    async def parse(self, file_bytes: bytes):
        ...
```

Registry:

``` python
def get_parser(provider: str) -> DocumentParser:
    registry = {
        "lite": LiteParser,
        "managed": ManagedParser,
    }

    if provider not in registry:
        raise ValueError(f"Unknown parser: {provider}")

    return registry[provider]()
```

**Interview answer:** This keeps orchestration dependent on an
abstraction and supports the Open/Closed Principle: a new parser can be
added without changing the core workflow.

## 5. Chunking

Concept:

``` text
Document
   ↓
Sections
   ↓
Words/tokens
   ↓
Chunks
   ↓
Overlap
```

Example configuration:

``` python
chunk_size = 512
overlap = 64
```

Simple implementation:

``` python
def chunk_words(text: str, chunk_size: int = 10, overlap: int = 2) -> list[str]:
    words = text.split()
    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk = words[start:start + chunk_size]
        if chunk:
            chunks.append(" ".join(chunk))

    return chunks
```

Overlap helps preserve context across chunk boundaries.

**Interview point:** 512 is a starting value, not a universal optimum.
Chunk size and overlap should be evaluated against document structure,
retrieval quality, context needs and cost.

## 6. Reciprocal Rank Fusion (RRF)

RRF combines ranked lists from different retrieval systems.

``` text
Vector search:   A, B, C, D
Keyword search:  C, A, E, B
```

Formula:

``` text
score(d) = Σ 1 / (k + rank(d))
```

Python:

``` python
def reciprocal_rank_fusion(
    result_lists: list[list[str]],
    k: int = 60,
) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}

    for results in result_lists:
        for rank, doc_id in enumerate(results):
            scores[doc_id] = (
                scores.get(doc_id, 0.0)
                + 1 / (k + rank + 1)
            )

    return sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )
```

**Interview answer:** Vector and keyword retrieval scores may live on
different scales. RRF combines their ranks rather than directly
comparing raw scores.

## 7. Python fundamentals supporting Topic 1

We will learn these through exercises:

-   `list`, `dict`, `set`, `tuple`
-   comprehensions
-   `sorted()` and `key=lambda`
-   `enumerate()`
-   `zip()`
-   `any()`, `all()`, `min()`, `max()`, `sum()`
-   type hints such as `list[str]` and `dict[str, float]`
-   exceptions and custom exceptions
-   decorators
-   generators
-   context managers
-   dataclasses
-   ABCs
-   dependency injection
-   logging
-   unit testing and mocking
-   time/space complexity

## 8. Progressive hands-on path

### Level 1 --- Basic Python

1.  Count word frequency
2.  Find duplicates
3.  Sort dictionaries
4.  Find the highest score per ID
5.  Filter and transform lists

### Level 2 --- Functions + typing

6.  Add type hints
7.  Write reusable functions
8.  Handle invalid input
9.  Create custom exceptions

### Level 3 --- Pydantic

10. Build a request model
11. Add field validation
12. Add enums
13. Handle invalid input

### Level 4 --- Async

14. Write a basic async function
15. Call multiple async functions
16. Use `asyncio.gather()`
17. Build a small async HTTP client

### Level 5 --- Architecture patterns

18. Repository abstraction
19. Mock repository
20. Strategy/plugin registry

### Level 6 --- AI-oriented Python

21. Chunk a document
22. Combine retrieval results
23. Implement RRF
24. Build a small async retrieval pipeline

### Level 7 --- Interview simulation

25. Debug broken production code
26. Refactor poor Python
27. Explain design decisions
28. Complete a timed mini AI coding task

## Topic 1 revision checklist

-   [ ] `async def`
-   [ ] `await`
-   [ ] `async with`
-   [ ] `asyncio.gather`
-   [ ] `httpx.AsyncClient`
-   [ ] HTTP errors / timeout / retry
-   [ ] Pydantic `BaseModel`
-   [ ] `field_validator`
-   [ ] Enum
-   [ ] ABC / `abstractmethod`
-   [ ] Repository pattern
-   [ ] Strategy / Plugin pattern
-   [ ] Registry pattern
-   [ ] Chunking
-   [ ] Chunk overlap
-   [ ] RRF
-   [ ] `dict` / `list` / `set`
-   [ ] comprehensions
-   [ ] `sorted` + `key`
-   [ ] type hints
-   [ ] exceptions
-   [ ] generators
-   [ ] decorators
-   [ ] context managers
-   [ ] testing / mocking

------------------------------------------------------------------------

# Topic 27 --- RAG Evaluation & Observability

Added separately because it is especially relevant to this role.

We will cover:

-   evaluation datasets and golden datasets
-   Context Precision
-   Context Recall
-   Faithfulness
-   Response Relevancy
-   Answer Correctness
-   citation accuracy
-   LLM-as-judge
-   human evaluation
-   offline evaluation
-   online evaluation
-   regression testing
-   Ragas
-   LangSmith tracing and experiments
-   production monitoring
-   latency, token and cost metrics

------------------------------------------------------------------------

## Our rule for every future topic

``` text
1. Learn the concept
2. Basic hands-on example
3. Modify the example
4. Medium example
5. AI/RAG-oriented example
6. Production considerations
7. Interview questions
8. Coding exercise
9. Review mistakes
10. Update this document
```
