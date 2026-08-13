import asyncio

from app.core.db.session import async_session_factory
from app.retrieval.factory import create_retrieval_service


QUERY = "What is the hotel reimbursement limit?"


async def main() -> None:
    async with async_session_factory() as session:
        service = create_retrieval_service(session)

        results = await service.keyword_search(
            query=QUERY,
            top_k=5,
        )

        for rank, result in enumerate(results, start=1):
            print(f"\n--- Result {rank} ---")
            print(f"chunk_id: {result.chunk_id}")
            print(f"document_id: {result.document_id}")
            print(f"keyword_rank: {result.keyword_rank}")
            print(f"keyword_score: {result.keyword_score}")
            print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
