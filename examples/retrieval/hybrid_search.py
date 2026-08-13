import asyncio

from app.core.db.session import async_session_factory
from app.retrieval.factory import create_retrieval_service

QUERY = "What is Alex Morgan's professional experience?"


async def main() -> None:
    async with async_session_factory() as session:
        service = create_retrieval_service(session)

        results = await service.retrieve(
            query=QUERY,
            candidate_top_k=20,
            final_top_k=5,
            min_similarity=0.3,
        )

        for rank, result in enumerate(results, start=1):
            print(f"\n--- Result {rank} ---")
            print(f"chunk_id: {result.chunk_id}")
            print(f"document_id: {result.document_id}")
            print(f"vector_rank: {result.vector_rank}")
            print(f"keyword_rank: {result.keyword_rank}")
            print(f"rrf_score: {result.rrf_score}")
            print(f"rerank_score: {result.rerank_score}")
            print(f"rerank_rank: {result.rerank_rank}")
            print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
