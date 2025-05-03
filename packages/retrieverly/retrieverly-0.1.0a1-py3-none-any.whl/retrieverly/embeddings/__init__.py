"""
Embedding provider implementations for Retrieverly.
"""

from .base import EmbeddingProvider
from .cohere import CohereEmbeddings

__all__ = ["EmbeddingProvider", "CohereEmbeddings"]