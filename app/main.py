from fastapi import FastAPI
# from app.api.health import router as health_router
from app.api.health import router as health_router
from app.core.config import app_settings    
from app.core.logger import logger
from app.core.lifespan import lifespan

def create_app() -> FastAPI:
    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.version,
        debug=app_settings.debug,
        lifespan=lifespan
    )

    app.include_router(health_router)
    
    return app
