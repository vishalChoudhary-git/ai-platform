# Topic 6 — Python Data Structures, Comprehensions & Sorting

**Status:** Complete

## Interview feedback — HIGH PRIORITY

**`enumerate()` and `lambda` were explicitly asked in the interview.** Treat both as interview-revision items, not just convenience syntax.

### `enumerate()`

```python
for rank, document in enumerate(results, start=1):
    print(rank, document["id"])
```

Use `enumerate()` when you need both the item and its index/rank without manually maintaining a counter.

**Likely interview question — What is `enumerate()` and why would you use it?**

> `enumerate()` lets me iterate over a collection while getting both the current index and the value. It makes ranking/indexing logic cleaner than maintaining a separate counter.

**Project connection:** In retrieval code, `enumerate()` is useful when assigning ranks to vector or keyword results before calculating RRF scores.

### `lambda`

**`lambda`:** The keyword that tells Python you are creating an anonymous function.

**`arguments`:** The inputs passed into the function (can be none, one, or many, separated by commas).

**`expression`:** A single piece of code that gets evaluated and automatically returned. You do not write the `return` keyword.

General form:

```python
lambda arguments: expression
```

Example:

```python
square = lambda x: x * x
```

This is similar in behavior to:

```python
def square(x):
    return x * x
```

A common production use is as a small callback, especially for sorting:

```python
sorted_documents = sorted(
    documents,
    key=lambda doc: doc["score"],
    reverse=True,
)
```

**Likely interview question — What is a lambda function and where would you use it?**

> A lambda is a small anonymous function containing a single expression. I mainly use it for short callbacks or transformations, such as the `key` function passed to `sorted()`. For larger or reusable logic, I prefer a normal named function because it is clearer and easier to test.

## Completed

- lists, dictionaries, sets and tuples
- loops and conditions
- filtering and aggregation
- `.append()`
- list comprehensions
- dictionary access and `dict.get()`
- `enumerate()` for ranking/indexing
- `lambda` functions
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
- [x] `lambda` **(HIGH PRIORITY — explicitly asked in interview)**
- [x] `sorted()`
- [x] `.sort()`
- [x] `key=lambda`
- [x] `max(..., key=...)`
- [x] basic complexity trade-offs
