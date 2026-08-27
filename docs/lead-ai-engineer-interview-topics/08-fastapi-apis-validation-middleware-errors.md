# Topic 8 — FastAPI: APIs, Validation, Middleware & Error Handling

**Status:** Complete

## Focus
Routes, request/response models, dependency injection, async endpoints, middleware, exception handlers, authentication, health checks and OpenAPI.

## Interview outcomes
Build and explain a production-ready AI service API.

## Core flow

```text
HTTP Request
     ↓
FastAPI Router
     ↓
Validation / Dependency Injection
     ↓
Service
     ↓
Repository / Provider
     ↓
Response Model
     ↓
HTTP Response
```

## Path parameter vs query parameter vs body

### Path parameter
Use a path parameter when the value identifies the resource.

```python
@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    ...
```

Request:

```text
GET /documents/doc123
```

Mental model: **which resource?**

### Query parameter
Use query parameters for filtering, pagination, sorting, search options or other optional behavior.

```python
@router.get("/documents")
async def get_documents(
    page: int = 1,
    size: int = 20,
    source: str | None = None,
):
    ...
```

Request:

```text
GET /documents?page=2&size=20&source=upload
```

Mental model: **how do I want the resources?**

### Request body
Use the body for the actual structured payload, commonly represented with a Pydantic model.

```python
class DocumentCreate(BaseModel):
    filename: str
    source: str

@router.post("/documents")
async def create_document(request: DocumentCreate):
    ...
```

Mental model:

```text
Path  → resource identity
Query → filtering/options/pagination
Body  → structured payload
```

## Project connection — document upload

Our actual document router uses `@router.post("/upload")`, `UploadFile = File(...)`, `Depends(...)`, a response model, and `BackgroundTasks`. The request is converted into a `RawDocument`, passed to the document service, then a background task starts the ingestion processing. This provides a concrete example of FastAPI decorators, dependency injection, file input, response models and deferred work in one endpoint.

## `Depends()` and dependency injection

The application uses FastAPI dependencies to construct repositories, storage providers and services. The dependency layer passes `DocumentRepository` and `StorageProvider` into `DocumentService`, and similarly wires `IngestionService` dependencies.

```text
Request
  ↓
FastAPI dependency graph
  ├── repository
  ├── storage provider
  └── service
```

The route/service does not need to manually construct every infrastructure dependency.

## Pydantic + FastAPI

FastAPI can use Pydantic models to validate request bodies and define response contracts.

```python
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search")
async def search(request: SearchRequest):
    ...
```

For Pydantic-specific details, revise Topic 3.

## Response models

```python
@router.post("/upload", response_model=UploadResponse)
```

Response models provide predictable contracts, serialization/validation behavior and API schema documentation.

## HTTP status codes to know

```text
200 → success
201 → created
204 → success with no response body
400 → bad request
401 → unauthenticated
403 → forbidden
404 → not found
409 → conflict
422 → validation failure
429 → rate limited
500 → server error
```

## Middleware

Middleware wraps request/response handling and is appropriate for cross-cutting concerns such as:

- request IDs
- logging
- timing
- CORS
- authentication/authorization hooks
- metrics
- tracing

Mental model:

```text
Request
  ↓
Middleware
  ↓
Route
  ↓
Service
  ↓
Response
  ↑
Middleware
```

## Authentication vs authorization

**Authentication:** who are you?

**Authorization:** are you allowed to perform this action or access this resource?

For a multi-tenant RAG platform, authorization must be enforced when determining which documents/chunks a caller is allowed to retrieve.

## BackgroundTasks

Our upload route adds `ingestion_service.process_document` as a background task after the document is ingested. This is useful for lightweight deferred work. For durable, long-running or high-scale ingestion, use a queue/worker architecture with retries, idempotency and failure handling rather than relying only on an in-process background task.

## Error handling

Prefer consistent application errors instead of exposing raw infrastructure exceptions.

```text
Database/API error
      ↓
service/application error boundary
      ↓
FastAPI exception handler
      ↓
consistent HTTP response
```

## Likely interview questions

### Path parameter vs query parameter?

> A path parameter identifies the resource, while query parameters normally control filtering, pagination, sorting, searching or optional behavior.

### Why not always use query parameters?

> For a specific resource, the path communicates resource identity more clearly and follows conventional REST resource modeling.

### What is `Depends()`?

> FastAPI's dependency injection mechanism. It lets endpoints declare dependencies while FastAPI resolves and supplies them, which improves separation, reuse and testability.

### Why use Pydantic with FastAPI?

> Pydantic provides runtime parsing and validation for structured request/response data, while FastAPI uses those models to build API contracts and schema documentation.

### Why use response models?

> They make the response contract explicit, validate/serialize output and help generate accurate API documentation.

### What is middleware?

> Middleware runs around request processing and is best for cross-cutting concerns that should apply consistently across routes.

### How would you handle long-running document ingestion?

> I would return an initial accepted/status response and move long-running work to a durable background worker/queue so retries, scaling and failures can be handled independently of the HTTP request.

## Additional interview question bank

### Message broker vs WebSocket — what is the difference and when would you use each?

**Message broker:** asynchronous service-to-service communication through a durable or buffered messaging system. Use it for background jobs, event-driven workflows, decoupling producers/consumers, retries and workload distribution.

**WebSocket:** a persistent bidirectional client-server connection. Use it when the client needs real-time interactive updates, such as live collaboration, notifications, agent progress or token/status streaming.

Key distinction:

```text
Message broker
→ backend-to-backend asynchronous messaging
→ decoupling / durability / buffering

WebSocket
→ client-to-server persistent real-time channel
→ low-latency interactive updates
```

They solve different problems and can be used together. For example, an AI ingestion worker may communicate through a broker while the frontend receives live job status through WebSocket/SSE.

## Checklist

- [x] path parameters
- [x] query parameters
- [x] request body
- [x] Pydantic integration
- [x] `Depends()`
- [x] async routes
- [x] response models
- [x] middleware concept
- [x] HTTP status codes
- [x] authentication vs authorization
- [x] background task concept
- [x] error-handling architecture
- [x] message broker vs WebSocket
