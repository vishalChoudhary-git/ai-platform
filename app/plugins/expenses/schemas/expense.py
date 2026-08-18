from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ExpenseCreateData(BaseModel):
    employee_name: str = Field(min_length=1, max_length=255)
    employee_email: str = Field(min_length=3, max_length=320)
    manager_email: str = Field(min_length=3, max_length=320)
    category: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    expense_date: date | None = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class ExpenseUpdateData(BaseModel):
    employee_name: str | None = Field(default=None, min_length=1, max_length=255)
    employee_email: str | None = Field(default=None, min_length=3, max_length=320)
    manager_email: str | None = Field(default=None, min_length=3, max_length=320)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1)
    amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    expense_date: date | None = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.upper() if value else value
