from toolfront.models.api import API
from toolfront.models.database import Database

__all__ = ["API", "Database"]

try:
    from toolfront.models.document import Document

    __all__ += ["Document"]
except ImportError:
    Document = None
