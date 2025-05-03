"""
Cohere embedding provider implementation for Retrieverly.
This module supports Cohere's embed v4 model for generating embeddings from images and text.
"""

import base64
import io
from pathlib import Path
from typing import Dict, List, Union

import cohere
import numpy as np
from PIL import Image

from retrieverly.embeddings.base import EmbeddingProvider


class CohereEmbeddings(EmbeddingProvider):
    """
    Cohere embedding provider specifically optimized for the embed v4 model.
    """
    
    def __init__(self, api_key: str, model: str = "embed-v4.0"):
        """
        Initialize Cohere embedding provider.
        
        Args:
            api_key: Cohere API key
            model: Model name (default: embed-v4.0)
        """
        self.api_key = api_key
        self.model = model
        self.client = cohere.AsyncClientV2(api_key=api_key)
        self.vector_size = 1536  # Embed v4 model produces 1536-dimensional vectors
    
    async def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Get embeddings for a text query.
        
        Args:
            text: Text query
            
        Returns:
            Embedding vector as numpy array
        """
        api_response = await self.client.embed(
            model=self.model,
            input_type="search_query",
            embedding_types=["float"],
            texts=[text],
        )
        
        # Return the embedding
        return np.asarray(api_response.embeddings.float[0])
    
    async def get_image_embedding(self, image: Union[Image.Image, Path, str]) -> np.ndarray:
        """
        Get embeddings for an image.
        
        Args:
            image: PIL image, path to image, or base64-encoded image string
            
        Returns:
            Embedding vector as numpy array
        """
        # Convert to base64 if needed
        base64_image = self._get_base64_from_image(image)
        
        # Format for Cohere API
        api_input_document = {
            "content": [
                {"type": "image", "image": base64_image},
            ]
        }
        
        # Call the Embed v4.0 model with the image
        api_response = await self.client.embed(
            model=self.model,
            input_type="search_document",
            embedding_types=["float"],
            inputs=[api_input_document],
        )
        
        # Return the embedding
        return np.asarray(api_response.embeddings.float[0])
    
    def _get_base64_from_image(self, image: Union[Image.Image, Path, str]) -> str:
        """
        Convert an image to base64 encoding for API requests.
        
        Args:
            image: PIL image, path to image, or base64-encoded image string
            
        Returns:
            Base64-encoded image string with data URI prefix
        """
        # If already a base64 string
        if isinstance(image, str) and image.startswith("data:image"):
            return image
        
        # If it's a file path
        if isinstance(image, (str, Path)) and not isinstance(image, Image.Image):
            image = Image.open(image)
        
        # Ensure we have a PIL Image now
        if not isinstance(image, Image.Image):
            raise ValueError("Image must be a PIL Image, file path, or base64-encoded string")
        
        # Resize if needed (Cohere has maximum resolution limits)
        image = self._resize_image_if_needed(image)
        
        # Convert to base64
        img_format = image.format if image.format else "PNG"
        
        with io.BytesIO() as img_buffer:
            image.save(img_buffer, format=img_format)
            img_buffer.seek(0)
            base64_data = base64.b64encode(img_buffer.read()).decode("utf-8")
            
        # Add data URI prefix
        mime_type = f"image/{img_format.lower()}"
        base64_image = f"data:{mime_type};base64,{base64_data}"
        
        return base64_image
    
    def _resize_image_if_needed(self, image: Image.Image, max_pixels: int = 1568 * 1568) -> Image.Image:
        """
        Resize image if it exceeds maximum allowed pixels.
        
        Args:
            image: PIL Image
            max_pixels: Maximum number of pixels allowed
            
        Returns:
            Resized image if needed, otherwise original image
        """
        width, height = image.size
        
        if width * height > max_pixels:
            # Calculate scale factor to resize
            scale_factor = (max_pixels / (width * height)) ** 0.5
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # Create a copy before resizing
            resized_image = image.copy()
            resized_image.thumbnail((new_width, new_height))
            return resized_image
        
        return image