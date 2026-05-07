class GSCAdapter:
    async def get_impressions(self, site_url: str, start_date: str, end_date: str) -> dict:
        raise NotImplementedError

    async def request_indexing(self, url: str) -> None:
        raise NotImplementedError
