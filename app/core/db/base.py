from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can discover them.
import app.features.documents.models  # noqa: F401, E402
import app.plugins.expenses.models  # noqa: F401, E402
