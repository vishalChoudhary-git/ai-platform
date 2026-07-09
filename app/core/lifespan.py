from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.logger import logger
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting AI Platform...")

    # Future:
    # Connect PostgreSQL
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connected")
    # Connect Redis
    # Initialize OpenAI
    # Register Agents

    yield

    logger.info("🛑 Shutting down AI Platform...")

    # Future:
    # Close DB
    await engine.dispose()
    logger.info("Database disconnected")
    # Close Redis
