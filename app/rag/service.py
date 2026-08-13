import re

from app.rag.context_builder import ContextBuilder
from app.rag.llm.base import LLMGenerator
from app.rag.schemas import RAGResponse, RAGSource
from app.retrieval.services import RetrievalService


class RAGService:
    _SOURCE_PATTERN = re.compile(r"\[(\d+)\]")

    def __init__(
        self,
        retrieval_service: RetrievalService,
        context_builder: ContextBuilder,
        llm_generator: LLMGenerator,
    ):
        self.retrieval_service = retrieval_service
        self.context_builder = context_builder
        self.llm_generator = llm_generator

    async def answer(
        self,
        query: str,
        candidate_top_k: int = 20,
        final_top_k: int = 5,
        min_similarity: float = 0.3,
    ) -> RAGResponse:
        query = query.strip()

        if not query:
            raise ValueError("query must not be empty")

        chunks = await self.retrieval_service.retrieve(
            query=query,
            candidate_top_k=candidate_top_k,
            final_top_k=final_top_k,
            min_similarity=min_similarity,
        )

        if not chunks:
            return RAGResponse(
                answer="The information was not found in the supplied documents.",
                sources=[],
            )

        context = self.context_builder.build(chunks)

        answer = await self.llm_generator.generate(
            query=query,
            context=context,
        )

        all_sources = [
            RAGSource(
                source_index=index,
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
            )
            for index, chunk in enumerate(chunks, start=1)
        ]

        sources = self._select_cited_sources(
            answer=answer,
            sources=all_sources,
        )

        return RAGResponse(
            answer=answer,
            sources=sources,
        )

    @classmethod
    def _select_cited_sources(
        cls,
        answer: str,
        sources: list[RAGSource],
    ) -> list[RAGSource]:
        cited_indexes = {
            int(match)
            for match in cls._SOURCE_PATTERN.findall(answer)
        }

        return [
            source
            for source in sources
            if source.source_index in cited_indexes
        ]
