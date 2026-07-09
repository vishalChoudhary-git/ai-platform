from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies.company import get_company_service
from app.schemas.common import PaginationParams
from app.schemas.company import CompanyCreate, CompanyResponse
from app.services.company_service import CompanyService

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("/", response_model=list[CompanyResponse])
async def get_companies(
    pagination: Annotated[
        PaginationParams,
        Depends(),
    ],
    service: CompanyService = Depends(get_company_service),
    sector: str | None = None,
):
    return await service.get_all(
        pagination.page,
        pagination.size,
        sector,
    )


@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    request: CompanyCreate,
    service: CompanyService = Depends(get_company_service),
):
    return await service.create(request)
