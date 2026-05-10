import base64
from typing import Any
import httpx
import structlog

from app.adapters.cms.base import CMSAdapter

log = structlog.get_logger()


class WordPressAdapter(CMSAdapter):
    def __init__(self, base_url: str, app_password: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_base = f"{self._base_url}/wp-json/wp/v2"
        encoded = base64.b64encode(app_password.encode()).decode()
        self._auth_header = {"Authorization": f"Basic {encoded}"}

    async def _find_page_by_slug(self, client: httpx.AsyncClient, slug: str) -> int | None:
        resp = await client.get(
            f"{self._api_base}/pages",
            params={"slug": slug},
            headers=self._auth_header,
        )
        pages = resp.json() if resp.status_code == 200 else []
        return pages[0]["id"] if pages else None

    async def update_meta(self, url: str, meta: dict[str, Any]) -> None:
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        log.info("wordpress.update_meta", slug=slug)

        async with httpx.AsyncClient(timeout=30) as client:
            page_id = await self._find_page_by_slug(client, slug)
            if page_id is None:
                log.warning("wordpress.page_not_found", slug=slug)
                return

            payload: dict[str, Any] = {}
            if "title" in meta:
                payload["title"] = meta["title"]
            if "description" in meta:
                payload["meta"] = {"_yoast_wpseo_metadesc": meta["description"]}

            await client.post(
                f"{self._api_base}/pages/{page_id}",
                json=payload,
                headers=self._auth_header,
            )

    async def publish(self, content: dict[str, Any]) -> str:
        log.info("wordpress.publish", title=content.get("title", ""))

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self._api_base}/posts",
                json=content,
                headers=self._auth_header,
            )

        data = resp.json()
        return data.get("link", "")
