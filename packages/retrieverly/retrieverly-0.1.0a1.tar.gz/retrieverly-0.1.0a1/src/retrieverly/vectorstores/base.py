"""
Base class for vector stores in the Retrieverly package.
This abstract class defines the interface that all vector store implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import numpy as np


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    async def create_collection(self, collection_name: str, vector_size: int) -> None:
        """
        Create a new collection in the vector store if it doesn't exist.
        
        Args:
            collection_name: Name of the collection
            vector_size: Size of the vectors to be stored
        """
        pass
    
    @abstractmethod
    async def upsert(
        self, 
        collection_name: str, 
        embeddings: List[np.ndarray], 
        payloads: List[Dict[str, Any]],
        ids: Optional[List[Union[str, int]]] = None
    ) -> None:
        """
        Insert or update vectors in the collection.
        
        Args:
            collection_name: Name of the collection
            embeddings: List of embedding vectors
            payloads: List of metadata payloads
            ids: Optional list of IDs for the vectors
        """
        pass
    
    @abstractmethod
    async def search(
        self, 
        collection_name: str, 
        query_embedding: np.ndarray, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection.
        
        Args:
            collection_name: Name of the collection
            query_embedding: Embedding vector to search for
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    async def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection from the vector store.
        
        Args:
            collection_name: Name of the collection to delete
        """
        pass
    
    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in the vector store.
        
        Args:
            collection_name: Name of the collection to check
            
        Returns:
            True if the collection exists, False otherwise
        """
        pass