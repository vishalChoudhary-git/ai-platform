from enum import StrEnum


class ExpenseStatus(StrEnum):
    SUBMITTED = "submitted"
    INFORMATION_REQUIRED = "information_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_REQUIRED = "review_required"
