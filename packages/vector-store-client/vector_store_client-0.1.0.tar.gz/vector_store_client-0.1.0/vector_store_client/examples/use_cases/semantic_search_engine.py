"""
Example of building a semantic search engine using Vector Store Client.

This example demonstrates:
- Building a document indexer
- Implementing semantic search
- Handling different document types
- Result ranking and filtering
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union
from pathlib import Path

from vector_store_client import VectorStoreClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document model for indexing."""
    
    content: str
    title: Optional[str] = None
    source: Optional[str] = None
    doc_type: Optional[str] = None
    created_at: datetime = datetime.now()


class SemanticSearchEngine:
    """Semantic search engine implementation."""

    def __init__(
        self,
        base_url: str = "http://localhost:8007",
        min_score: float = 0.7
    ):
        """Initialize search engine.
        
        Args:
            base_url: Vector Store API URL
            min_score: Minimum similarity score threshold
        """
        self.client = VectorStoreClient(base_url=base_url)
        self.min_score = min_score

    async def index_document(self, document: Document) -> str:
        """Index a document.
        
        Args:
            document: Document to index
            
        Returns:
            Record ID
        """
        metadata = {
            "title": document.title,
            "source": document.source,
            "doc_type": document.doc_type,
            "created_at": document.created_at.isoformat(),
            "text": document.content
        }
        
        record_id = await self.client.create_text_record(
            text=document.content,
            metadata=metadata
        )
        
        logger.info(
            f"Indexed document: {document.title or 'Untitled'} "
            f"(ID: {record_id})"
        )
        return str(record_id)

    async def index_file(self, file_path: Union[str, Path]) -> str:
        """Index a text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Record ID
        """
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as f:
            content = f.read()
        
        document = Document(
            content=content,
            title=path.name,
            source=str(path),
            doc_type="file"
        )
        
        return await self.index_document(document)

    async def search(
        self,
        query: str,
        doc_type: Optional[str] = None,
        limit: int = 5
    ) -> List[dict]:
        """Search for documents.
        
        Args:
            query: Search query
            doc_type: Optional document type filter
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        results = await self.client.search_by_text(
            text=query,
            limit=limit * 2  # Get extra results for filtering
        )
        
        # Filter and format results
        filtered_results = []
        for result in results:
            if result.score < self.min_score:
                continue
                
            if doc_type and result.metadata.get("doc_type") != doc_type:
                continue
                
            filtered_results.append({
                "id": str(result.id),
                "score": result.score,
                "title": result.metadata.get("title", "Untitled"),
                "source": result.metadata.get("source"),
                "doc_type": result.metadata.get("doc_type"),
                "text": result.metadata.get("text"),
                "created_at": result.metadata.get("created_at")
            })
            
            if len(filtered_results) >= limit:
                break
        
        return filtered_results


async def main():
    """Example usage of semantic search engine."""
    
    # Initialize search engine
    engine = SemanticSearchEngine()
    
    # Example documents
    documents = [
        Document(
            content="Python is a high-level programming language.",
            title="Python Overview",
            doc_type="article"
        ),
        Document(
            content="Machine learning is a subset of artificial intelligence.",
            title="ML Basics",
            doc_type="article"
        ),
        Document(
            content="Neural networks are inspired by biological neurons.",
            title="Neural Networks",
            doc_type="tutorial"
        )
    ]
    
    try:
        # Index documents
        for doc in documents:
            await engine.index_document(doc)
        
        # Perform search
        results = await engine.search(
            query="machine learning concepts",
            doc_type="article",
            limit=2
        )
        
        # Display results
        print("\nSearch Results:")
        for result in results:
            print(f"\nTitle: {result['title']}")
            print(f"Score: {result['score']:.2f}")
            print(f"Type: {result['doc_type']}")
            print(f"Text: {result['text'][:100]}...")
    
    except Exception as e:
        logger.error(f"Error in example: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 