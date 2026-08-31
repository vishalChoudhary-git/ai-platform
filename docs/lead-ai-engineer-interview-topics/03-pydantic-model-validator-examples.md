# Pydantic Model-Level Validators — Interview Examples

## Why `model_validator`?

Use a **model-level validator** when validation depends on multiple fields together.

```text
field_validator
→ validates one field

model_validator
→ validates the relationship between multiple fields
```

In Pydantic v2, `model_validator` supports modes such as `before` and `after`.

---

## Example 1 — `mode="after"`

### Requirement

The model contains `start_date` and `end_date`.

The rule is:

```text
start_date < end_date
```

Because we want to validate the already-parsed model values, use `mode="after"`.

```python
from datetime import date
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self
```

Example:

```python
DateRange(
    start_date=date(2026, 8, 1),
    end_date=date(2026, 8, 10),
)
```

Valid because:

```text
August 1 < August 10
```

Invalid:

```python
DateRange(
    start_date=date(2026, 8, 10),
    end_date=date(2026, 8, 1),
)
```

### Interview answer

> "I would use a model-level validator because the rule depends on both dates. With `mode='after'`, Pydantic has already parsed the fields into their expected types, so I can compare the `date` values directly."

---

## Example 2 — `mode="before"`

### Requirement

We receive:

```text
price
quantity
total_price (optional)
```

If `total_price` is missing, calculate it:

```text
price × quantity
```

This is a good use case for `mode="before"` because we want to modify/prepare the raw input **before normal model validation happens**.

```python
from pydantic import BaseModel, model_validator

class Order(BaseModel):
    price: float
    quantity: int
    total_price: float | None = None

    @model_validator(mode="before")
    @classmethod
    def calculate_total_price(cls, values):
        if isinstance(values, dict):
            if values.get("total_price") is None:
                values["total_price"] = values["price"] * values["quantity"]
        return values
```

Input:

```python
order = Order(
    price=100,
    quantity=3,
)
```

Result:

```text
price       = 100
quantity    = 3
total_price = 300
```

If the caller provides `total_price`, the validator can preserve the supplied value.

```python
order = Order(
    price=100,
    quantity=3,
    total_price=280,
)
```

Result:

```text
total_price = 280
```

### Interview answer

> "I would use `mode='before'` when I need to transform or enrich the raw input before Pydantic validates the model. Here, `total_price` is optional, so I can calculate it from `price` and `quantity` before normal field validation."

---

## `before` vs `after` — remember this

```text
mode="before"

Raw input
   ↓
model_validator
   ↓
Pydantic parsing/validation
   ↓
Model
```

Use it for:

- preprocessing raw input
- filling/calculating missing values
- transforming input shape
- handling different input formats

```text
mode="after"

Raw input
   ↓
Pydantic parsing/validation
   ↓
Validated Model
   ↓
model_validator
```

Use it for:

- cross-field validation
- business relationships between already-typed values
- final consistency checks

---

## Important interview distinction

### `field_validator` vs `model_validator`

```text
field_validator("price")
→ Is price valid by itself?

model_validator(...)
→ Is price × quantity consistent with total_price?
```

A simple rule such as:

```text
price > 0
```

belongs naturally to a field validator or `Field(gt=0)`.

A relationship such as:

```text
start_date < end_date
```

belongs naturally to a model-level validator.
