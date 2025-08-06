from .models.api import API
from .models.database import Database

__all__ = ["Database", "API"]

# Optional imports for document processing
try:
    from .models.document import Document  # noqa: F401

    __all__.append("Document")
except ImportError:
    # Document dependencies not installed
    pass
