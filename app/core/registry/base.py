from collections.abc import Iterator
from enum import StrEnum


class Registry[T]:
    """
    Generic registry used to register
    connectors, llms, tools, agents etc.
    """

    def __init__(self, registry_name: str):
        self._registry_name = registry_name
        self._items: dict[str, T] = {}

    def register(
        self,
        name: str | StrEnum,
        item: T,
    ) -> None:
        key = str(name)

        if key in self._items:
            raise ValueError(f"{self._registry_name}: '{key}' already registered.")

        self._items[key] = item

    def get(
        self,
        name: str | StrEnum,
    ) -> T:
        key = str(name)

        try:
            return self._items[key]

        except KeyError as exc:
            raise KeyError(f"{self._registry_name}: '{key}' not registered.") from exc

    def exists(
        self,
        name: str | StrEnum,
    ) -> bool:
        return str(name) in self._items

    def unregister(
        self,
        name: str | StrEnum,
    ):
        self._items.pop(str(name), None)

    def names(self) -> list[str]:
        return sorted(self._items.keys())

    def values(self) -> list[T]:
        return list(self._items.values())

    def __iter__(self) -> Iterator[T]:
        return iter(self._items.values())
