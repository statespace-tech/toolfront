from toolfront.models.api import API
from toolfront.models.database import Database

__all__ = ["API", "Database"]

try:
    from toolfront.models.document import Document
    __all__.append("Document")
except ImportError:
    # Document functionality not available without optional dependencies
    pass
