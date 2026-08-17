from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import Base
from app.core.db.mixins import TimestampMixin, UUIDMixin

from .enums import ExpenseStatus


class Expense(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "expenses"

    expense_id: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    employee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_email: Mapped[str] = mapped_column(String(320), nullable=False)
    manager_email: Mapped[str] = mapped_column(String(320), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    expense_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[ExpenseStatus] = mapped_column(
        postgresql.ENUM(
            ExpenseStatus,
            name="expense_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ExpenseStatus.SUBMITTED,
        server_default=ExpenseStatus.SUBMITTED.value,
        nullable=False,
    )

    documents: Mapped[list["ExpenseDocument"]] = relationship(
        back_populates="expense",
        cascade="all, delete-orphan",
    )


class ExpenseDocument(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "expense_documents"

    expense_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("expenses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    expense: Mapped[Expense] = relationship(back_populates="documents")
