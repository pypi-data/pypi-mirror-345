"""
Content Recommendation System using Vector Store Client.

This example demonstrates:
- Building a simple content recommender
- User profile management
- Content-based recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional
from uuid import UUID

from vector_store_client import VectorStoreClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentRecommender:
    """Content-based recommendation system."""

    def __init__(self, base_url: str = "http://localhost:8007"):
        """Initialize recommender.
        
        Args:
            base_url: Vector Store API URL
        """
        self.client = VectorStoreClient(base_url=base_url)

    async def add_content(
        self,
        content: str,
        content_type: str,
        tags: List[str],
        author: Optional[str] = None
    ) -> str:
        """Add content item to the store.
        
        Args:
            content: Content text
            content_type: Type of content (article, post, etc.)
            tags: Content tags/categories
            author: Optional content author
            
        Returns:
            Record ID
        """
        metadata = {
            "type": "content",
            "content_type": content_type,
            "tags": tags,
            "author": author,
            "text": content
        }
        
        record_id = await self.client.create_text_record(
            text=content,
            metadata=metadata
        )
        logger.info(
            f"Added {content_type} content: "
            f"{content[:50]}... (ID: {record_id})"
        )
        return str(record_id)

    async def update_user_profile(
        self,
        user_id: str,
        interests: List[str],
        viewed_content: Optional[List[str]] = None
    ) -> str:
        """Update user profile with interests and viewed content.
        
        Args:
            user_id: User identifier
            interests: List of user interests
            viewed_content: Optional list of viewed content IDs
            
        Returns:
            Profile record ID
        """
        # Combine interests into a text description
        profile_text = (
            f"User interested in: {', '.join(interests)}. "
            "Looking for relevant content."
        )
        
        metadata = {
            "type": "user_profile",
            "user_id": user_id,
            "interests": interests,
            "viewed_content": viewed_content or []
        }
        
        record_id = await self.client.create_text_record(
            text=profile_text,
            metadata=metadata
        )
        logger.info(f"Updated profile for user: {user_id}")
        return str(record_id)

    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 5,
        min_score: float = 0.6
    ) -> List[Dict]:
        """Get content recommendations for user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of recommendations
            min_score: Minimum similarity score
            
        Returns:
            List of recommended content items
        """
        # Find user profile
        profiles = await self.client.filter_records(
            criteria={"type": "user_profile", "user_id": user_id},
            limit=1
        )
        if not profiles:
            raise ValueError(f"User profile not found: {user_id}")
        
        profile = profiles[0]
        
        # Search for relevant content
        results = await self.client.search_by_text(
            text=profile.metadata["interests"][0],  # Use first interest
            limit=limit * 2  # Get extra results for filtering
        )
        
        # Filter and format recommendations
        recommendations = []
        viewed = set(profile.metadata.get("viewed_content", []))
        
        for result in results:
            if result.score < min_score:
                continue
                
            metadata = result.metadata
            if metadata.get("type") != "content":
                continue
                
            if str(result.id) in viewed:
                continue
                
            recommendations.append({
                "id": str(result.id),
                "content": metadata["text"][:200] + "...",
                "content_type": metadata["content_type"],
                "tags": metadata["tags"],
                "author": metadata.get("author"),
                "score": result.score
            })
            
            if len(recommendations) >= limit:
                break
        
        return recommendations


async def main():
    """Example usage of content recommender."""
    recommender = ContentRecommender()
    
    try:
        # Add some content
        content_items = [
            (
                "Python is a versatile programming language perfect for data science and AI.",
                "article",
                ["programming", "python", "tech"],
                "John Doe"
            ),
            (
                "Machine learning algorithms are transforming the tech industry.",
                "article",
                ["ai", "ml", "tech"],
                "Jane Smith"
            ),
            (
                "Data visualization best practices for clear communication.",
                "tutorial",
                ["data", "visualization", "tech"],
                "Alice Brown"
            )
        ]
        
        for content, type_, tags, author in content_items:
            await recommender.add_content(content, type_, tags, author)
        
        # Create user profile
        user_id = "user123"
        await recommender.update_user_profile(
            user_id=user_id,
            interests=["python programming", "data science"]
        )
        
        # Get recommendations
        recommendations = await recommender.get_recommendations(user_id)
        
        # Display results
        print(f"\nRecommendations for user {user_id}:\n")
        for rec in recommendations:
            print(f"Type: {rec['content_type']}")
            print(f"Tags: {', '.join(rec['tags'])}")
            print(f"Author: {rec['author']}")
            print(f"Score: {rec['score']:.2f}")
            print(f"Preview: {rec['content']}\n")
    
    except Exception as e:
        logger.error(f"Error in recommender: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 