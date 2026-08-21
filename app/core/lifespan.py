from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.db.session import engine
from app.core.logger import logger
from app.plugins.expenses.policy.startup import warm_expense_policy_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting AI Platform...")

    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connected")

    try:
        await warm_expense_policy_cache()
        logger.info("Expense policy cache warm-up completed")
    except Exception:
        logger.exception("Expense policy cache warm-up failed")

    yield

    logger.info("🛑 Shutting down AI Platform...")

    await engine.dispose()
    logger.info("Database disconnected")
