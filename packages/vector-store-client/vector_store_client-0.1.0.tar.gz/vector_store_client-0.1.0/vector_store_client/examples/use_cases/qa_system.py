"""
Question Answering System using Vector Store Client.

This example demonstrates:
- Building a simple QA system
- Storing and retrieving question-answer pairs
- Finding similar questions
"""

import asyncio
import logging
from typing import List, Optional, Tuple

from vector_store_client import VectorStoreClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QASystem:
    """Simple Question Answering system."""

    def __init__(self, base_url: str = "http://localhost:8007"):
        """Initialize QA system.
        
        Args:
            base_url: Vector Store API URL
        """
        self.client = VectorStoreClient(base_url=base_url)

    async def add_qa_pair(
        self,
        question: str,
        answer: str,
        category: Optional[str] = None
    ) -> str:
        """Add question-answer pair to the store.
        
        Args:
            question: The question text
            answer: The answer text
            category: Optional category/topic
            
        Returns:
            Record ID
        """
        metadata = {
            "type": "qa_pair",
            "question": question,
            "answer": answer,
            "category": category
        }
        
        record_id = await self.client.create_text_record(
            text=question,  # Index by question for similarity search
            metadata=metadata
        )
        logger.info(f"Added QA pair with ID: {record_id}")
        return str(record_id)

    async def find_similar_questions(
        self,
        question: str,
        min_score: float = 0.7,
        limit: int = 5
    ) -> List[Tuple[str, str, float]]:
        """Find similar questions and their answers.
        
        Args:
            question: Query question
            min_score: Minimum similarity score
            limit: Maximum number of results
            
        Returns:
            List of (question, answer, score) tuples
        """
        results = await self.client.search_by_text(
            text=question,
            limit=limit
        )
        
        # Filter and format results
        qa_pairs = []
        for result in results:
            if result.score < min_score:
                continue
                
            metadata = result.metadata
            if metadata.get("type") != "qa_pair":
                continue
                
            qa_pairs.append((
                metadata["question"],
                metadata["answer"],
                result.score
            ))
        
        return qa_pairs


async def main():
    """Example usage of QA system."""
    qa = QASystem()
    
    # Add some QA pairs
    qa_data = [
        (
            "What is vector search?",
            "Vector search is a technique for finding similar items by comparing their vector representations.",
            "technical"
        ),
        (
            "How does vector similarity work?",
            "Vector similarity measures how close two vectors are in high-dimensional space, often using cosine similarity.",
            "technical"
        ),
        (
            "What are embeddings?",
            "Embeddings are vector representations of data (text, images, etc.) that capture semantic meaning.",
            "technical"
        )
    ]
    
    try:
        # Add QA pairs
        for question, answer, category in qa_data:
            await qa.add_qa_pair(question, answer, category)
        
        # Search for similar questions
        query = "Can you explain vector embeddings?"
        results = await qa.find_similar_questions(query, min_score=0.6)
        
        # Display results
        print(f"\nQuery: {query}\n")
        for question, answer, score in results:
            print(f"Q: {question}")
            print(f"A: {answer}")
            print(f"Similarity: {score:.2f}\n")
    
    except Exception as e:
        logger.error(f"Error in QA system: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 