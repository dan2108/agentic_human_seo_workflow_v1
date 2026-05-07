from abc import ABC, abstractmethod


class CMSAdapter(ABC):
    @abstractmethod
    async def publish(self, content: dict) -> str: ...

    @abstractmethod
    async def update_meta(self, url: str, meta: dict) -> None: ...
