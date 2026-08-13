from app.features.knowledge.schemas import KnowledgeQueryResponse, KnowledgeSource
from app.rag.service import RAGService


class KnowledgeService:
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service

    async def query(self, query: str) -> KnowledgeQueryResponse:
        response = await self.rag_service.answer(query=query)
        return KnowledgeQueryResponse(
            answer=response.answer,
            sources=[
                KnowledgeSource(
                    source_index=source.source_index,
                    chunk_id=source.chunk_id,
                    document_id=source.document_id,
                    page_number=source.page_number,
                    chunk_index=source.chunk_index,
                    text=source.text,
                )
                for source in response.sources
            ],
        )
