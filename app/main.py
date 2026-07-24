from fastapi import FastAPI

from app.api.company import router as company_router
from app.api.health import router as health_router
from app.core.config import app_settings
from app.core.constants.connectors import ConnectorName
from app.core.lifespan import lifespan
from app.core.registry import connector_registry
from app.extensions.upload import UploadConnector


def create_app() -> FastAPI:
    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.version,
        debug=app_settings.debug,
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(company_router)
    connector_registry.register(
        ConnectorName.UPLOAD,
        UploadConnector(),
    )
    print(connector_registry.names())
    return app
