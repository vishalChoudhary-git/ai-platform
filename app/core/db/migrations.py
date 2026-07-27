"""
Import every SQLAlchemy model here.

Alembic imports this file to discover metadata.
"""

from app.features.documents.models import Document

__all__ = [
    "Document",
]
