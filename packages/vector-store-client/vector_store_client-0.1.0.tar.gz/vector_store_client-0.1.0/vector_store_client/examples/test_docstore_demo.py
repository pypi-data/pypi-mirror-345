import pytest
import asyncio
from vector_store_client.examples.docstore_demo import store_and_search_docs

class DummyClient:
    def __init__(self):
        self.docs = []
    async def create_text_record(self, text, metadata=None):
        self.docs.append((text, metadata))
        return f"doc_{len(self.docs)}"
    async def search_by_text(self, text, limit=2):
        class Result:
            def __init__(self, text, metadata):
                self.text = text
                self.metadata = metadata
        # Возвращаем первые два документа
        return [Result(t, m) for t, m in self.docs[:2]]
    @classmethod
    async def create(cls, **kwargs):
        return cls()

@pytest.mark.asyncio
async def test_store_and_search_docs(monkeypatch):
    monkeypatch.setattr("vector_store_client.VectorStoreClient", DummyClient)
    doc_ids, results = await store_and_search_docs()
    assert doc_ids == ["doc_1", "doc_2", "doc_3"]
    assert results[0].text == "A vector database stores embeddings."
    assert results[0].metadata["title"] == "Vector DB Guide"

@pytest.mark.asyncio
async def test_store_and_search_docs_live():
    try:
        doc_ids, results = await store_and_search_docs()
    except Exception as e:
        pytest.skip(f"Vector Store API not available: {e}")
    assert all(isinstance(i, str) and len(i) > 0 for i in doc_ids)
    assert results and hasattr(results[0], 'text') 