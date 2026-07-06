from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting AI Platform...")

    # Future:
    # Connect PostgreSQL
    # Connect Redis
    # Initialize OpenAI
    # Register Agents

    yield

    logger.info("🛑 Shutting down AI Platform...")

    # Future:
    # Close DB
    # Close Redis
