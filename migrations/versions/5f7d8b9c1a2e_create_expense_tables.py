"""create expense tables

Revision ID: 5f7d8b9c1a2e
Revises: e368cc50222a
Create Date: 2026-08-17 21:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5f7d8b9c1a2e"
down_revision: str | Sequence[str] | None = "e368cc50222a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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
        sa.Column(
            "status",
            postgresql.ENUM(
                "submitted",
                "information_required",
                "approved",
                "rejected",
                "review_required",
                name="expense_status",
            ),
            server_default="submitted",
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_expenses_expense_id"), "expenses", ["expense_id"], unique=True)

    op.create_table(
        "expense_documents",
        sa.Column("expense_id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
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
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_expense_documents_document_id"),
        "expense_documents",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_expense_documents_expense_id"),
        "expense_documents",
        ["expense_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_expense_documents_expense_id"), table_name="expense_documents")
    op.drop_index(op.f("ix_expense_documents_document_id"), table_name="expense_documents")
    op.drop_table("expense_documents")
    op.drop_index(op.f("ix_expenses_expense_id"), table_name="expenses")
    op.drop_table("expenses")
    postgresql.ENUM(name="expense_status").drop(op.get_bind(), checkfirst=True)
