# Lead AI Engineer Interview — Additional Coding Tests

These exercises are added from the interview-preparation reference sheet and from the Min Stack coding test you were actually asked in the interview.

> Practice rule: first understand the problem and constraints, then implement. We will review complexity and production follow-ups after the solution.

---

## 1. Min Stack — Exact Interview Question ⭐

### Problem

Implement a stack that supports all of these operations in **O(1)**:

```python
class MinStack:
    def __init__(self):
        ...

    def push(self, val: int) -> None:
        ...

    def pop(self) -> int:
        ...

    def top(self) -> int:
        ...

    def get_min(self) -> int:
        ...
```

### Constraints

- `push()` → O(1)
- `pop()` → O(1)
- `top()` → O(1)
- `get_min()` → O(1)
- Maximum elements: 1000
- Correctly handle duplicate minimum values.
- Correctly handle negative values.

### Test cases to reproduce

```text
Basic push/pop:
5, 3, 7
→ top() = 7
→ pop() = 7
→ top() = 3

Minimum tracking:
10, 5, 15, 2
→ get_min() = 2
→ pop()       # removes 2
→ get_min() = 5
→ pop()       # removes 15
→ get_min() = 5

Duplicate minimum:
3, 1, 1, 2
→ get_min() = 1
→ pop()      # removes 2
→ get_min() = 1
→ pop()      # removes first 1
→ get_min() = 1
→ pop()      # removes second 1
→ get_min() = 3

Negative values:
-3, -1, -5, -2
→ get_min() = -5
→ pop()      # removes -2
→ get_min() = -5
→ pop()      # removes -5
→ get_min() = -3

Ascending sequence:
1, 5, 10, 15
→ minimum remains 1

Descending sequence:
10, 5, 1
→ minimum changes 10 → 5 → 1
```

### Key interview question

**Why can't we simply call `min(self.stack)` inside `get_min()`?**

Because scanning the stack is O(n), violating the O(1) requirement.

### Expected solution direction

Use an additional structure that keeps track of the minimum associated with each stack state. The common approach is:

```text
Main stack        Minimum stack
-----------       -------------
5                 5
3                 3
7                 3
2                 2
```

When an element is popped, the corresponding minimum state is popped as well.

### Follow-up questions

- Why do duplicate minimum values require special handling?
- Can you implement it with one stack instead of two?
- What are the time and space complexities?
- What happens if `pop()` or `top()` is called on an empty stack?

---

# 2. OpenAI API — Exponential Backoff ⭐

### Interview-style problem

Write a function that calls an LLM API and retries when a rate-limit error occurs using **exponential backoff**.

Requirements:

- bounded number of retries
- increasing delay between attempts
- do not retry forever
- raise/return a meaningful failure after retries are exhausted
- distinguish retryable errors from non-retryable errors

### Example shape

```python
def call_model_with_retry(messages: list[dict], max_retries: int = 3):
    ...
```

### What we should demonstrate

```text
Attempt 1 → rate limited → wait
Attempt 2 → rate limited → wait longer
Attempt 3 → success
```

### Follow-up questions

- Why exponential backoff instead of immediately retrying?
- Why add jitter?
- Which HTTP/API errors should be retried?
- Why should retries be bounded?
- How would you prevent a retry storm across many API workers?

---

# 3. Minimal RAG Pipeline ⭐

### Interview-style problem

Write a minimal RAG pipeline that:

- accepts a list of text documents
- accepts a user query
- creates embeddings
- retrieves the most relevant documents/chunks
- constructs context
- sends the context + question to an LLM
- returns the answer

```python
def answer_query(documents: list[str], query: str) -> str:
    ...
```

### Expected mental model

```text
Documents
   ↓
Embeddings / Index
   ↓
User Query
   ↓
Query Embedding
   ↓
Similarity Search
   ↓
Top-K Context
   ↓
LLM
   ↓
Answer
```

### Follow-up questions

- Where does chunking happen?
- Would you use vector search only or hybrid search?
- Where would metadata filtering happen?
- Where would reranking fit?
- How would you evaluate retrieval quality?
- How would you prevent hallucinations?
- What changes when the corpus grows from 10K to 1M documents?

---

# 4. LLM → Database Search Tool ⭐

### Interview-style problem

Write a function/tool that allows an LLM to search a database while validating its arguments.

Example request:

```text
"Find expenses above 1000 dollars from last month."
```

The tool should convert the model's structured arguments into a safe database operation.

### Requirements

- validate arguments
- use typed input/schema
- prevent arbitrary SQL from being supplied by the model
- use parameterized queries
- return structured results
- handle empty results and database errors

### Follow-up questions

- Why should the LLM never generate unrestricted SQL and execute it directly?
- Where should authorization happen?
- Where should validation happen?
- How would you expose this as a LangChain/LangGraph tool?
- How would you audit tool calls?

---

# 5. Top-K Documents — Retrieval-Oriented Coding Test

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

Write:

