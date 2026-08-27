# Topic 3 — Pydantic Models, Validation & Type Safety

**Status:** Complete

## Focus
Pydantic `BaseModel`, field validation, enums, nested models, serialization, request/response models, configuration and structured LLM outputs.

## Completed
- `BaseModel`
- typed fields and defaults
- `field_validator`
- Enum-based constrained values
- `str | None`
- nested models
- request/response modeling
- runtime validation vs Python type hints
- Pydantic vs dataclasses
- structured AI/application output modeling

## Revision notes

### Mental model

```text
Raw / untrusted input
        ↓
     Pydantic
        ↓
Validated Python model
        ↓
Service / business logic
```

### Basic model

```python
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
```

### Validation

Use `field_validator` when business constraints go beyond basic typing.

```python
from pydantic import BaseModel, field_validator

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, value: int) -> int:
        if value <= 0 or value > 100:
            raise ValueError("top_k must be between 1 and 100")
        return value
```

### Enum

```python
from enum import Enum

class SearchType(str, Enum):
    VECTOR = "vector"
    HYBRID = "hybrid"
```

### Nested models

```python
class UserContext(BaseModel):
    user_id: str
    tenant_id: str

class ChatRequest(BaseModel):
    query: str
    context: UserContext
```

### Optional values

```python
document_id: str | None = None
```

### AI application example

```python
class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    search_type: SearchType = SearchType.HYBRID
    document_ids: list[str] | None = None
```

Structured application/LLM output can also be represented explicitly:

```python
class Answer(BaseModel):
    answer: str
    citations: list[str]
    confidence: float
```

## Key interview distinctions

**Pydantic vs type hints:** type hints describe expected types and help static analysis; Pydantic performs runtime parsing/validation.

**Pydantic vs dataclass:** dataclasses are primarily convenient data containers; Pydantic is designed for data parsing and validation.

**Where to validate:** validate external/untrusted data at the application boundary, then pass trusted structured models internally.

**What validation does not solve:** authorization, security, database constraints, business authorization rules and downstream failure handling still matter.

## Interview questions

### Why Pydantic if Python already has type hints?

> Type hints communicate intent, while Pydantic provides runtime validation and parsing of actual input.

### Where would you use Pydantic in an AI platform?

> API requests/responses, configuration, service boundaries, structured tool/LLM outputs and other external data boundaries.

## Checklist

- [x] `BaseModel`
- [x] typed fields and defaults
- [x] `field_validator`
- [x] Enum
- [x] optional fields
- [x] nested models
- [x] request/response models
- [x] structured output models
- [x] Pydantic vs type hints
- [x] Pydantic vs dataclass
