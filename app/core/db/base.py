from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can discover them.
import app.features.knowledge_base.models  # noqa: F401, E402
