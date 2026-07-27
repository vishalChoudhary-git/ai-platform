from enum import StrEnum


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentSource(StrEnum):
    UPLOAD = "upload"
    GITHUB = "github"
    NOTION = "notion"
    FINANCE = "finance"
    SHAREPOINT = "sharepoint"
