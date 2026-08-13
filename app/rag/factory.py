from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import app_settings
from app.rag.context_builder import ContextBuilder
from app.rag.llm.base import LLMGenerator
from app.rag.llm.openai_generator import OpenAILLMGenerator
from app.rag.service import RAGService
from app.retrieval.factory import create_retrieval_service


def create_llm_generator() -> LLMGenerator:
    return OpenAILLMGenerator(
        api_key=app_settings.openai_api_key,
        model=app_settings.rag_llm_model,
        max_tokens=app_settings.rag_llm_max_tokens,
        temperature=app_settings.rag_llm_temperature,
    )


def create_rag_service(session: AsyncSession) -> RAGService:
    return RAGService(
        retrieval_service=create_retrieval_service(session),
        context_builder=ContextBuilder(),
        llm_generator=create_llm_generator(),
    )
