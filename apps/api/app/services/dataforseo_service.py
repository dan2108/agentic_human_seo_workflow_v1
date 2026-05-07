import httpx
from app.config import settings


class DataForSEOService:
    BASE_URL = "https://api.dataforseo.com/v3"

    def __init__(self):
        self.auth = (settings.dataforseo_login, settings.dataforseo_password)

    async def keyword_data(self, keywords: list[str]) -> dict:
        raise NotImplementedError

    async def serp(self, keyword: str) -> dict:
        raise NotImplementedError
