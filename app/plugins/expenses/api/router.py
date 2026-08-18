import json
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from app.features.documents.api.dependencies import get_ingestion_service
from app.features.documents.services import IngestionService
from app.plugins.expenses.schemas import (
    ExpenseCreateData,
    ExpenseResponse,
    ExpenseUpdateData,
)
from app.plugins.expenses.services import ExpenseService

from .dependencies import get_expense_service

router = APIRouter(
    prefix="/plugins/expenses",
    tags=["expenses"],
)


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_expense(
    background_tasks: BackgroundTasks,
    expense_id: Annotated[str | None, Query()] = None,
    expense: Annotated[str | None, Form()] = None,
    files: Annotated[list[UploadFile], File()] = [],
    service: ExpenseService = Depends(get_expense_service),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
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

    for document_id in document_ids:
        background_tasks.add_task(
            ingestion_service.process_document,
            document_id,
        )

    return result
