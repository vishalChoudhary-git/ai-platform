import asyncio
import json
import urllib.error
import urllib.request
from typing import Any

from app.retrieval.reranked_chunk import RerankedRetrievedChunk
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
    ) -> list[RerankedRetrievedChunk]:
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

        data = await asyncio.to_thread(self._request, payload, headers)

        reranked: list[RerankedRetrievedChunk] = []
        for rank, item in enumerate(data.get("results", []), start=1):
            index = int(item["index"])
            candidate = candidates[index]
            reranked_candidate = RerankedRetrievedChunk(
                **candidate.model_dump(),
                rerank_score=float(item["relevance_score"]),
                rerank_rank=rank,
            )
            reranked.append(reranked_candidate)

        return reranked

    def _request(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        request = urllib.request.Request(
            self.ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OpenRouter reranker request failed: {exc.code} {body}"
            ) from exc
