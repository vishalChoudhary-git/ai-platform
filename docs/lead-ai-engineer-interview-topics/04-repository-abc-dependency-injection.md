# Topic 4 — Repository Pattern, ABC & Dependency Injection

**Status:** Complete

## Focus
Abstract base classes, repository interfaces, dependency inversion, constructor injection, mocks and persistence boundaries.

## Completed
- ABC and `abstractmethod`
- abstraction/contracts
- Repository pattern
- dependency inversion
- constructor dependency injection
- FastAPI dependency wiring
- project examples using `StorageProvider`, `RetrievalRepository`, `EmbeddingProvider`, and `Reranker`
- testability through replaceable implementations

## Project-connected examples

### `StorageProvider`

`ai-platform` defines a storage abstraction and keeps vendor-specific storage code behind it.

```text
Document/Ingestion Service
        ↓
   StorageProvider
        ↓
CloudflareR2StorageProvider
        ↓
    Cloudflare R2
```

### Dependency Injection

FastAPI dependency functions provide repositories/providers and pass them into services instead of services constructing infrastructure dependencies themselves.

```text
FastAPI dependency layer
        ↓
DocumentService(repository, storage)
```

### Retrieval service

Our retrieval service receives `RetrievalRepository`, `EmbeddingProvider`, and an optional `Reranker` through its constructor.

```text
RetrievalService
   ├── RetrievalRepository
   ├── EmbeddingProvider
   └── Reranker | None
```

## Key distinctions

```text
ABC / interface
    → defines a contract

Dependency Injection
    → supplies an implementation

Repository pattern
    → abstracts persistence/data access

Service
    → application/business orchestration
```

## Interview questions

### Why use an abstraction?

> To isolate a responsibility or infrastructure boundary so the consuming service is not tightly coupled to one implementation.

### Why dependency injection?

> It separates object construction from business logic, reduces coupling, and makes implementations replaceable and testable.

### Repository vs service?

> A repository owns persistence/data access. A service owns application/business orchestration.

### Is abstraction always necessary?

> No. It is valuable when there is a real responsibility boundary, implementation variability, or a meaningful testing/replacement seam. Over-abstraction creates unnecessary complexity.

## Revision checklist

- [x] `ABC`
- [x] `abstractmethod`
- [x] repository abstraction
- [x] dependency inversion
- [x] constructor injection
- [x] FastAPI dependency injection
- [x] project example: `StorageProvider`
- [x] project example: `RetrievalRepository`
- [x] project example: `Reranker`
- [x] testability / mocks concept
