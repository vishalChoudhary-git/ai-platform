import logging

from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"]
)

@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
    }
    
logger = logging.getLogger(__name__)