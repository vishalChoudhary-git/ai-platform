from fastapi import APIRouter, Depends, status

from app.features.expenses.schemas import ExpenseCreateRequest, ExpenseResponse
from app.features.expenses.services import ExpenseService

from .dependencies import get_expense_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    request: ExpenseCreateRequest,
    service: ExpenseService = Depends(get_expense_service),
) -> ExpenseResponse:
    return await service.create(request)
