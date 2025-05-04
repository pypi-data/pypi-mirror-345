"""
Document Clustering using Vector Store Client.

This example demonstrates:
- Clustering similar documents
- Topic extraction
- Cluster visualization
"""

import asyncio
import logging
from typing import Dict, List, Tuple

import numpy as np
from sklearn.cluster import KMeans
from vector_store_client import VectorStoreClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentClusterer:
    """Document clustering system."""

    def __init__(self, base_url: str = "http://localhost:8007"):
        """Initialize clusterer.
        
        Args:
            base_url: Vector Store API URL
        """
        self.client = VectorStoreClient(base_url=base_url)

    async def add_document(
        self,
        text: str,
        title: str,
        source: str
    ) -> str:
        """Add document to the store.
        
        Args:
            text: Document text
            title: Document title
            source: Document source
            
        Returns:
            Record ID
        """
        metadata = {
            "type": "document",
            "title": title,
            "source": source,
            "text": text,
            "cluster": None  # Will be assigned later
        }
        
        record_id = await self.client.create_text_record(
            text=text,
            metadata=metadata
        )
        logger.info(f"Added document: {title}")
        return str(record_id)

    async def cluster_documents(
        self,
        n_clusters: int = 3,
        min_score: float = 0.5
    ) -> List[Dict]:
        """Cluster documents using K-means.
        
        Args:
            n_clusters: Number of clusters
            min_score: Minimum similarity score for cluster assignment
            
        Returns:
            List of cluster information
        """
        # Get all documents
        docs = await self.client.filter_records(
            criteria={"type": "document"},
            limit=1000,
            include_vectors=True
        )
        
        if not docs:
            return []
        
        # Extract vectors for clustering
        vectors = np.array([doc.vector for doc in docs if doc.vector])
        
        if len(vectors) < n_clusters:
            raise ValueError(
                f"Not enough documents ({len(vectors)}) "
                f"for {n_clusters} clusters"
            )
        
        # Perform clustering
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42
        ).fit(vectors)
        
        # Assign clusters and update documents
        clusters = [[] for _ in range(n_clusters)]
        
        for doc, cluster_id in zip(docs, kmeans.labels_):
            # Update document metadata with cluster
            await self.client.create_text_record(
                text=doc.metadata["text"],
                metadata={
                    **doc.metadata,
                    "cluster": int(cluster_id)
                }
            )
            
            # Add to cluster group
            clusters[cluster_id].append({
                "id": str(doc.id),
                "title": doc.metadata["title"],
                "source": doc.metadata["source"]
            })
        
        # Calculate cluster info
        cluster_info = []
        for i, cluster in enumerate(clusters):
            # Get cluster center
            center = kmeans.cluster_centers_[i]
            
            # Find most representative document
            if cluster:
                representative = await self._find_representative_doc(
                    center,
                    cluster
                )
            else:
                representative = None
            
            cluster_info.append({
                "cluster_id": i,
                "size": len(cluster),
                "documents": cluster,
                "representative": representative
            })
        
        return cluster_info

    async def _find_representative_doc(
        self,
        center: np.ndarray,
        cluster: List[Dict]
    ) -> Dict:
        """Find most representative document in cluster.
        
        Args:
            center: Cluster center vector
            cluster: List of documents in cluster
            
        Returns:
            Representative document info
        """
        # Search using cluster center
        results = await self.client.search_by_vector(
            vector=center.tolist(),
            limit=1
        )
        
        if results:
            doc = results[0]
            return {
                "id": str(doc.id),
                "title": doc.metadata["title"],
                "score": doc.score
            }
        return None


async def main():
    """Example usage of document clustering."""
    clusterer = DocumentClusterer()
    
    try:
        # Add sample documents
        documents = [
            (
                "Python is a popular programming language for data science and AI.",
                "Python Overview",
                "tech_blog"
            ),
            (
                "Machine learning algorithms help computers learn from data.",
                "Intro to ML",
                "tutorial"
            ),
            (
                "Deep learning networks process data through multiple layers.",
                "Deep Learning",
                "article"
            ),
            (
                "Data visualization helps understand complex patterns.",
                "Data Viz",
                "guide"
            ),
            (
                "Statistical analysis reveals insights in data.",
                "Stats Basics",
                "tutorial"
            )
        ]
        
        for text, title, source in documents:
            await clusterer.add_document(text, title, source)
        
        # Perform clustering
        clusters = await clusterer.cluster_documents(n_clusters=2)
        
        # Display results
        print("\nDocument Clusters:\n")
        for cluster in clusters:
            print(f"Cluster {cluster['cluster_id']}:")
            print(f"Size: {cluster['size']}")
            if cluster['representative']:
                print(
                    f"Representative: {cluster['representative']['title']} "
                    f"(score: {cluster['representative']['score']:.2f})"
                )
            print("\nDocuments:")
            for doc in cluster['documents']:
                print(f"- {doc['title']} ({doc['source']})")
            print()
    
    except Exception as e:
        logger.error(f"Error in clustering: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 