"""
Embedding provider implementations for Orbitron.
"""

from .base import EmbeddingProvider
from .cohere import CohereEmbeddings

__all__ = ["EmbeddingProvider", "CohereEmbeddings"]