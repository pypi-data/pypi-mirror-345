import pytest
from vector_store_client import VectorStoreClient

class DummyClient(VectorStoreClient):
    _method_map = {
        "create_record": {"command": "create_record", "params": ["vector", "metadata"]},
        "search_by_text": {"command": "search_by_text", "params": ["text", "limit"]},
    }
    def __init__(self):
        super().__init__(base_url="http://test")
        self.schema = {"commands": {"create_record": {"params": {}}, "search_by_text": {"params": {}}}}
    async def call_command(self, command, **params):
        self.last_call = (command, params)
        return "ok"
    async def create_record(self, vector, metadata=None):
        return await self.call_command(self._method_map["create_record"]["command"], vector=vector, metadata=metadata)
    async def search_by_text(self, text, limit=5):
        return await self.call_command(self._method_map["search_by_text"]["command"], text=text, limit=limit)

@pytest.mark.asyncio
async def test_create_record_mapping():
    client = DummyClient()
    result = await client.create_record(vector=[0.1]*384, metadata={"foo": "bar"})
    assert result == "ok"
    assert client.last_call[0] == "create_record"
    assert client.last_call[1]["vector"] == [0.1]*384
    assert client.last_call[1]["metadata"] == {"foo": "bar"}

@pytest.mark.asyncio
async def test_search_by_text_mapping():
    client = DummyClient()
    result = await client.search_by_text(text="query", limit=3)
    assert result == "ok"
    assert client.last_call[0] == "search_by_text"
    assert client.last_call[1]["text"] == "query"
    assert client.last_call[1]["limit"] == 3 