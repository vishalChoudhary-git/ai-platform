# Topic 6 — Python Data Structures, Comprehensions & Sorting

**Status:** Complete

## Focus
Lists, dictionaries, sets, tuples, comprehensions, `enumerate`, `zip`, `sorted`, `max`, `min`, hashing and common complexity trade-offs.

## Interview feedback — HIGH PRIORITY

**`enumerate()` was explicitly asked in the interview.** Treat it as an interview-revision item, not just a convenience function.

```python
for rank, document in enumerate(results, start=1):
    print(rank, document["id"])
```

Use `enumerate()` when you need both the item and its index/rank without manually maintaining a counter.

### Likely interview question

**What is `enumerate()` and why would you use it?**

> `enumerate()` lets me iterate over a collection while getting both the current index and the value. It makes ranking/indexing logic cleaner than maintaining a separate counter.

### Project connection

In retrieval code, `enumerate()` is useful when assigning ranks to vector or keyword results before calculating RRF scores.

## Completed
- lists, dictionaries, sets and tuples
- loops and conditions
- filtering and aggregation
- `.append()`
- list comprehensions
- dictionary access and `dict.get()`
- `enumerate()` for ranking/indexing
- `sorted()` vs `.sort()`
- `key=lambda`
- `max(..., key=...)`
- basic transformation/ranking patterns used in retrieval code

## Core revision patterns

### List

```python
doc_ids = ["doc1", "doc2", "doc3"]
doc_ids.append("doc4")
```

### Dictionary

```python
document = {
    "id": "doc1",
    "score": 0.91,
}

score = document.get("score", 0.0)
```

### Set

Use sets for uniqueness and fast membership checks when appropriate:

```python
unique_ids = {"doc1", "doc2", "doc1"}
```

### Filtering

```python
high_score = [
    doc for doc in documents
    if doc["score"] >= 0.8
]
```

### Sorting

```python
sorted_documents = sorted(
    documents,
    key=lambda doc: doc["score"],
    reverse=True,
)
```

`sorted()` returns a new list; `.sort()` mutates the existing list.

### Ranking

```python
for rank, doc in enumerate(documents, start=1):
    print(rank, doc["id"])
```

### Maximum by field

```python
highest = max(
    documents,
    key=lambda doc: doc["pages"],
)
```

## Project connection

These patterns appear directly in `ai-platform` retrieval code: results are ranked with `enumerate()`, candidates are merged using dictionaries keyed by chunk ID, and final candidates are sorted by RRF score. This is why the fundamentals matter for the AI coding test.

## Complexity points to remember

- list membership: typically **O(n)**
- set/dict membership: typically **O(1)** average case
- sorting: **O(n log n)**
- iterating through a list: **O(n)**

Use the data structure that matches the operation you need rather than choosing one arbitrarily.

## Interview questions

### When would you use a set instead of a list?

> When uniqueness and fast membership checks are more important than ordering/indexed access.

### `sort()` vs `sorted()`?

> `sort()` modifies the existing list; `sorted()` returns a new sorted list.

### Why use `key=lambda`?

> It tells Python which derived value should be used for comparison/sorting.

### Why use `enumerate()`?

> It provides both the index/rank and the value while iterating and avoids manually maintaining a counter.

### List comprehension vs normal loop?

> A comprehension is concise for simple transformations and filtering. Use a normal loop when the logic becomes complex or less readable as a one-liner.

## Checklist

- [x] list
- [x] dict
- [x] set
- [x] tuple
- [x] filtering
- [x] list comprehension
- [x] `dict.get()`
- [x] `enumerate()` **(HIGH PRIORITY — explicitly asked in interview)**
- [x] `sorted()`
- [x] `.sort()`
- [x] `key=lambda`
- [x] `max(..., key=...)`
- [x] basic complexity trade-offs
