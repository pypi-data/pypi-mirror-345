"""
Base class for embedding providers in the Retrieverly package.
This abstract class defines the interface that all embedding providers must follow.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    async def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Get embeddings for a text query.
        
        Args:
            text: Text query
            
        Returns:
            Embedding vector as numpy array
        """
        pass
    
    @abstractmethod
    async def get_image_embedding(self, image: Union[Image.Image, Path, str]) -> np.ndarray:
        """
        Get embeddings for an image.
        
        Args:
            image: PIL image, path to image, or base64-encoded image string
            
        Returns:
            Embedding vector as numpy array
        """
        pass