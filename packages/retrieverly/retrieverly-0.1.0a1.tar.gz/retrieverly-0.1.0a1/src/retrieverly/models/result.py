"""
Result data models for Retrieverly.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from PIL import Image

from ..utils.image_processing import ImageProcessor


@dataclass
class RetrievalResult:
    """
    Represents a result from multimodal retrieval.
    """
    # Common fields
    source_file: str
    score: float
    
    # Image-specific fields
    image_path: Optional[Path] = None
    image_data_base64: Optional[str] = None
    page_number: Optional[int] = None
    
    # Additional metadata
    metadata: Dict = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def image(self) -> Optional[Image.Image]:
        """
        Get the image as a PIL Image object.
        
        Returns:
            PIL Image or None if no image data is available
        """
        if self.image_data_base64:
            return ImageProcessor.base64_to_image(self.image_data_base64)
        elif self.image_path and self.image_path.exists():
            return Image.open(self.image_path)
        return None
    
    def to_dict(self) -> Dict:
        """
        Convert result to dictionary representation.
        
        Returns:
            Dictionary representation of the result
        """
        result_dict = {
            "source_file": self.source_file,
            "score": self.score,
            "metadata": self.metadata,
        }
        
        # Add optional fields if they exist
        if self.page_number is not None:
            result_dict["page_number"] = self.page_number
            
        if self.image_path:
            result_dict["image_path"] = str(self.image_path)
            
        if self.image_data_base64:
            # Only include the start of the base64 data to avoid huge dictionaries
            base64_preview = self.image_data_base64[:50] + "..."
            result_dict["image_data_base64"] = base64_preview
            
        return result_dict