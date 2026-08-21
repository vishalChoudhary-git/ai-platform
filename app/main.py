from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.health import router as health_router
from app.core.config import app_settings
from app.core.lifespan import lifespan
from app.core.registry import connector_registry, extension_registry
from app.extensions.upload import UploadExtension
from app.features.documents.api.router import router as documents_router
from app.features.knowledge.api.router import router as knowledge_router
from app.plugins.expenses.api.router import router as expenses_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.version,
        debug=app_settings.debug,
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(documents_router)
    app.include_router(knowledge_router)
    app.include_router(expenses_router)
    upload_extension = UploadExtension()
    upload_extension.register()
    extension_registry.register(
        upload_extension.name,
        upload_extension,
    )

    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            openapi_version="3.0.3",
            routes=app.routes,
        )

        def normalize_file_schema(value: object) -> None:
            if isinstance(value, dict):
                if value.pop("contentMediaType", None):
                    value["format"] = "binary"
                for child in value.values():
                    normalize_file_schema(child)
            elif isinstance(value, list):
                for child in value:
                    normalize_file_schema(child)

        normalize_file_schema(schema)

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
    print(extension_registry.names())
    print(connector_registry.names())
    return app
