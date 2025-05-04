"""Integration tests for record creation commands and their aliases."""

import pytest
from uuid import uuid4
from datetime import datetime, UTC
from vector_store_client import VectorStoreClient

# Test data
TEST_VECTOR = [0.1] * 384
TEST_TEXT = "Test document for integration testing"
TEST_METADATA = {"source": "integration_test", "test_id": str(uuid4())}
TEST_TIMESTAMP = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

@pytest.mark.asyncio
async def test_create_record_and_alias(client: VectorStoreClient):
    """Test create_record and its alias add_vector produce identical results."""
    # Создаем запись через create_record
    record_id1 = await client._make_request(
        "create_record",
        {
            "vector": TEST_VECTOR,
            "metadata": TEST_METADATA,
            "timestamp": TEST_TIMESTAMP
        }
    )
    record_id1 = str(record_id1["result"])
    
    # Создаем запись через add_vector
    record_id2 = await client._make_request(
        "add_vector",
        {
            "vector": TEST_VECTOR,
            "metadata": TEST_METADATA,
            "timestamp": TEST_TIMESTAMP
        }
    )
    record_id2 = str(record_id2["result"])
    
    # Проверяем что обе записи созданы
    metadata1 = await client.get_metadata(record_id1)
    metadata2 = await client.get_metadata(record_id2)
    
    # Проверяем идентичность метаданных
    assert metadata1["source"] == metadata2["source"] == TEST_METADATA["source"]
    assert metadata1["test_id"] == TEST_METADATA["test_id"]
    assert metadata2["test_id"] == TEST_METADATA["test_id"]
    
    # Очистка
    await client.delete_records([record_id1, record_id2])

@pytest.mark.asyncio
async def test_create_text_record_and_alias(client: VectorStoreClient):
    """Test create_text_record and its alias add_text produce identical results."""
    # Создаем запись через create_text_record
    record_id1 = await client._make_request(
        "create_text_record",
        {
            "text": TEST_TEXT,
            "metadata": TEST_METADATA,
            "timestamp": TEST_TIMESTAMP
        }
    )
    record_id1 = str(record_id1["result"])
    
    # Создаем запись через add_text
    record_id2 = await client._make_request(
        "add_text",
        {
            "text": TEST_TEXT,
            "metadata": TEST_METADATA,
            "timestamp": TEST_TIMESTAMP
        }
    )
    record_id2 = str(record_id2["result"])
    
    # Проверяем что обе записи созданы
    metadata1 = await client.get_metadata(record_id1)
    metadata2 = await client.get_metadata(record_id2)
    
    # Проверяем идентичность метаданных
    assert metadata1["source"] == metadata2["source"] == TEST_METADATA["source"]
    assert metadata1["test_id"] == TEST_METADATA["test_id"]
    assert metadata2["test_id"] == TEST_METADATA["test_id"]
    
    # Проверяем идентичность текста
    text1 = await client.get_text(record_id1)
    text2 = await client.get_text(record_id2)
    assert text1 == text2 == TEST_TEXT
    
    # Очистка
    await client.delete_records([record_id1, record_id2])

@pytest.mark.asyncio
async def test_create_record_validation(client: VectorStoreClient):
    """Test validation in create_record/add_vector commands."""
    # Проверка некорректной размерности вектора
    invalid_vector = [0.1] * 10
    with pytest.raises(Exception) as exc_info:
        await client._make_request(
            "create_record",
            {
                "vector": invalid_vector,
                "metadata": TEST_METADATA
            }
        )
    assert "dimensions" in str(exc_info.value).lower()
    
    # То же самое для алиаса
    with pytest.raises(Exception) as exc_info:
        await client._make_request(
            "add_vector",
            {
                "vector": invalid_vector,
                "metadata": TEST_METADATA
            }
        )
    assert "dimensions" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_create_text_record_with_model(client: VectorStoreClient):
    """Test create_text_record/add_text with specific model."""
    # Создаем запись с указанием модели
    record_id = await client._make_request(
        "create_text_record",
        {
            "text": TEST_TEXT,
            "metadata": TEST_METADATA,
            "model": "paraphrase-multilingual-MiniLM-L12-v2"
        }
    )
    record_id = str(record_id["result"])
    
    # Проверяем что запись создана
    text = await client.get_text(record_id)
    assert text == TEST_TEXT
    
    # Очистка
    await client.delete_records([record_id]) 