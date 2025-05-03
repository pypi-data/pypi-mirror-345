"""
Qdrant implementation of the VectorStore abstract class.
This class provides integration with Qdrant (both in-memory and cloud) for the Retrieverly package.
"""

import uuid
from typing import Any, Dict, List, Optional, Union

import numpy as np
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from .base import VectorStore


class QdrantVectorStore(VectorStore):
    """Qdrant vector store implementation."""
    
    def __init__(
        self, 
        client: AsyncQdrantClient, 
        collection_name: str,
    ):
        """
        Initialize Qdrant vector store.
        
        Args:
            client: AsyncQdrantClient instance
            collection_name: Name of the collection to use
        """
        self.client = client
        self.collection_name = collection_name
    
    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        collections = await self.client.get_collections()
        collection_names = [collection.name for collection in collections.collections]
        return collection_name in collection_names
    
    async def create_collection(self, vector_size: int) -> None:
        """Create a new collection if it doesn't exist."""
        if not await self.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
    
    async def upsert(
        self,
        embeddings: List[np.ndarray], 
        payloads: List[Dict[str, Any]],
        ids: Optional[List[Union[str, int]]] = None
    ) -> None:
        """Insert or update vectors in the collection."""
        if not ids:
            ids = [str(uuid.uuid4().hex) for _ in range(len(embeddings))]
        
        points = []
        for i, (emb, payload, id_) in enumerate(zip(embeddings, payloads, ids)):
            point = models.PointStruct(
                id=id_,
                vector=emb.tolist(),
                payload=payload
            )
            points.append(point)
        
        # Upsert points to Qdrant
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    async def search(
        self,
        query_embedding: np.ndarray, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in the collection."""
        search_results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k
        )
        
        # Transform results to a consistent format
        formatted_results = []
        for result in search_results:
            formatted_result = {
                'id': result.id,
                'score': float(result.score),
                'payload': result.payload
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    async def delete_collection(self) -> None:
        """Delete a collection."""
        if await self.collection_exists(self.collection_name):
            await self.client.delete_collection(collection_name=self.collection_name)