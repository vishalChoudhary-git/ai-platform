from fastapi import APIRouter, Depends, File, UploadFile

from app.core.ingestion.types import RawDocument
from app.features.documents.models.enums import (
    DocumentSource,
)
from app.features.documents.schemas.upload import (
    UploadResponse,
)
from app.features.documents.services import (
    DocumentService,
)

from .dependencies import get_document_service

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=UploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(
        get_document_service,
    ),
):
    raw_document = RawDocument(
        content=await file.read(),
        filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        source=DocumentSource.UPLOAD,
        metadata={},
    )

    document = await service.ingest(raw_document)

    return UploadResponse.model_validate(document)


# @router.get("/", response_model=list[CompanyResponse])
# async def get_companies(
#     pagination: Annotated[
#         PaginationParams,
#         Depends(),
#     ],
#     service: CompanyService = Depends(get_company_service),
#     sector: str | None = None,
# ):
#     return await service.get_all(
#         pagination.page,
#         pagination.size,
#         sector,
#     )


# @router.post(
#     "/",
#     response_model=CompanyResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# async def create_company(
#     request: CompanyCreate,
#     service: CompanyService = Depends(get_company_service),
# ):
#     return await service.create(request)
