from app.core.connectors.base import BaseConnector


class UploadConnector(BaseConnector):
    async def fetch(
        self,
        identifier: str,
    ):
        raise NotImplementedError("Upload connector not implemented.")

    async def health(self) -> bool:
        return True
