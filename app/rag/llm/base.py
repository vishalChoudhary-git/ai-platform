from abc import ABC, abstractmethod


class LLMGenerator(ABC):
    @abstractmethod
    async def generate(
        self,
        query: str,
        context: str,
    ) -> str:
        """Generate a grounded answer from the supplied context."""
        raise NotImplementedError
