from pydantic import BaseModel

from toolfront.models.api import API
from toolfront.models.database import ConnectionResult, Database


class Connection(BaseModel):
    """Connection to a data source."""

    async def connect(self) -> Database | API:
        """Connect to the data source."""
        raise NotImplementedError("Subclasses must implement connect")

    @classmethod
    async def test_connection(cls, url: str) -> ConnectionResult:
        """Test the connection to the data source."""
        try:
            connection = cls(url=url)
            connection = await connection.connect()
            return await connection.test_connection()
        except Exception as e:
            return ConnectionResult(connected=False, message=str(e))
