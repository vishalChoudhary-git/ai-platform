from app.retrieval.schemas import RetrievedChunk


class ContextBuilder:
    def build(self, chunks: list[RetrievedChunk]) -> str:
        sections: list[str] = []

        for source_index, chunk in enumerate(chunks, start=1):
            sections.append(
                "\n".join(
                    [
                        f"SOURCE [{source_index}]",
                        f"Document ID: {chunk.document_id}",
                        f"Page: {chunk.page_number if chunk.page_number is not None else 'N/A'}",
                        f"Chunk: {chunk.chunk_index}",
                        "",
                        chunk.text,
                    ]
                )
            )

        return "\n\n".join(sections)
