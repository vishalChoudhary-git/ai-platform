# Lead AI Engineer Interview — Coding Tests

This file contains the hands-on coding exercises, solutions, mistakes, and revision notes from our interview preparation.

> **Rule:** We practice from basic Python to production AI code. Exercises live here; topic theory lives in the dedicated topic files under `docs/lead-ai-engineer-interview-topics/`.

## Topic 1 — Python Coding Test

### Level 1 — Python Fundamentals

#### Exercise 1 — Documents and Retrieval Results

Given:

```python
results = [
    {"id": "doc1", "score": 0.91},
    {"id": "doc2", "score": 0.42},
    {"id": "doc3", "score": 0.85},
    {"id": "doc4", "score": 0.31},
    {"id": "doc5", "score": 0.95},
]
```

Tasks:

1. Print all document IDs.
2. Print documents with score >= 0.8.
3. Create a list containing only their IDs.
4. Sort all results by score descending.
5. Print the ranking using `enumerate()`.

### User attempt / review

The attempt correctly used list iteration, dictionary access, filtering, `.sort()`, `lambda`, and `reverse=True`. The main gaps were building a new list rather than printing values and remembering `enumerate()` for human-readable ranking.

Correct patterns:

```python
high_score_ids = []
for document in results:
    if document["score"] >= 0.8:
        high_score_ids.append(document["id"])

results.sort(
    key=lambda document: document["score"],
    reverse=True,
)

for rank, document in enumerate(results, start=1):
    print(f"{rank}. {document['id']} - {document['score']}")
```

---

#### Exercise 2 — Documents and Page Counts

Given:

```python
documents = [
    {"id": "doc1", "type": "pdf", "pages": 10},
    {"id": "doc2", "type": "docx", "pages": 5},
    {"id": "doc3", "type": "pdf", "pages": 20},
    {"id": "doc4", "type": "pdf", "pages": 7},
    {"id": "doc5", "type": "docx", "pages": 15},
]
```

Tasks:

1. Print only PDF documents.
2. Create a list containing only PDF IDs.
3. Find the document with the highest number of pages.
4. Sort documents by pages descending.
5. Create a list containing only page counts.

### User attempt

```python
for doc in documents:
    print(f"{doc['id']}")

doc_list = []
for doc in documents:
    doc_list.append(doc["id"])
print(f"{doc_list}")

sorted_results = sorted(
    documents,
    key=lambda doc: doc["pages"],
    reverse=True
)
print(f"{sorted_results[0]}")
print(f"{sorted_results}")

page_list = []
for doc in documents:
    page_list.append(doc["pages"])
print(f"{page_list}")
```

### Review

- **Task 1:** Needs a filter. The original code printed every document instead of only PDFs.
- **Task 2:** Needs the same PDF filter before appending the ID.
- **Task 3:** Correct approach. Sorting descending and taking `[0]` finds the highest-page document.
- **Task 4:** Correct.
- **Task 5:** Correct.

Correct patterns:

```python
for doc in documents:
    if doc["type"] == "pdf":
        print(doc["id"])

pdf_ids = []
for doc in documents:
    if doc["type"] == "pdf":
        pdf_ids.append(doc["id"])

highest = max(documents, key=lambda doc: doc["pages"])

sorted_documents = sorted(
    documents,
    key=lambda doc: doc["pages"],
    reverse=True,
)

page_counts = [doc["pages"] for doc in documents]
```

---

### Level 2 — Functions + Type Hints

#### Exercise 3 — Filter High-Score Documents

Given:

```python
documents = [
    {"id": "doc1", "score": 0.91},
    {"id": "doc2", "score": 0.42},
    {"id": "doc3", "score": 0.85},
    {"id": "doc4", "score": 0.31},
    {"id": "doc5", "score": 0.95},
]
```

Task:

```python
def get_high_score_documents(
    documents: list[dict],
    threshold: float = 0.8,
) -> list[str]:
    ...
```

Return only the IDs whose score is greater than or equal to `threshold`.

### User solution

```python
def get_high_score_documents(
    documents: list[dict],
    threshold: float = 0.8
) -> list[str]:
    high_score_documents = []
    for doc in documents:
        if doc["score"] >= threshold:
            high_score_documents.append(doc["id"])

    return high_score_documents
```

### Review

**Correct.** This demonstrates function definition, parameters, default arguments, type hints, `list[dict]`, return type `list[str]`, filtering, `.append()` and `return`.

Additional validation:

```python
if threshold < 0 or threshold > 1:
    raise ValueError("threshold must be between 0 and 1")
```

---

### Level 3 — Async / Await

#### Exercise 4 — Concurrent document fetching

Task:

```python
import asyncio

async def fetch_documents(doc_id: str):
    await asyncio.sleep(2)
    return f"document:{doc_id}"
```

Use `asyncio.gather()` to fetch `doc1`, `doc2`, and `doc3` concurrently.

### User solution

```python
async def fetch_documents(doc_id: str):
    await asyncio.sleep(2)
    return f"document:{doc_id}"

async def main():
    res1, res2, res3 = await asyncio.gather(
        fetch_documents("doc1"),
        fetch_documents("doc2"),
        fetch_documents("doc3"),
    )
    print(res1, res2, res3)

asyncio.run(main())
```

### Review

**Correct.** `asyncio.gather()` allows independent async operations to run concurrently. Three simulated two-second waits take roughly two seconds rather than six seconds.

A list-oriented variant is easier to scale:

```python
results = await asyncio.gather(
    fetch_documents("doc1"),
    fetch_documents("doc2"),
    fetch_documents("doc3"),
)
```

We also discussed `return_exceptions=True` when partial success should be collected rather than immediately propagating an exception.

