"""
Best-practice example: Simple dialog logger using VectorStoreClient
"""
import asyncio
from vector_store_client import VectorStoreClient

async def log_dialog():
    client = await VectorStoreClient.create(base_url="http://localhost:8007")
    dialog = [
        {"role": "user", "text": "Hello!"},
        {"role": "assistant", "text": "Hi! How can I help you?"},
        {"role": "user", "text": "What's the weather?"},
        {"role": "assistant", "text": "It's sunny."},
    ]
    record_ids = []
    for turn in dialog:
        record_id = await client.create_text_record(
            text=turn["text"],
            metadata={"role": turn["role"]}
        )
        print(f"Logged: {turn['role']} -> {record_id}")
        record_ids.append(record_id)
    return record_ids

if __name__ == "__main__":
    asyncio.run(log_dialog()) 