"""
PDF processing utilities for Retrieverly.
"""

import os
from pathlib import Path
from typing import List

from pdf2image import convert_from_path

from .logging import logger
from .utils import check_poppler_installed


class PDFProcessor:
    """Utility class for PDF processing operations."""
    
    @staticmethod
    def convert_pdf_to_images(
        pdf_path: Path,
        output_dir: Path,
        dpi: int = 200
    ) -> List[Path]:
        """
        Convert PDF to images and save them to the output directory.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save the images (if None, a temporary directory is used)
            dpi: DPI for the images
            
        Returns:
            List of paths to the generated images
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Check for poppler dependency early
        if not check_poppler_installed():
             logger.error("Poppler utilities (pdftoppm) not found. PDF conversion requires poppler.")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info(f"Converting PDF '{pdf_path.name}' to images...")
            
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                output_folder=output_dir,
                fmt="png",
                paths_only=True,
                thread_count=os.cpu_count() - 1,
                dpi=dpi
            )
            
            # Get paths to the generated images
            image_paths = [Path(img_path) for img_path in images]
            
            logger.info(f"Successfully converted {pdf_path.name} to {len(image_paths)} images")
            
            return image_paths
            
        except Exception as e:
            logger.error(f"Error converting PDF '{pdf_path.name}' to images: {e}")
            raise
