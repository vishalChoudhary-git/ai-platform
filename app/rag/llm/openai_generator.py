from openai import AsyncOpenAI

from app.rag.llm.base import LLMGenerator


SYSTEM_PROMPT = """You are a document-grounded assistant.

Answer the user's question using only the supplied sources.

Rules:
1. Do not invent information.
2. Do not use knowledge outside the supplied sources.
3. If the sources do not contain enough information, say that the information was not found in the supplied documents.
4. Keep the answer concise and factual.
5. Cite supporting sources using [1], [2], etc.
"""


class OpenAILLMGenerator(LLMGenerator):
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, query: str, context: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"USER QUESTION:\n{query}\n\n"
                        f"SOURCES:\n{context}"
                    ),
                },
            ],
        )

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("LLM returned an empty response")

        return content.strip()
