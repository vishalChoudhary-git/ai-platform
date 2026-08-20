from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.auth.dependencies import require_role
from app.core.auth.models import AuthenticatedUser

from .dependencies import get_policy_service
from .schemas import ExpensePolicyResponse
from .service import ExpensePolicyService

router = APIRouter(prefix="/plugins/expenses/policies", tags=["expense-policies"])


@router.post("", response_model=ExpensePolicyResponse, status_code=status.HTTP_201_CREATED)
async def upload_policy(
    policy_name: Annotated[str, Form()],
    version: Annotated[str, Form()],
    effective_from: Annotated[str | None, Form()] = None,
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(require_role("HR")),
    service: ExpensePolicyService = Depends(get_policy_service),
) -> ExpensePolicyResponse:
    try:
        parsed_effective_from = (
            __import__("datetime").date.fromisoformat(effective_from)
            if effective_from
            else None
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="effective_from must be YYYY-MM-DD") from exc

    policy = await service.create(
        policy_name=policy_name,
        version=version,
        effective_from=parsed_effective_from,
        published_by=current_user.email,
        content=await file.read(),
        filename=file.filename or "policy.pdf",
        mime_type=file.content_type or "application/octet-stream",
    )
    return ExpensePolicyResponse(
        policy_id=policy.policy_id,
        policy_name=policy.policy_name,
        version=policy.version,
        document_id=str(policy.document_id),
        checksum=policy.checksum,
        effective_from=policy.effective_from,
        status=policy.status,
        published_by=policy.published_by,
        published_at=policy.published_at,
    )
