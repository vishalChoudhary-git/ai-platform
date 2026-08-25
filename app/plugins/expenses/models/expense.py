from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import Base
from app.core.db.mixins import TimestampMixin, UUIDMixin

from .enums import (
    ExpenseApprovalStatus,
    ExpenseDocumentRole,
    ExpenseRequiredAction,
    ExpenseStatus,
)


class Expense(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "expenses"

    expense_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )
    employee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_email: Mapped[str] = mapped_column(String(320), nullable=False)
    manager_email: Mapped[str] = mapped_column(String(320), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )
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
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_action: Mapped[ExpenseRequiredAction] = mapped_column(
        postgresql.ENUM(
            ExpenseRequiredAction,
            name="expense_required_action",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ExpenseRequiredAction.NONE,
        server_default=ExpenseRequiredAction.NONE.value,
        nullable=False,
    )
    decision_evidence: Mapped[list[dict[str, Any]] | None] = mapped_column(
        postgresql.JSONB,
        nullable=True,
    )

    documents: Mapped[list["ExpenseDocument"]] = relationship(
        back_populates="expense",
        cascade="all, delete-orphan",
    )
    approvals: Mapped[list["ExpenseApproval"]] = relationship(
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
    role: Mapped[ExpenseDocumentRole] = mapped_column(
        postgresql.ENUM(
            ExpenseDocumentRole,
            name="expense_document_role",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ExpenseDocumentRole.RECEIPT,
        server_default=ExpenseDocumentRole.RECEIPT.value,
        nullable=False,
    )

    expense: Mapped[Expense] = relationship(back_populates="documents")

    __table_args__ = (
        UniqueConstraint(
            "expense_id",
            "document_id",
            name="uq_expense_document",
        ),
    )


class ExpenseApproval(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "expense_approvals"

    expense_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("expenses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approver_email: Mapped[str] = mapped_column(String(320), nullable=False)
    status: Mapped[ExpenseApprovalStatus] = mapped_column(
        postgresql.ENUM(
            ExpenseApprovalStatus,
            name="expense_approval_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ExpenseApprovalStatus.PENDING,
        server_default=ExpenseApprovalStatus.PENDING.value,
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    expense: Mapped[Expense] = relationship(back_populates="approvals")
