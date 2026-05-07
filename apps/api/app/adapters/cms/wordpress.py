from app.adapters.cms.base import CMSAdapter


class WordPressAdapter(CMSAdapter):
    async def publish(self, content: dict) -> str:
        raise NotImplementedError

    async def update_meta(self, url: str, meta: dict) -> None:
        raise NotImplementedError
