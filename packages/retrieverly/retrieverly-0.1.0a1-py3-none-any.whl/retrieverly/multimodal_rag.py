"""
Main implementation of the MultiModalRAG system for Retrieverly.
"""

import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union, Literal
import logging

from PIL import Image

from .embeddings.cohere import CohereEmbeddings
from .models.result import RetrievalResult
from .utils.image_processing import ImageProcessor
from .utils.pdf_processing import PDFProcessor
from .utils.logging import setup_logger
from .vectorstores.base import VectorStore

logger = logging.getLogger(__name__)

class MultiModalRAG:
    """
    MultiModalRAG class for indexing and retrieving multimodal content.
    """
    DEFAULT_OUTPUT_DIR_NAME = ".retrieverly/data"

    def __init__(
        self,
        vector_store: VectorStore,
        cohere_api_key: str,
        output_dir: Optional[Union[str, Path]] = None,
        storage_mode: Literal["reference", "embedded"] = "reference",
        verbose: bool = False
    ):
        """
        Initialize MultiModalRAG.
        
        Args:
            vector_store: Vector store instance
            cohere_api_key: Cohere API key
            cache_dir: Directory to cache images (default: ~/.retrieverly/cache)
            storage_mode: Storage mode: "reference" or "embedded" (default: "reference")
            verbose: Enable verbose logging
        """
        # Set up vector store
        self.vector_store = vector_store
        
        # Set up embedding provider
        self.embedding_provider = CohereEmbeddings(api_key=cohere_api_key)
        
        # Set up output directory
        if output_dir is None:
            # Default to .retrieverly/output in the current working directory
            self.output_dir = Path.cwd() / self.DEFAULT_OUTPUT_DIR_NAME
        else:
            # Use specified output directory
            self.output_dir = Path(output_dir).resolve()
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure storage mode
        if storage_mode not in ["reference", "embedded"]:
            raise ValueError("Storage mode must be 'reference' or 'embedded'")
        self.storage_mode = storage_mode
        
        # Configure logging verbosity
        self.logger = setup_logger(level=logging.INFO if verbose else logging.WARNING)

    async def index(
        self, 
        path: Union[str, Path],
        recursive: bool = True
    ) -> Dict:
        """
        Index a file or directory.
        
        Args:
            path: Path to file or directory
            recursive: Recursively index directories
            
        Returns:
            Summary of indexing operation
        """
        file_or_dir = Path(path)
        
        # Initialize collection if needed
        await self.vector_store.create_collection(
            self.embedding_provider.vector_size
        )
        
        # Process based on input type
        if file_or_dir.is_file():
            return await self._index_file(file_or_dir)
        elif file_or_dir.is_dir():
            return await self._index_directory(file_or_dir, recursive)
        else:
            raise ValueError(f"Path does not exist: {file_or_dir}")
    
    async def _index_directory(
        self, 
        directory: Path, 
        recursive: bool
    ) -> Dict:
        """
        Index a directory of files.
        
        Args:
            directory: Directory path
            recursive: Recursively index subdirectories
            
        Returns:
            Summary of indexing operation
        """
        # Get files to process
        pattern = "**/*" if recursive else "*"
        files = []
        
        # Get supported extensions
        supported_extensions = [".pdf", ".png", ".jpg", ".jpeg"]
        
        # Find all files with supported extensions
        for ext in supported_extensions:
            files.extend(directory.glob(f"{pattern}{ext}"))
        
        # Process each file
        total_files = len(files)
        processed_files = 0
        processed_images = 0
        failed_files = 0
        
        self.logger.info(f"Found {total_files} files to process in {directory}")
        
        for file in files:
            try:
                result = await self._index_file(file)
                processed_files += 1
                processed_images += result.get("images_indexed", 0)
            except Exception as e:
                self.logger.error(f"Failed to process {file}: {e}")
                failed_files += 1
        
        return {
            "total_files": total_files,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "images_indexed": processed_images
        }
    
    async def _index_file(self, file_path: Path) -> Dict:
        """
        Index a single file.
        
        Args:
            file_path: File path
            
        Returns:
            Summary of indexing operation
        """
        file_path = Path(file_path)

        # Process based on file type
        if file_path.suffix.lower() == ".pdf":
            return await self._index_pdf(file_path)
        elif file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
            return await self._index_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    async def _index_pdf(self, pdf_path: Path) -> Dict:
        """
        Index a PDF file by converting to images and then indexing each image.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Summary of indexing operation
        """

        # Convert PDF to images and store them directly in output directory
        image_paths = PDFProcessor.convert_pdf_to_images(
            pdf_path, 
            output_dir=Path(self.output_dir)
        )
        
        # Index each image
        embeddings = []
        payloads = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # Load image
                image = Image.open(image_path)
                
                # Get embedding
                embedding = await self.embedding_provider.get_image_embedding(image)
                
                # Create payload based on storage mode
                page_number = i + 1
                
                if self.storage_mode == "reference":
                    # Create payload with direct image reference
                    payload = {
                        "source_file": pdf_path.name,
                        "page_number": page_number,
                        "image_path": str(image_path)
                    }
                else:  # embedded mode
                    # Convert image to base64
                    base64_image = ImageProcessor.image_to_base64(image)
                    
                    # Create payload with embedded image
                    payload = {
                        "source_file": pdf_path.name,
                        "page_number": page_number,
                        "image_data": base64_image
                    }
                
                # Add to batches
                embeddings.append(embedding)
                payloads.append(payload)

            except Exception as e:
                self.logger.error(f"Error processing image {image_path}: {e}")
        
        # Store in vector database
        if embeddings:
            await self.vector_store.upsert(
                embeddings,
                payloads,
            )
        
        return {
            "file": pdf_path.name,
            "images_indexed": len(embeddings)
        }
    
    async def _index_image(self, image_path: Path) -> Dict:
        """
        Index a single image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Summary of indexing operation
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Get embedding
            embedding = await self.embedding_provider.get_image_embedding(image)
            
            # Create payload based on storage mode
            image_id = uuid.uuid4().hex
            
            if self.storage_mode == "reference":
                output_filename = f"{image_path.name}"
                output_path = self.output_dir / output_filename
                
                # Save image directly to output directory
                image.save(output_path)
                
                # Create payload with direct image reference
                payload = {
                    "source_file": image_path.name,
                    "image_path": str(output_path)
                }
            else:  # embedded mode
                # Convert image to base64
                base64_image = ImageProcessor.image_to_base64(image)
                
                # Create payload with embedded image
                payload = {
                    "source_file": image_path.name,
                    "image_data": base64_image
                }
            
            # Store in vector database
            await self.vector_store.upsert(
                [embedding],
                [payload],
                [image_id]
            )
            
            return {
                "file": image_path.name,
                "images_indexed": 1
            }
            
        except Exception as e:
            self.logger.error(f"Error indexing image {image_path}: {e}")
            raise
    
    async def retrieve(self, query: str, top_k: int = 3) -> List[RetrievalResult]:
        """
        Retrieve most relevant images based on a text query.
        
        Args:
            query: Text query
            top_k: Number of results to return
            
        Returns:
            List of retrieval results
        """
        self.logger.info(f"Retrieving results for query: '{query}'")
        
        # Get query embedding
        query_embedding = await self.embedding_provider.get_text_embedding(query)
        
        # Search in vector store
        search_results = await self.vector_store.search(
            query_embedding,
            top_k=top_k
        )
        
        # Convert to RetrievalResult objects
        results = []
        for result in search_results:
            payload = result["payload"]
            
            # Create result object based on storage mode
            if self.storage_mode == "reference" and "image_path" in payload:
                # Reference mode - use image path
                result_obj = RetrievalResult(
                    source_file=payload["source_file"],
                    score=result["score"],
                    image_path=Path(payload["image_path"]),
                    page_number=payload.get("page_number")
                )
            elif "image_data" in payload:
                # Embedded mode - use base64 data
                result_obj = RetrievalResult(
                    source_file=payload["source_file"],
                    score=result["score"],
                    image_data_base64=payload["image_data"],
                    page_number=payload.get("page_number")
                )
            else:
                # Fallback for unexpected payload structure
                self.logger.warning(f"Unexpected payload structure for result ID {result['id']}")
                result_obj = RetrievalResult(
                    source_file=payload.get("source_file", "unknown"),
                    score=result["score"]
                )
            
            results.append(result_obj)
        
        self.logger.info(f"Found {len(results)} results for query: '{query}'")
        return results