import os


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_SITE_URL = os.getenv(
    "OPENROUTER_SITE_URL",
    "https://github.com/vishalChoudhary-git/ai-platform",
)
OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "AI Platform")
OPENROUTER_RERANKER_MODEL = os.getenv(
    "OPENROUTER_RERANKER_MODEL",
    "nvidia/llama-nemotron-rerank-vl-1b-v2:free",
)
