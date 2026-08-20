from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import Base
from app.core.db.mixins import TimestampMixin, UUIDMixin

from .enums import ExpensePolicyStatus


class ExpensePolicy(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "expense_policies"

    policy_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )
    policy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    document_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[ExpensePolicyStatus] = mapped_column(
        postgresql.ENUM(
            ExpensePolicyStatus,
            name="expense_policy_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ExpensePolicyStatus.UPLOADED,
        server_default=ExpensePolicyStatus.UPLOADED.value,
        nullable=False,
    )
    published_by: Mapped[str] = mapped_column(String(320), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "policy_name",
            "version",
            name="uq_expense_policy_name_version",
        ),
    )
