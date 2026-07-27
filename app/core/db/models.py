from app.core.db.base import Base
from app.core.db.mixins import TimestampMixin, UUIDMixin


class BaseModel(UUIDMixin, TimestampMixin, Base):
    __abstract__ = True
