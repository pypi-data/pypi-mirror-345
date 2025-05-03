"""Image processing utilities for Retrieverly."""

import base64
import io
from typing import Optional
from PIL import Image


class ImageProcessor:
    """Utility class for image processing operations."""
    
    @staticmethod
    def resize_image(
        image: Image.Image, 
        max_pixels: int = 1568 * 1568
    ) -> Image.Image:
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
    
    @staticmethod
    def image_to_base64(
        image: Image.Image, 
        format: Optional[str] = None
    ) -> str:
        """
        Convert PIL image to base64 string with data URI prefix.
        
        Args:
            image: PIL image
            format: Image format (default: use image's format or PNG)
            
        Returns:
            Base64-encoded image string with data URI prefix
        """
        img_format = format or image.format or "PNG"
        
        with io.BytesIO() as img_buffer:
            image.save(img_buffer, format=img_format)
            img_buffer.seek(0)
            base64_data = base64.b64encode(img_buffer.read()).decode("utf-8")
            
        # Add data URI prefix
        mime_type = f"image/{img_format.lower()}"
        base64_image = f"data:{mime_type};base64,{base64_data}"
        
        return base64_image
    
    @staticmethod
    def base64_to_image(base64_string: str) -> Image.Image:
        """
        Convert base64 string to PIL image.
        
        Args:
            base64_string: Base64-encoded image string (with or without data URI prefix)
            
        Returns:
            PIL Image
        """
        # Remove data URI prefix if present
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
            
        # Decode base64 to bytes
        image_data = base64.b64decode(base64_string)
        
        # Create PIL image from bytes
        return Image.open(io.BytesIO(image_data))