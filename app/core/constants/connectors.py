from enum import StrEnum


class ConnectorName(StrEnum):
    UPLOAD = "upload"
    GITHUB = "github"
    NOTION = "notion"
    SHAREPOINT = "sharepoint"
    FINANCE = "finance"
