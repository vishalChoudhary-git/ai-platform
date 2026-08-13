from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import app_settings
from app.core.lifespan import lifespan
from app.core.registry import connector_registry, extension_registry
from app.extensions.upload import UploadExtension
from app.features.documents.api.router import router as documents_router
from app.retrieval.api.router import router as retrieval_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.version,
        debug=app_settings.debug,
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(documents_router)
    app.include_router(retrieval_router)
    upload_extension = UploadExtension()
    upload_extension.register()
    extension_registry.register(
        upload_extension.name,
        upload_extension,
    )
    print(extension_registry.names())
    print(connector_registry.names())
    return app
