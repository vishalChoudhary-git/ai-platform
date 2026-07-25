"""
Import every SQLAlchemy model here.

Alembic imports this file to discover metadata.
"""

from app.features.documents.models.company import Company

__all__ = [
    "Company",
]
