# Topic 2 — Async / Await, asyncio & HTTP Clients

**Status:** Complete

## Focus
`async def`, `await`, event loop, `asyncio.gather()`, `httpx.AsyncClient`, timeouts, retries, backoff, cancellation, concurrency limits and production API clients.

## Interview outcomes
Explain I/O-bound vs CPU-bound work, concurrent retrieval/API calls, failure handling and production-safe async design.

## Completed
- Async/await fundamentals
- `asyncio.gather()` for concurrent I/O
- Async HTTP with `httpx.AsyncClient`
- `raise_for_status()` and HTTP failure handling
- Timeouts
- Retry/backoff concepts
- Partial-failure handling with `return_exceptions=True`

## Revision notes

### Core mental model

```text
async def
   ↓
await I/O
   ↓
event loop can run other work
```

Async is primarily valuable for I/O-bound work such as HTTP APIs, databases, vector stores, embedding APIs and LLM calls. It does not automatically make CPU-heavy computation faster.

### Concurrent independent operations

```python
results = await asyncio.gather(
    operation_a(),
    operation_b(),
    operation_c(),
)
```

### Async HTTP pattern

```python
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.get(url)
    response.raise_for_status()
    data = response.json()
```

### Production considerations

- bounded retries
- exponential backoff
- timeouts
- rate limiting
- concurrency limits
- connection reuse
- cancellation/graceful shutdown
- structured logging/tracing
- distinguish retryable from non-retryable failures

## Project connection

Our `ai-platform` retrieval/services use async boundaries for operations dominated by I/O. The pattern is useful when calling repositories, providers and external AI services concurrently.

## Likely interview questions

### Why use async in an AI application?

> AI applications spend substantial time waiting on external APIs, databases and other I/O. Async improves concurrency for these waits.

### Why `asyncio.gather()`?

> To execute independent async operations concurrently and reduce end-to-end waiting time.

### Does async make Python faster?

> It improves concurrency for I/O-bound workloads; it does not inherently speed up CPU-bound computation.

### Why timeout external calls?

> To prevent slow or unavailable dependencies from holding requests indefinitely and exhausting application resources.

### Should every failure be retried?

> No. Retry only transient failures with bounded attempts and backoff. Permanent client errors should generally fail fast or be handled differently.

## Checklist

- [x] `async def`
- [x] `await`
- [x] `asyncio.gather()`
- [x] I/O-bound vs CPU-bound
- [x] `httpx.AsyncClient`
- [x] timeout
- [x] HTTP error handling
- [x] retries/backoff concepts
- [x] partial failure concept
