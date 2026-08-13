from typing import Any

import httpx

from app.core.config import app_settings
from app.retrieval.reranking import Reranker
from app.retrieval.schemas import RetrievedChunk


class OpenRouterNemotronReranker(Reranker):
    ENDPOINT = "https://openrouter.ai/api/v1/rerank"

    def __init__(
        self,
        api_key: str,
        model: str,
        site_url: str,
        site_name: str,
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.model = model
        self.site_url = site_url
        self.site_name = site_name
        self.timeout = timeout

    async def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        if not candidates:
            return []

        payload = {
            "model": self.model,
            "query": query,
            "documents": [{"text": candidate.text} for candidate in candidates],
            "top_n": min(top_k, len(candidates)),
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-OpenRouter-Title": self.site_name,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.ENDPOINT,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        data: dict[str, Any] = response.json()

        reranked: list[RetrievedChunk] = []
        for rank, item in enumerate(data.get("results", []), start=1):
            index = int(item["index"])
            candidate = candidates[index]
            candidate.rerank_score = float(item["relevance_score"])
            candidate.rerank_rank = rank
            reranked.append(candidate)

        return reranked
