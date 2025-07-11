import logging
from urllib.parse import ParseResult, urlparse

from pydantic import Field

from toolfront.models.connection import Connection
from toolfront.models.library import Library

logger = logging.getLogger("toolfront")


class LibraryConnection(Connection):
    url: str = Field(..., description="Full library URL.")

    async def connect(cls) -> Library:
        url: ParseResult = urlparse(cls.url)
        return Library(url=url)
