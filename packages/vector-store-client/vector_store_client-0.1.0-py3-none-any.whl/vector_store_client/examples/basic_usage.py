"""
Basic usage examples for Vector Store Client.

This module demonstrates the fundamental operations:
- Client initialization
- Creating records
- Searching
- Error handling
"""

import asyncio
import logging
from typing import List

from vector_store_client import VectorStoreClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_and_search_example() -> None:
    """Demonstrates basic create and search operations."""
    client = VectorStoreClient(base_url="http://localhost:8007")

    # Create a record from text
    try:
        record_id = await client.create_text_record(
            text="Python is a high-level programming language",
            metadata={"type": "programming", "language": "python"}
        )
        logger.info(f"Created record with ID: {record_id}")

        # Search for similar texts
        results = await client.search_by_text(
            text="python programming",
            limit=5
        )
        
        logger.info("Search results:")
        for result in results:
            logger.info(f"Score: {result.score:.2f}, Metadata: {result.metadata}")

    except Exception as e:
        logger.error(f"Error occurred: {e}")


async def batch_processing_example(texts: List[str]) -> None:
    """Demonstrates batch processing of multiple records."""
    client = VectorStoreClient(base_url="http://localhost:8007")

    try:
        # Create multiple records
        record_ids = []
        for text in texts:
            record_id = await client.create_text_record(
                text=text,
                metadata={"batch": "example"}
            )
            record_ids.append(record_id)
            logger.info(f"Created record: {record_id}")

        # Search across all created records
        results = await client.filter_records(
            criteria={"batch": "example"},
            limit=len(record_ids)
        )
        
        logger.info(f"Found {len(results)} records")

    except Exception as e:
        logger.error(f"Batch processing error: {e}")


async def vector_operations_example() -> None:
    """Demonstrates working with raw vectors."""
    client = VectorStoreClient(base_url="http://localhost:8007")

    # Example 384-dimensional vector (normally you'd get this from an embedding model)
    vector = [0.1] * 384

    try:
        # Create record with vector
        record_id = await client.create_record(
            vector=vector,
            metadata={"type": "raw_vector"}
        )
        logger.info(f"Created vector record: {record_id}")

        # Search by vector
        results = await client.search_by_vector(
            vector=vector,
            limit=5,
            include_vectors=True  # Include vectors in results
        )
        
        logger.info("Vector search results:")
        for result in results:
            logger.info(f"Score: {result.score:.2f}")

    except Exception as e:
        logger.error(f"Vector operations error: {e}")


async def main() -> None:
    """Run all examples."""
    # Basic create and search
    await create_and_search_example()

    # Batch processing
    sample_texts = [
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks",
        "Natural language processing works with text",
    ]
    await batch_processing_example(sample_texts)

    # Vector operations
    await vector_operations_example()


if __name__ == "__main__":
    asyncio.run(main()) 