```python
def top_k_documents(results: list[dict], k: int) -> list[dict]:
    ...
```

Requirements:

- return the top K documents by score
- do not modify the original list
- handle `k <= 0`
- handle `k > len(results)`

### Follow-up

**If there are millions of documents, would you still sort everything?**

Expected discussion: heap-based Top-K selection or, in a real retrieval system, let the vector/keyword index perform candidate retrieval rather than loading the entire corpus into Python.

---

# 6. Deduplicate Retrieved Chunks — RAG Coding Test

Two retrieval methods return overlapping chunks:

```python
vector_results = [
    {"id": "c1", "score": 0.91},
    {"id": "c2", "score": 0.88},
    {"id": "c3", "score": 0.82},
]

keyword_results = [
    {"id": "c2", "score": 12.1},
    {"id": "c4", "score": 10.5},
    {"id": "c1", "score": 9.8},
]
```

Write a function that merges them without duplicate chunk IDs.

Then discuss why simply adding the vector score and keyword score is usually not a good fusion strategy.

### Follow-up

This should naturally lead into **RRF — Reciprocal Rank Fusion**.

---

# 7. LRU Cache ⭐

Implement an LRU cache:

```python
class LRUCache:
    def __init__(self, capacity: int):
        ...

    def get(self, key: str):
        ...

    def put(self, key: str, value):
        ...
```

Requirements:

- `get()` → O(1)
- `put()` → O(1)
- evict the least recently used item when capacity is exceeded

### AI connection

Explain where caching could appear in our AI systems:

```text
Query → semantic cache → RAG/LLM

Embedding request → embedding cache

Retrieval → retrieval-result cache
```

### Follow-up

- Why isn't a normal Python dictionary enough for a true O(1) LRU implementation?
- When should you use Redis instead of an in-process cache?
- What are the risks of caching AI responses?

---

# 8. Bounded Concurrent Embedding ⭐

You have 1,000 chunks to embed.

Write an async implementation that:

- processes chunks concurrently
- limits concurrency to a configurable maximum
- collects successful results
- handles individual failures

Expected concepts:

```text
asyncio
    +
Semaphore
    +
HTTP/API calls
    +
bounded concurrency
```

### Follow-up

- Why not launch 1,000 requests with `asyncio.gather()` immediately?
- How does a semaphore protect the API?
- How would you add retries?
- How would you batch embeddings?

---

# 9. Rate Limiter ⭐

Implement a simple rate limiter for an API client.

Example requirement:

```text
Maximum: 10 requests / second
```

Discuss:

- token bucket
- leaky bucket
- sliding window
- distributed rate limiting with Redis

### AI connection

Apply it to:

- LLM providers
- embedding providers
- reranker APIs
- external document parsers

---

# 10. Retry Helper with Jitter

Implement:

```python
def retry_with_backoff(func, max_retries=3):
    ...
```

The delay should increase exponentially and include random jitter.

Then explain why this is different from simply doing:

```python
for _ in range(3):
    try:
        return func()
    except Exception:
        time.sleep(1)
```

---

# 11. Query + Metadata Filtering

Given chunks:

```python
chunks = [
    {"id": "c1", "tenant_id": "t1", "type": "policy"},
    {"id": "c2", "tenant_id": "t2", "type": "policy"},
    {"id": "c3", "tenant_id": "t1", "type": "invoice"},
]
```

Write:

```python
def filter_chunks(chunks, tenant_id, document_type=None):
    ...
```

Then explain why tenant filtering must happen at the data/retrieval boundary rather than asking the LLM to ignore unauthorized chunks.

---

# 12. Production Coding Simulation

For the final stage, combine multiple concepts instead of solving isolated algorithms.

### Challenge

Build a small Python service function:

```python
async def answer_question(
    query: str,
    tenant_id: str,
) -> dict:
    ...
```

It should conceptually:

```text
validate request
      ↓
retrieve authorized chunks
      ↓
vector + keyword retrieval
      ↓
RRF / deduplication
      ↓
rerank candidates
      ↓
construct context
      ↓
call LLM with timeout/retry
      ↓
return answer + citations
```

Then explain:

- where dependency injection would be used
- where Pydantic fits
- where async helps
- where caching fits
- how you would test it
- what metrics you would emit
- how you would handle dependency failures

---

# Recommended Practice Order

```text
1. Min Stack ⭐⭐⭐   ← exact interview question
2. Top-K Documents ⭐⭐
3. Deduplicate Chunks ⭐⭐
4. Retry + Exponential Backoff ⭐⭐⭐
5. LRU Cache ⭐⭐
6. Bounded Concurrent Embedding ⭐⭐⭐
7. Rate Limiter ⭐⭐
8. LLM Database Tool ⭐⭐⭐
9. Minimal RAG Pipeline ⭐⭐⭐
10. Production Coding Simulation ⭐⭐⭐
```

The goal is not to memorize solutions. The goal is to be able to **write the code, explain the complexity, identify edge cases, and connect the implementation to a production AI system.**
