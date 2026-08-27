# Topic 7 — Python OOP, Decorators, Generators & Context Managers

**Status:** Complete

## Focus
Classes, inheritance vs composition, `@property`, decorators, dataclasses, generators/`yield`, context managers, `with`, and clean object-oriented design.

## New interview feedback
The interviewer explicitly asked deep questions around:

- decorators
- dataclasses
- context managers

These are high-priority revision areas.

## 1. Classes and objects

A class is a blueprint; an object is an instance of that class.

```python
class Document:
    def __init__(self, document_id: str, name: str):
        self.document_id = document_id
        self.name = name

    def describe(self) -> str:
        return f"{self.document_id}: {self.name}"
```

### `self`

`self` refers to the current object/instance.

## 2. Inheritance vs composition

### Inheritance

Use inheritance when there is a genuine substitutable relationship and a common abstraction/contract.

```python
class BaseParser:
    def parse(self):
        ...

class PdfParser(BaseParser):
    def parse(self):
        ...
```

### Composition

Use composition when one object owns/uses another object and behavior needs to vary independently.

```python
class DocumentParser:
    def __init__(self, parser):
        self.parser = parser

    def parse(self, source):
        return self.parser.parse(source)
```

### Project connection

The `ai-document-intelligence` `DocumentParser` holds a `BaseParser` implementation and delegates parsing to it. This is a concrete example of composition around interchangeable strategies.

### Interview answer

> "I generally prefer composition when behavior needs to vary independently, and inheritance when there is a genuine substitutable abstraction or contract."

## 3. `@property`

A property makes a method accessible like an attribute.

```python
class Document:
    def __init__(self, pages: int):
        self.pages = pages

    @property
    def is_large(self) -> bool:
        return self.pages > 100
```

## 4. Decorators — high priority

### Definition to remember

> **A decorator is a function that takes a function as an argument and returns a function.**

More generally, a decorator is a callable that takes a function/class and returns a modified or wrapped callable.

Basic example:

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
```

The syntax:

```python
@decorator
def hello():
    ...
```

is equivalent in concept to:

```python
hello = decorator(hello)
```

### Why decorators?

They are useful for cross-cutting concerns such as:

- logging
- timing
- authorization
- caching
- retries
- instrumentation

### `*args` and `**kwargs` in decorators

A reusable decorator usually accepts arbitrary arguments:

```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Calling function")
        result = func(*args, **kwargs)
        print("Finished")
        return result

    return wrapper
```

### Why `functools.wraps`?

It preserves metadata such as the wrapped function's name and docstring.

### Project/framework connection

```text
Decorator
   ↓
FastAPI @app.get / @app.post
```

FastAPI route decorators register endpoint functions with the framework. This is a useful real-world example to mention in an interview.

## 5. Dataclasses

`@dataclass` is useful for lightweight typed data containers.

```python
from dataclasses import dataclass

@dataclass
class Document:
    document_id: str
    text: str
```

Python generates common methods such as `__init__` and a useful representation/equality behavior.

### When to use a dataclass

Use it when the primary need is a lightweight Python data object and full runtime parsing/validation is not required.

### Dataclass vs Pydantic

```text
dataclass
    ↓
primarily a Python data container

Pydantic
    ↓
runtime parsing + validation
```

### Mutable defaults

Avoid:

```python
@dataclass
class Document:
    tags: list[str] = []
```

Prefer:

```python
from dataclasses import dataclass, field

@dataclass
class Document:
    tags: list[str] = field(default_factory=list)
```

### `frozen=True`

```python
@dataclass(frozen=True)
class DocumentId:
    value: str
```

Useful when the object should be immutable after construction.

## 6. Context managers — high priority

A context manager manages setup and cleanup around a block of code.

Common syntax:

```python
with resource:
    do_work()
```

and asynchronously:

```python
async with resource:
    await do_work()
```

### Mental model

```text
enter
  ↓
do work
  ↓
exit / cleanup
```

### What happens behind `with`?

Class-based context managers implement:

```python
__enter__()
__exit__()
```

For async context managers the equivalents are:

```python
__aenter__()
__aexit__()
```

### Why use context managers?

They make resource lifecycle explicit and help guarantee cleanup even when an exception occurs.

Examples:

- files
- locks
- database transactions
- HTTP clients
- temporary resources

### Project connection

We already used:

```python
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.get(url)
```

This is a real context-manager pattern from our async HTTP work.

### `contextlib.contextmanager`

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    print("Acquire")
    try:
        yield
    finally:
        print("Release")
```

The `finally` block ensures cleanup.

## 7. Generators

Generators use `yield` to produce values lazily.

```python
def get_numbers():
    yield 1
    yield 2
    yield 3
```

Instead of creating all values immediately, they produce values as they are consumed.

### Why generators?

Useful for:

- large datasets
- incremental processing
- streaming
- memory efficiency

### List vs generator

```text
list
→ all values are materialized now

generator
→ values are produced on demand
```

### Async generators

```python
async def stream_tokens():
    yield "Hello"
    yield " world"

async for token in stream_tokens():
    print(token)
```

This maps naturally to LLM token streaming and other asynchronous streams.

## 8. High-value interview questions

### What is a decorator?

> A decorator is a function that takes a function as an argument and returns a function. It lets us add behavior without changing the original function implementation.

### What does `@decorator` mean?

> It is syntactic sugar for assigning the decorated function to the result of calling the decorator with that function.

### Why use `functools.wraps`?

> To preserve metadata of the original function when it is wrapped.

### Why use dataclass?

> For lightweight typed data containers when full runtime validation is not required.

### Dataclass vs Pydantic?

> Dataclasses are primarily data containers; Pydantic is designed for parsing and runtime validation.

### What is a context manager?

> A context manager manages setup and cleanup around a block of code and can guarantee cleanup even when an exception occurs.

### What are `__enter__` and `__exit__`?

> They define the synchronous context-manager lifecycle. Async context managers use `__aenter__` and `__aexit__`.

### What is a generator?

> A generator uses `yield` to produce values lazily, which can reduce memory usage and support incremental processing.

### Composition vs inheritance?

> Prefer composition when behavior varies independently; use inheritance when there is a real substitutable relationship and shared contract.

## 9. The project/framework mental model

```text
Decorator
   ↓
FastAPI @app.get / @app.post
```

```text
Context Manager
   ↓
async with httpx.AsyncClient()
```

```text
Strategy / ABC
   ↓
BaseParser / Reranker
```

```text
Dataclass / typed data object
   ↓
lightweight internal data representation
```

```text
Generator
   ↓
streaming / large-data processing / LLM token streams
```

## Checklist

- [x] Classes / objects
- [x] `self`
- [x] inheritance vs composition
- [x] `@property`
- [x] decorator definition and mechanics
- [x] `@decorator` syntax
- [x] `*args` / `**kwargs` in wrappers
- [x] `functools.wraps`
- [x] FastAPI decorator connection
- [x] dataclasses
- [x] `default_factory`
- [x] `frozen=True`
- [x] Pydantic vs dataclass
- [x] context managers
- [x] `__enter__` / `__exit__`
- [x] `__aenter__` / `__aexit__`
- [x] `contextlib.contextmanager`
- [x] generators / `yield`
- [x] async generators
- [x] project-based interview framing
