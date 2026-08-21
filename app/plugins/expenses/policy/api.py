from datetime import date

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.core.auth.dependencies import require_role
from app.core.auth.models import AuthenticatedUser

from .background import process_policy_in_background
from .dependencies import get_policy_service
from .schemas import ExpensePolicyResponse
from .service import ExpensePolicyService

router = APIRouter(prefix="/policies", tags=["expense-policies"])


@router.post(
    "",
    response_model=ExpensePolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_policy(
    background_tasks: BackgroundTasks,
    policy_name: str = Form(...),
    version: str = Form(...),
    effective_from: str | None = Form(default=None),
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(require_role("HR")),
    service: ExpensePolicyService = Depends(get_policy_service),
) -> ExpensePolicyResponse:
    try:
        parsed_effective_from = date.fromisoformat(effective_from) if effective_from else None
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="effective_from must be YYYY-MM-DD",
        ) from exc

    try:
        policy = await service.create(
            policy_name=policy_name,
            version=version,
            effective_from=parsed_effective_from,
            published_by=current_user.email,
            content=await file.read(),
            filename=file.filename or "policy.pdf",
            mime_type=file.content_type or "application/octet-stream",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    background_tasks.add_task(process_policy_in_background, policy.policy_id)

    return ExpensePolicyResponse.model_validate(policy)
