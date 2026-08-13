import asyncio

from app.core.db.session import async_session_factory
from app.rag.factory import create_rag_service

QUERY = "What is the hotel reimbursement limit?"


async def main() -> None:
    async with async_session_factory() as session:
        service = create_rag_service(session)

        response = await service.answer(
            query=QUERY,
            candidate_top_k=20,
            final_top_k=5,
            min_similarity=0.3,
        )

        print("\n=== ANSWER ===")
        print(response.answer)

        print("\n=== SOURCES ===")
        for source in response.sources:
            print(
                f"\n[{source.source_index}] "
                f"document={source.document_id} "
                f"page={source.page_number} "
                f"chunk={source.chunk_index}"
            )
            print(source.text)


if __name__ == "__main__":
    asyncio.run(main())
