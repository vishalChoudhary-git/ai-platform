import json
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from app.plugins.expenses.schemas import (
    ExpenseApprovalDecision,
    ExpenseCreateData,
    ExpenseResponse,
    ExpenseUpdateData,
)
from app.plugins.expenses.services import ExpenseApprovalService, ExpenseService

from ..evidence.background import process_expense_documents_in_background
from ..policy.api import router as policy_router
from .dependencies import get_expense_approval_service, get_expense_service

router = APIRouter(
    prefix="/plugins/expenses",
)
router.include_router(policy_router)


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["expenses"],
)
async def submit_expense(
    background_tasks: BackgroundTasks,
    expense_id: Annotated[str | None, Query()] = None,
    expense: Annotated[str | None, Form()] = None,
    files: Annotated[list[UploadFile], File()] = [],
    service: ExpenseService = Depends(get_expense_service),
) -> ExpenseResponse:
    try:
        data = json.loads(expense) if expense else None
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expense form field must contain valid JSON.",
        ) from exc

    if expense_id:
        update_data = ExpenseUpdateData.model_validate(data) if data else None
        result, document_ids = await service.append(
            expense_id=expense_id,
            files=files,
            data=update_data,
        )
    else:
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Expense form field is required when creating an expense.",
            )
        create_data = ExpenseCreateData.model_validate(data)
        result, document_ids = await service.create(
            data=create_data,
            files=files,
        )

    if document_ids:
        background_tasks.add_task(
            process_expense_documents_in_background,
            result.expense_id,
            document_ids,
        )

    return result


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    tags=["expenses"],
)
async def get_expense_status(
    expense_id: str,
    service: ExpenseService = Depends(get_expense_service),
) -> ExpenseResponse:
    return await service.get_by_business_id(expense_id)


@router.post(
    "/{expense_id}/approval",
    response_model=ExpenseResponse,
    tags=["expenses"],
)
async def decide_expense_approval(
    expense_id: str,
    decision: ExpenseApprovalDecision,
    approver_email: Annotated[str, Header(alias="X-Debug-User-Email")],
    service: ExpenseApprovalService = Depends(get_expense_approval_service),
) -> ExpenseResponse:
    if not approver_email.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Debug-User-Email is required for temporary manager authorization.",
        )

    try:
        expense = await service.decide(
            expense_id=expense_id,
            approver_email=approver_email.strip().lower(),
            decision=decision,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ExpenseResponse.model_validate(expense)
