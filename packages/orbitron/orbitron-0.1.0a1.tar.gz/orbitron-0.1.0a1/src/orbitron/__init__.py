"""
Orbitron: A lightweight async package for building Multi-Modal RAG applications
"""

__version__ = "0.1.0"

from orbitron.multimodal_rag import MultiModalRAG
from orbitron.vectorstores.qdrant import QdrantVectorStore
from orbitron.models.result import RetrievalResult
from orbitron.utils.logging import logger
from orbitron.utils.utils import check_poppler_installed

__all__ = ["MultiModalRAG", "QdrantVectorStore", "RetrievalResult"]

# Check for critical dependencies early
if not check_poppler_installed():
    logger.warning(
        "Poppler utilities (required for PDF indexing) not found in PATH. "
        "Please install poppler-utils (Debian/Ubuntu), poppler (macOS/brew), "
        "or the equivalent for your OS. Indexing will fail without it."
    )
