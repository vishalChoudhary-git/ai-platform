# Topic 7 — Python OOP, Decorators, Generators & Context Managers

**Status:** Planned

## Focus
Classes, inheritance vs composition, `@property`, decorators, generators/`yield`, context managers, `with`, dataclasses, and clean object-oriented design.

## New interview feedback
The interviewer explicitly asked deep questions around:

- decorators
- dataclasses
- context managers

These are now **high-priority revision areas** rather than optional Python trivia.

## Interview outcomes
Recognize, explain, and write the common production Python patterns used in AI/backend services. Connect each concept to the actual `ai-platform` codebase where applicable.

## Priority questions to prepare

### What is a decorator?
Explain that a decorator is a callable that takes a function/class and returns a modified or wrapped callable, commonly using `@decorator` syntax. Know why decorators are useful for cross-cutting concerns such as logging, timing, authorization, caching, retries, and instrumentation.

### What is a dataclass?
Explain that `@dataclass` generates common methods such as `__init__` and `__repr__` for data-focused classes. Know when a dataclass is preferable to a manually written container and how it differs from Pydantic when runtime validation is required.

### What is a context manager?
Explain the resource-lifecycle pattern behind `with`, including `__enter__`/`__exit__` and why it is useful for files, locks, database transactions, and client/resource cleanup. Also recognize `contextlib.contextmanager`.

## Project connection
For each concept we will identify a real or natural application in `ai-platform`, such as request instrumentation, resource lifecycle management, configuration/data models, and service abstractions. We should avoid inventing usage that is not actually in the repository.

## Notes
Content will be added as we complete this topic.
