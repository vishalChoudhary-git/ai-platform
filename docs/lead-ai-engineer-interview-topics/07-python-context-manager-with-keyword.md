# Context Manager — `with` Keyword Interview Deep Dive

## What does the `with` keyword do?

The `with` statement is used with a **context manager** to handle setup and cleanup automatically around a block of code.

```python
with resource:
    do_work()
```

Mental model:

```text
enter / setup
      ↓
   do work
      ↓
exit / cleanup
```

The important benefit is that cleanup happens even if an exception occurs inside the block.

---

## Why use `with` instead of manual cleanup?

Without a context manager:

```python
file = open("data.txt")
try:
    data = file.read()
finally:
    file.close()
```

With `with`:

```python
with open("data.txt") as file:
    data = file.read()
```

The context manager takes responsibility for cleanup.

---

## How does it work internally?

A synchronous context manager implements:

```python
__enter__()
__exit__()
```

Conceptually:

```python
resource = Resource()
value = resource.__enter__()
try:
    do_work()
finally:
    resource.__exit__(...)
```

You normally do not call these methods directly; Python calls them through `with`.

---

## Exception handling

One of the biggest reasons to use a context manager is reliable cleanup.

```python
with open("data.txt") as file:
    data = file.read()
    raise ValueError("something failed")
```

Even though the block raises an exception, the file is still closed.

---

## Async context managers

For async resources use `async with`:

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

Async context managers implement:

```text
__aenter__()
__aexit__()
```

This is directly relevant to AI systems because HTTP clients, database sessions and other async resources often need deterministic cleanup.

---

## `contextlib`

Instead of implementing `__enter__` and `__exit__` manually, Python provides helpers:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    print("setup")
    try:
        yield "resource"
    finally:
        print("cleanup")
```

Usage:

```python
with managed_resource() as resource:
    print(resource)
```

For async code:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource():
    print("setup")
    try:
        yield "resource"
    finally:
        print("cleanup")
```

---

## Interview question

### What is the `with` keyword in Python?

> "`with` is used with a context manager to manage setup and cleanup around a block of code. It makes resource management safer because cleanup is performed automatically, including when an exception occurs."

### Where would you use it in an AI platform?

> "For resources such as HTTP clients, database sessions, files and other connections that need deterministic cleanup. In async services I'd use `async with`, for example with an `httpx.AsyncClient`."
