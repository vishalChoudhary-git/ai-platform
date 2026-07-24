from app.core.constants.connectors import ConnectorName
from app.core.extensions.base import BaseExtension
from app.core.registry import connector_registry
from app.extensions.upload.connector import UploadConnector


class UploadExtension(BaseExtension):
    @property
    def name(self) -> str:
        return "upload"

    def register(self) -> None:
        connector_registry.register(
            ConnectorName.UPLOAD,
            UploadConnector(),
        )
