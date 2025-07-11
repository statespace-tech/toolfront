import logging

from pydantic import Field

from toolfront.models.api import API
from toolfront.models.connection import Connection

logger = logging.getLogger("toolfront")


class APIConnection(Connection):
    """API connection."""

    url: str = Field(..., description="Clean API URL.")

    async def connect(self) -> API:
        from toolfront.cache import load_from_cache

        # The spec should always be cached since save_connections already processed it
        spec = load_from_cache(self.url)
        if not spec:
            raise ConnectionError(f"Spec not found in cache: {self.url}")

        return API(spec=spec)
