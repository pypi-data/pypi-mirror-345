"""
Best-practice example: Simple long-term memory using VectorStoreClient
"""
import asyncio
from vector_store_client import VectorStoreClient

async def store_and_recall():
    client = await VectorStoreClient.create(base_url="http://localhost:8007")
    # Store a memory
    memory_id = await client.create_text_record(
        text="Remember: The project deadline is Friday.",
        metadata={"type": "reminder"}
    )
    print(f"Memory stored: {memory_id}")
    # Recall by semantic search
    results = await client.search_by_text(
        text="When is the deadline?",
        limit=1
    )
    for result in results:
        print(f"Recalled: {result.text}")
    return memory_id, results

if __name__ == "__main__":
    asyncio.run(store_and_recall()) 