from enum import StrEnum


class ExpensePolicyStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PUBLISHED = "published"
    ARCHIVED = "archived"
