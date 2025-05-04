"""
Best-practice example: Simple document store using VectorStoreClient
"""
import asyncio
from vector_store_client import VectorStoreClient

async def store_and_search_docs():
    client = await VectorStoreClient.create(base_url="http://localhost:8007")
    # Store documents
    docs = [
        {"title": "Vector DB Guide", "content": "A vector database stores embeddings."},
        {"title": "Python Tips", "content": "Use async for scalable I/O."},
        {"title": "AI News", "content": "Transformers are state-of-the-art."},
    ]
    doc_ids = []
    for doc in docs:
        doc_id = await client.create_text_record(
            text=doc["content"],
            metadata={"title": doc["title"]}
        )
        print(f"Stored doc: {doc['title']} -> {doc_id}")
        doc_ids.append(doc_id)
    # Semantic search
    results = await client.search_by_text(
        text="How to store embeddings?",
        limit=2
    )
    for result in results:
        print(f"Found: {result.text} (title: {result.metadata.get('title')})")
    return doc_ids, results

if __name__ == "__main__":
    asyncio.run(store_and_search_docs()) 