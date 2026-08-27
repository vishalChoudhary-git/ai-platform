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
# Filter and build a list
high_score_ids = []
for document in results:
    if document["score"] >= 0.8:
        high_score_ids.append(document["id"])

# Sort the existing list in place
results.sort(
    key=lambda document: document["score"],
    reverse=True,
)

# Print ranking
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
# Print only PDF documents.
for doc in documents:
    print(f"{doc['id']}")

# Create a list containing only PDF IDs.
doc_list = []
for doc in documents:
    doc_list.append(doc["id"])
print(f"{doc_list}")

# Find the document with the highest number of pages.
sorted_results = sorted(
    documents,
    key=lambda doc: doc["pages"],
    reverse=True
)
print(f"{sorted_results[0]}")

# Sort documents by pages descending.
print(f"{sorted_results}")

# Create a list containing only the page counts.
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
# 1. PDFs
for doc in documents:
    if doc["type"] == "pdf":
        print(doc["id"])

# 2. PDF IDs
pdf_ids = []
for doc in documents:
    if doc["type"] == "pdf":
        pdf_ids.append(doc["id"])

# 3. Highest-page document
highest = max(documents, key=lambda doc: doc["pages"])

# 4. Sort descending
sorted_documents = sorted(
    documents,
    key=lambda doc: doc["pages"],
    reverse=True,
)

# 5. Page counts
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

## Theory-first topics covered without a coding exercise yet

### Pydantic

Theory is maintained in `docs/lead-ai-engineer-interview-topics/01-python-production.md`. We will not spend a separate exercise on every Pydantic feature. We will do one focused hands-on model later if needed.

Key points to revise:

- `BaseModel`
- typed fields and defaults
- `field_validator`
- `Enum`
- `str | None`
- nested models
- request/response models
- runtime validation vs type hints
- Pydantic vs dataclasses

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
- [ ] Pydantic hands-on exercise
- [ ] Repository / ABC
- [ ] Strategy / Plugin pattern
- [ ] Chunking
- [ ] RRF
- [ ] Testing / mocking
- [ ] Production coding simulation

## Mistakes to revisit

1. Use `f"...{variable}..."` when a variable must be interpolated into a URL/string.
2. Distinguish printing values from actually creating a list.
3. `list.sort()` mutates the original list; `sorted()` returns a new list.
4. Use `enumerate(..., start=1)` for human-readable ranking.
5. Async primarily helps I/O-bound concurrency; it does not automatically speed up CPU-bound work.
