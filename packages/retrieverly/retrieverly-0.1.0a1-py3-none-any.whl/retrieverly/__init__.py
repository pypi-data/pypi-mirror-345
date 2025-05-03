"""
Retrieverly: A lightweight async package for building Multi-Modal RAG applications
"""

__version__ = "0.1.0"

from retrieverly.multimodal_rag import MultiModalRAG
from retrieverly.vectorstores.qdrant import QdrantVectorStore
from retrieverly.models.result import RetrievalResult
from retrieverly.utils.logging import logger
from retrieverly.utils.utils import check_poppler_installed

__all__ = ["MultiModalRAG", "QdrantVectorStore", "RetrievalResult"]

# Check for critical dependencies early
if not check_poppler_installed():
    logger.warning(
        "Poppler utilities (required for PDF indexing) not found in PATH. "
        "Please install poppler-utils (Debian/Ubuntu), poppler (macOS/brew), "
        "or the equivalent for your OS. Indexing will fail without it."
    )