---

#### Exercise 5 — Async HTTP with HTTPX

Task:

```python
async def fetch_user(user_id: str) -> dict:
    ...
```

Requirements:

- GET `/users/{user_id}`
- timeout of 10 seconds
- `raise_for_status()`
- return JSON

### User attempt

```python
async def fetch_user(user_id: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get("https://api.example.com/user/{user_id}")
        response.raise_for_status()
        return response.json()
```

### Review

The structure was correct. Two small corrections:

1. Use an f-string so `user_id` is interpolated.
2. Use the requested 10-second timeout.

Correct version:

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

Production concepts connected to this exercise:

- timeouts
- bounded retries
- exponential backoff
- HTTP 429 / 5xx handling
- rate limiting
- structured logging
- tracing
- circuit breakers / fallbacks

---

### Topic 7 — Decorator micro-exercise / revision

The important interview definition we chose to remember:

> **A decorator is a function that takes a function as an argument and returns a function.**

Example:

```python
def decorator(func):
    def wrapper():
        print("Transaction Initiated")
        func()
        print("Transaction Completed")

    return wrapper

@decorator
def hello():
    print("Executing all steps of transaction")

hello()
```

Key transformation:

```python
@decorator
def hello():
    ...
```

is equivalent in concept to:

```python
hello = decorator(hello)
```

Production-safe wrapper:

```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result

    return wrapper
```

### Revision points

- decorator receives a callable and returns a callable
- `@decorator` is decorator syntax
- wrapper commonly uses `*args` and `**kwargs`
- `functools.wraps` preserves function metadata
- common use cases: logging, timing, authorization, caching, retries, instrumentation
- FastAPI's `@app.get()` / `@app.post()` are a practical framework example of decorators

---

## Project-based design-pattern questions

These are not separate syntax drills. They are interview questions to answer using our real project implementations.

### Question — Tell me about chunking in your AI system.

Expected answer structure:

> "Our document-intelligence pipeline separates parsing from chunking. The parser produces a normalized `ParsedDocument`, and the chunker converts that into `DocumentChunk` objects suitable for retrieval. We preserve useful provenance such as document/page context. Chunk size and overlap are treated as tunable retrieval parameters, and I would validate those choices using retrieval and end-to-end evaluation rather than assuming one universal size."

### Question — Why did you separate parsing and chunking?

> "They have different responsibilities. Parsing extracts and normalizes document structure, while chunking decides how that structured content should be divided into retrieval units. Keeping them separate lets us change the chunking strategy without changing the parser and lets the chunker operate on a standardized document representation."

### Question — Why use a `BaseChunker` abstraction?

> "It gives us a stable chunking contract and allows different chunking strategies to be introduced independently of the rest of the pipeline. It also gives us a clean testing seam."

### Question — Why not use a fixed chunk size everywhere?

> "Document structure and query behavior vary. I treat chunk size and overlap as tunable parameters and evaluate them against representative retrieval data, balancing retrieval quality, context size, latency and cost."

### Question — Why preserve metadata with a chunk?

> "For citations and provenance, metadata/permission filtering, and debugging retrieval behavior."

### Question — Why is chunking evaluated through retrieval instead of only looking at chunks?

> "The purpose of chunking is to support retrieval and answer generation. A chunk can look reasonable to a developer but still perform poorly for actual queries, so I evaluate it using retrieval metrics and downstream answer quality while considering latency and cost."

### Project-based abstraction questions

#### Why did you introduce `StorageProvider`?

> "The application depends on a storage capability rather than directly on Cloudflare R2. `StorageProvider` defines the contract while `CloudflareR2StorageProvider` contains vendor-specific details. This gives us a replacement and testing boundary."

#### Where is dependency injection in your project?

> "Our FastAPI dependency layer constructs the repository and storage dependencies and passes them into services. The services therefore don't need to create their infrastructure dependencies themselves."

#### Why is `Reranker` an abstraction?

> "The retrieval service should not be coupled to a specific reranking model/provider. By depending on the `Reranker` contract, we can change the reranking implementation independently of retrieval orchestration."

## Progress

- [x] Lists, dictionaries, loops, conditions, sorting
- [x] Filtering and list building
- [x] `sorted()` and `max()` patterns
- [x] Functions
- [x] Type hints
- [x] Basic input validation with `raise`
- [x] Async / await basics
- [x] `asyncio.gather()`
- [x] HTTPX async request basics
- [x] Pydantic theory
- [x] ABC / abstraction — project example
- [x] Dependency injection — project example
- [x] Strategy concept — project example
- [x] Chunking theory + project-based interview questions
- [x] Decorator theory and framework connection
- [ ] Pydantic hands-on exercise
- [ ] Full parser Strategy/Plugin implementation
- [ ] RRF
- [ ] Testing / mocking
- [ ] Production coding simulation

## Mistakes to revisit

1. Use `f"...{variable}..."` when a variable must be interpolated into a URL/string.
2. Distinguish printing values from actually creating a list.
3. `list.sort()` mutates the original list; `sorted()` returns a new list.
4. Use `enumerate(..., start=1)` for human-readable ranking.
5. Async primarily helps I/O-bound concurrency; it does not automatically speed up CPU-bound work.

---

## Additional coding tests

A separate expanded coding bank has been added at:

`docs/lead-ai-engineer-interview-coding-tests-additional.md`

It includes the exact Min Stack exercise from the interview plus production-oriented exercises for exponential backoff, minimal RAG, LLM database tools, Top-K retrieval, chunk deduplication/RRF, LRU cache, bounded async embedding, rate limiting, metadata filtering and a final production coding simulation.
