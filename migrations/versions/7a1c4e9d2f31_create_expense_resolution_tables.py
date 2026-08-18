"""create expense resolution workflow schema

Revision ID: 7a1c4e9d2f31
Revises: e368cc50222a
Create Date: 2026-08-18 08:48:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "7a1c4e9d2f31"
down_revision: str | Sequence[str] | None = "e368cc50222a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


expense_status = postgresql.ENUM(
    "submitted",
    "information_required",
    "approved",
    name="expense_status",
    create_type=False,
)
expense_required_action = postgresql.ENUM(
    "none",
    "additional_information",
    "additional_document",
    "manager_decision",
    name="expense_required_action",
    create_type=False,
)
expense_document_role = postgresql.ENUM(
    "receipt",
    "supporting",
    name="expense_document_role",
    create_type=False,
)
expense_approval_status = postgresql.ENUM(
    "pending",
    "approved",
    "rejected",
    name="expense_approval_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    expense_status.create(bind, checkfirst=True)
    expense_required_action.create(bind, checkfirst=True)
    expense_document_role.create(bind, checkfirst=True)
    expense_approval_status.create(bind, checkfirst=True)

    op.create_table(
        "expenses",
        sa.Column("expense_id", sa.String(length=32), nullable=False),
        sa.Column("employee_name", sa.String(length=255), nullable=False),
        sa.Column("employee_email", sa.String(length=320), nullable=False),
        sa.Column("manager_email", sa.String(length=320), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=True),
        sa.Column("status", expense_status, server_default="submitted", nullable=False),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column(
            "required_action",
            expense_required_action,
            server_default="none",
            nullable=False,
        ),
        sa.Column(
            "decision_evidence",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_expenses_expense_id"),
        "expenses",
        ["expense_id"],
        unique=True,
    )

    op.create_table(
        "expense_documents",
        sa.Column("expense_id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column(
            "role",
            expense_document_role,
            server_default="receipt",
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["expense_id"],
            ["expenses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "expense_id",
            "document_id",
            name="uq_expense_document",
        ),
    )
    op.create_index(
        op.f("ix_expense_documents_document_id"),
        "expense_documents",
        ["document_id"],
    )
    op.create_index(
        op.f("ix_expense_documents_expense_id"),
        "expense_documents",
        ["expense_id"],
    )

    op.create_table(
        "expense_approvals",
        sa.Column("expense_id", sa.UUID(), nullable=False),
        sa.Column("approver_email", sa.String(length=320), nullable=False),
        sa.Column(
            "status",
            expense_approval_status,
            server_default="pending",
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["expense_id"],
            ["expenses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_expense_approvals_expense_id"),
        "expense_approvals",
        ["expense_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_expense_approvals_expense_id"),
        table_name="expense_approvals",
    )
    op.drop_table("expense_approvals")
    op.drop_index(
        op.f("ix_expense_documents_expense_id"),
        table_name="expense_documents",
    )
    op.drop_index(
        op.f("ix_expense_documents_document_id"),
        table_name="expense_documents",
    )
    op.drop_table("expense_documents")
    op.drop_index(
        op.f("ix_expenses_expense_id"),
        table_name="expenses",
    )
    op.drop_table("expenses")

    bind = op.get_bind()
    expense_approval_status.drop(bind, checkfirst=True)
    expense_document_role.drop(bind, checkfirst=True)
    expense_required_action.drop(bind, checkfirst=True)
    expense_status.drop(bind, checkfirst=True)
