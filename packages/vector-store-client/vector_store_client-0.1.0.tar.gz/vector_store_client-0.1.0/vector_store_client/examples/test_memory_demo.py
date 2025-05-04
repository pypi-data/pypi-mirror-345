import pytest
import asyncio
from vector_store_client.examples.memory_demo import store_and_recall

class DummyClient:
    def __init__(self):
        self.mem = None
    async def create_text_record(self, text, metadata=None):
        self.mem = text
        return "memory_id"
    async def search_by_text(self, text, limit=1):
        class Result:
            def __init__(self, text):
                self.text = text
        return [Result(self.mem)]
    @classmethod
    async def create(cls, **kwargs):
        return cls()

@pytest.mark.asyncio
async def test_store_and_recall(monkeypatch):
    monkeypatch.setattr("vector_store_client.VectorStoreClient", DummyClient)
    mem_id, results = await store_and_recall()
    assert mem_id == "memory_id"
    assert results[0].text == "Remember: The project deadline is Friday."

@pytest.mark.asyncio
async def test_store_and_recall_live():
    try:
        mem_id, results = await store_and_recall()
    except Exception as e:
        pytest.skip(f"Vector Store API not available: {e}")
    assert isinstance(mem_id, str) and len(mem_id) > 0
    assert results and hasattr(results[0], 'text') 