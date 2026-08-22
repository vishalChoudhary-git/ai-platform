from enum import StrEnum


class ExpenseStatus(StrEnum):
    SUBMITTED = "submitted"
    INFORMATION_REQUIRED = "information_required"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExpenseRequiredAction(StrEnum):
    NONE = "none"
    ADDITIONAL_INFORMATION = "additional_information"
    ADDITIONAL_DOCUMENT = "additional_document"
    MANAGER_DECISION = "manager_decision"


class ExpenseDocumentRole(StrEnum):
    RECEIPT = "receipt"
    SUPPORTING = "supporting"


class ExpenseApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
