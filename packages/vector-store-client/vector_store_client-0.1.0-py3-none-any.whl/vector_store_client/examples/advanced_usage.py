"""
Advanced usage examples for Vector Store Client.

This module demonstrates more complex scenarios:
- Custom error handling
- Connection pooling
- Batch operations with concurrency
- Custom metadata filtering
"""

import asyncio
import logging
from typing import List, Optional
from uuid import UUID

import httpx
from vector_store_client import VectorStoreClient
from vector_store_client.models import SearchResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomVectorClient:
    """Example of a custom client wrapper with additional functionality."""

    def __init__(
        self,
        base_url: str,
        max_retries: int = 3,
        timeout: float = 10.0,
        max_connections: int = 10
    ):
        """Initialize custom client wrapper.
        
        Args:
            base_url: Base URL for the Vector Store API
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            max_connections: Maximum number of concurrent connections
        """
        self.limits = httpx.Limits(
            max_keepalive_connections=max_connections,
            max_connections=max_connections
        )
        self.timeout = httpx.Timeout(timeout)
        self.client = httpx.AsyncClient(
            limits=self.limits,
            timeout=self.timeout
        )
        self.vector_client = VectorStoreClient(
            base_url=base_url,
            async_client=self.client
        )
        self.max_retries = max_retries

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    async def create_with_retry(
        self,
        text: str,
        metadata: Optional[dict] = None,
        retry_count: int = 0
    ) -> UUID:
        """Create record with automatic retry on failure.
        
        Args:
            text: Text to vectorize and store
            metadata: Optional metadata
            retry_count: Current retry attempt number
            
        Returns:
            UUID of created record
            
        Raises:
            Exception: If all retries fail
        """
        try:
            return await self.vector_client.create_text_record(
                text=text,
                metadata=metadata
            )
        except Exception as e:
            if retry_count < self.max_retries:
                logger.warning(f"Retry {retry_count + 1}/{self.max_retries}")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.create_with_retry(
                    text=text,
                    metadata=metadata,
                    retry_count=retry_count + 1
                )
            raise Exception(f"Failed after {self.max_retries} retries") from e

    async def batch_create_concurrent(
        self,
        texts: List[str],
        chunk_size: int = 5
    ) -> List[UUID]:
        """Create multiple records concurrently in chunks.
        
        Args:
            texts: List of texts to process
            chunk_size: Number of concurrent operations
            
        Returns:
            List of created record UUIDs
        """
        results = []
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i:i + chunk_size]
            tasks = [
                self.create_with_retry(text, {"chunk": i // chunk_size})
                for text in chunk
            ]
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend([r for r in chunk_results if not isinstance(r, Exception)])
        return results

    async def semantic_search_with_filter(
        self,
        text: str,
        metadata_filter: dict,
        limit: int = 5
    ) -> List[SearchResult]:
        """Combine semantic search with metadata filtering.
        
        Args:
            text: Search query text
            metadata_filter: Metadata criteria for filtering
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        # First, get more results than needed to allow for filtering
        results = await self.vector_client.search_by_text(
            text=text,
            limit=limit * 2  # Get extra results for filtering
        )

        # Then filter by metadata
        filtered_results = []
        for result in results:
            if all(
                result.metadata.get(k) == v
                for k, v in metadata_filter.items()
            ):
                filtered_results.append(result)
                if len(filtered_results) >= limit:
                    break

        return filtered_results[:limit]


async def advanced_example() -> None:
    """Demonstrate advanced usage patterns."""
    
    async with CustomVectorClient(base_url="http://localhost:8007") as client:
        # Example texts
        texts = [
            "Python is great for data science",
            "Machine learning with scikit-learn",
            "Deep learning with PyTorch",
            "TensorFlow for neural networks",
            "Natural Language Processing in Python",
            "Data analysis with pandas",
            "Visualization with matplotlib"
        ]

        try:
            # Batch create with concurrency
            logger.info("Creating records concurrently...")
            record_ids = await client.batch_create_concurrent(texts, chunk_size=3)
            logger.info(f"Created {len(record_ids)} records")

            # Combined semantic search and metadata filtering
            logger.info("Performing filtered semantic search...")
            results = await client.semantic_search_with_filter(
                text="machine learning",
                metadata_filter={"chunk": 0},
                limit=3
            )

            logger.info("Search results:")
            for result in results:
                logger.info(
                    f"Score: {result.score:.2f}, "
                    f"Metadata: {result.metadata}"
                )

        except Exception as e:
            logger.error(f"Error in advanced example: {e}")


if __name__ == "__main__":
    asyncio.run(advanced_example()) 