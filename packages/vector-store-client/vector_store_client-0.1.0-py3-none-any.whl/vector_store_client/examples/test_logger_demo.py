import pytest
import asyncio
from vector_store_client.examples.logger_demo import log_dialog

class DummyClient:
    def __init__(self):
        self.created = []
    async def create_text_record(self, text, metadata=None):
        self.created.append((text, metadata))
        return f"id_{len(self.created)}"
    @classmethod
    async def create(cls, **kwargs):
        return cls()

@pytest.mark.asyncio
async def test_log_dialog(monkeypatch):
    monkeypatch.setattr("vector_store_client.VectorStoreClient", DummyClient)
    ids = await log_dialog()
    assert len(ids) == 4
    assert ids == ["id_1", "id_2", "id_3", "id_4"]

@pytest.mark.asyncio
async def test_log_dialog_live():
    try:
        ids = await log_dialog()
    except Exception as e:
        pytest.skip(f"Vector Store API not available: {e}")
    assert len(ids) == 4
    assert all(isinstance(i, str) and len(i) > 0 for i in ids) 