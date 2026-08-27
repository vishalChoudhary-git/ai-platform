# Topic 3 — Pydantic Models, Validation & Type Safety

**Status:** Complete

## Focus
Pydantic `BaseModel`, field validation, enums, nested models, serialization, request/response models, configuration and structured LLM outputs.

## Completed
- `BaseModel`
- typed fields and defaults
- `Field()` metadata and constraints
- `field_validator`
- model-level validation concept
- Enum-based constrained values
- `str | None`
- nested models
- request/response modeling
- runtime validation vs Python type hints
- Pydantic vs dataclasses
- structured AI/application output modeling
- common API-boundary use cases

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

### `Field()` — field metadata and declarative constraints

Use `Field()` when you want to describe a field more precisely than a bare type annotation.

```python
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=100)
```

Typical uses of `Field()`:

- minimum/maximum numeric constraints
- string length constraints
- defaults and default factories
- descriptions/examples for API schema/documentation
- aliases and field configuration

Mental model:

```text
Type annotation
    → what type is expected?

Field(...)
    → what declarative constraints/metadata apply to this field?
```

### `field_validator` — custom field-level rules

Use `field_validator` when a rule cannot be expressed cleanly with the type/field constraints alone.

```python
from pydantic import BaseModel, field_validator

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query cannot be empty")
        return value
```

Another example:

```python
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

Mental model:

```text
Field()
   → declarative/simple constraints + metadata

field_validator()
   → custom validation logic for one field
```

### Model-level validation

When a rule depends on multiple fields together, use model-level validation rather than forcing the rule into a single field validator.

Example concept:

```text
start_date < end_date
password == password_confirmation
search_type == hybrid → keyword configuration required
```

The exact Pydantic API can vary by version, so the important interview concept is **cross-field validation**.

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
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    search_type: SearchType = SearchType.HYBRID
    document_ids: list[str] | None = None
```

Structured application/LLM output can also be represented explicitly:

```python
class Answer(BaseModel):
    answer: str
    citations: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
```

## Different Pydantic use cases

### 1. API request models

Validate incoming request bodies.

```python
class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
```

### 2. API response models

Define and validate the shape returned by an endpoint.

```python
class SearchResponse(BaseModel):
    results: list[str]
    total: int
```

### 3. Field constraints with `Field()`

Use declarative rules for simple constraints and API schema metadata.

```python
score: float = Field(ge=0.0, le=1.0)
name: str = Field(min_length=1, max_length=200)
```

### 4. Custom field validation with `field_validator`

Use application-specific rules for a single field.

```text
normalize a query
validate a provider name
reject an empty identifier
validate a range with custom logic
```

### 5. Cross-field/model validation

Use when the validity of one field depends on another field.

```text
if search_type == hybrid:
    keyword settings must be present
```

### 6. Nested/domain models

Represent structured internal data cleanly.

```text
ChatRequest
   └── UserContext
```

### 7. Configuration/settings

Pydantic models can be used to parse and validate application configuration/environment values.

Typical checks include required settings, URLs, numeric limits and environment-specific configuration.

### 8. Structured LLM/tool outputs

Instead of trusting arbitrary JSON from an LLM/tool call, map it into a typed model and validate the expected shape.

```text
LLM output
   ↓
Pydantic model
   ↓
validated structured object
   ↓
downstream business logic
```

### 9. External service boundaries

Pydantic is useful when data comes from APIs, connectors or other services and needs to become a stable internal representation.

### 10. Serialization / schema generation

Pydantic models can be serialized back to dictionaries/JSON and are commonly used to produce API schemas and OpenAPI-compatible contracts.

## Key interview distinctions

**Pydantic vs type hints:** type hints describe expected types and help static analysis; Pydantic performs runtime parsing/validation.

**Pydantic vs dataclass:** dataclasses are primarily convenient data containers; Pydantic is designed for data parsing and validation.

**`Field()` vs `field_validator`:** use `Field()` for declarative constraints and metadata; use `field_validator` for custom logic around a specific field.

**Field validator vs model validator:** use a field validator for one field; use model-level validation when correctness depends on multiple fields.

**Where to validate:** validate external/untrusted data at the application boundary, then pass trusted structured models internally.

**What validation does not solve:** authorization, security, database constraints, business authorization rules and downstream failure handling still matter.

## Interview questions

### Why Pydantic if Python already has type hints?

> Type hints communicate intent, while Pydantic provides runtime validation and parsing of actual input.

### Where would you use Pydantic in an AI platform?

> API requests/responses, configuration, service boundaries, structured tool/LLM outputs and other external data boundaries.

### When would you use `Field()` instead of `field_validator`?

> I would use `Field()` for straightforward declarative constraints and schema metadata, such as `ge`, `le`, `min_length` or a description. I would use `field_validator` when I need custom validation or normalization logic.

### When would you use model-level validation?

> When the validity of the object depends on a relationship between multiple fields rather than on one field in isolation.

## Checklist

- [x] `BaseModel`
- [x] typed fields and defaults
- [x] `Field()` constraints/metadata
- [x] `field_validator`
- [x] model-level validation concept
- [x] Enum
- [x] optional fields
- [x] nested models
- [x] request/response models
- [x] configuration
- [x] structured output models
- [x] serialization/schema concept
- [x] Pydantic vs type hints
- [x] Pydantic vs dataclass
