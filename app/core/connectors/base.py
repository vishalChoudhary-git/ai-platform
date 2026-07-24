from abc import ABC, abstractmethod


class BaseConnector(ABC):
    """
    Base class for every connector.
    """

    @abstractmethod
    async def fetch(
        self,
        identifier: str,
    ):
        """
        Fetch a document from the connector.
        """
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> bool:
        """
        Connector health check.
        """
        raise NotImplementedError
