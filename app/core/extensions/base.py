from abc import ABC, abstractmethod


class BaseExtension(ABC):
    """
    Base class for every platform extension.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Extension unique name.
        """
        raise NotImplementedError

    @abstractmethod
    def register(self) -> None:
        """
        Register all extension components.
        """
        raise NotImplementedError
