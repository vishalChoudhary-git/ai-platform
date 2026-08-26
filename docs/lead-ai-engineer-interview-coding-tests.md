# Lead AI Engineer Interview — Coding Tests

This file contains the hands-on coding exercises, solutions, mistakes, and revision notes from our interview preparation.

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

Key patterns learned:

```python
# Filter and print
for document in results:
    if document["score"] >= 0.8:
        print(document["id"])

# Build a list
high_score_ids = []
for document in results:
    if document["score"] >= 0.8:
        high_score_ids.append(document["id"])

# Sort
results.sort(
    key=lambda document: document["score"],
    reverse=True,
)

# Ranking
afor rank, document in enumerate(results, start=1):
    print(f"{rank}. {document['id']} - {document['score']}")
```

Note: The `a` before `for rank` above is intentionally a mistake to fix during revision. Correct version:

```python
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

- **Task 1:** Needs a filter. The current code prints every document, not only PDFs.
- **Task 2:** The current code collects every ID. It needs `if doc["type"] == "pdf"`.
- **Task 3:** Correct approach. Sorting descending and taking `[0]` gives the highest-page document.
- **Task 4:** Correct approach. `sorted(..., key=..., reverse=True)` produces the requested ordering.
- **Task 5:** Correct approach. The loop correctly builds the page-count list.

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
print(highest)

# 4. Sort descending
sorted_documents = sorted(
    documents,
    key=lambda doc: doc["pages"],
    reverse=True,
)

# 5. Page counts
page_counts = [doc["pages"] for doc in documents]
```

### Important Python patterns from these exercises

- Iterate through a list with `for item in items`.
- Access dictionary values with `item["key"]`.
- Filter with `if` inside a loop.
- Build lists using `.append()`.
- Use `sorted()` when you want a new sorted list.
- Use `.sort()` when modifying the existing list is acceptable.
- Use `key=lambda ...` to tell Python what value to sort by.
- Use `max(..., key=...)` to find the maximum object by a field.
- Use list comprehensions after understanding the equivalent normal loop.
- Use `enumerate(..., start=1)` when a human-readable rank/index is needed.

## Progress

- [x] Level 1 — Lists, dictionaries, loops, conditions, sorting
- [x] Basic filtering and list building
- [x] `sorted()` and `max()` patterns
- [ ] List comprehensions — more practice
- [ ] Functions
- [ ] Type hints
- [ ] Exceptions
- [ ] Pydantic
- [ ] Async / await
- [ ] Repository pattern
- [ ] Strategy / Plugin pattern
- [ ] Chunking
- [ ] RRF
- [ ] Production coding simulation
