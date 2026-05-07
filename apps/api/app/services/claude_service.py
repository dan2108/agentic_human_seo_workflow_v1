import anthropic
from app.config import settings


class ClaudeService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-6"

    async def complete(self, system: str, user: str) -> str:
        # TODO: add prompt caching on system prompt; structured output mode
        raise NotImplementedError

    async def stream(self, system: str, user: str):
        # TODO: yield SSE chunks for co-pilot streaming
        raise NotImplementedError
