"""
Тесты для проверки всех команд Vector Store API с использованием реального сервера.

Эти тесты работают с живым API и требуют запущенного сервера Vector Store.
Прежде чем запускать, убедитесь, что сервер доступен по адресу http://localhost:8007.

Запуск:
    pytest tests/live_api_tests.py -v
"""

import pytest
import uuid
import json
import time
from datetime import datetime, UTC
from typing import Dict, List, Tuple

from vector_store_client import VectorStoreClient
from vector_store_client.models import SearchResult

# Настройки
API_URL = "http://localhost:8007"
TEST_VECTOR_DIM = 384

# Тестовые данные
TEST_VECTOR = [0.1] * TEST_VECTOR_DIM
TEST_TEXT = "Это тестовый документ для проверки работы Vector Store API"
TEST_MODEL = {"name": "test-embedding-model"}


@pytest.fixture
async def api_client():
    """Создает экземпляр клиента, подключенного к реальному API."""
    async with VectorStoreClient(base_url=API_URL, timeout=10.0) as client:
        try:
            # Проверяем доступность сервера
            response = await client._make_request("health", {})
            print(f"Сервер доступен: {response['result']}")
            yield client
        except Exception as e:
            pytest.skip(f"Vector Store сервер недоступен: {e}")


@pytest.fixture
async def test_record(api_client) -> Tuple[str, Dict]:
    """Создает тестовую запись для использования в тестах и удаляет её после завершения."""
    # Уникальные метаданные для идентификации тестовых записей
    test_id = str(uuid.uuid4())
    metadata = {
        "source": "api_test",
        "test_id": test_id,
        "timestamp": datetime.now(UTC).isoformat()
    }
    
    # Создаем запись
    record_id = await api_client.create_record(
        vector=TEST_VECTOR,
        metadata=metadata
    )
    
    print(f"Создана тестовая запись с ID: {record_id}")
    
    yield record_id, metadata
    
    # Удаляем запись после теста
    try:
        await api_client.delete_records([record_id])
        print(f"Удалена тестовая запись: {record_id}")
    except Exception as e:
        print(f"Не удалось удалить тестовую запись {record_id}: {e}")


@pytest.mark.asyncio
async def test_health(api_client):
    """Проверка состояния сервера."""
    response = await api_client._make_request("health", {})
    assert "status" in response["result"]
    assert response["result"]["status"] == "ok"
    assert "version" in response["result"]
    assert "timestamp" in response["result"]
    
    print(f"Статус сервера: {response['result']['status']}, версия: {response['result']['version']}")


@pytest.mark.asyncio
async def test_create_record(api_client):
    """Проверка создания записи из вектора."""
    # Уникальные метаданные
    test_id = str(uuid.uuid4())
    metadata = {"source": "create_record_test", "test_id": test_id}
    
    # Создаем запись
    record_id = await api_client.create_record(
        vector=TEST_VECTOR,
        metadata=metadata
    )
    
    assert isinstance(record_id, str)
    assert uuid.UUID(record_id, version=4)  # Проверяем, что ID - валидный UUID
    
    # Проверяем, что запись действительно создана, запросив её метаданные
    fetched_metadata = await api_client.get_metadata(record_id)
    assert fetched_metadata["source"] == metadata["source"]
    assert fetched_metadata["test_id"] == test_id
    
    # Удаляем тестовую запись
    success = await api_client.delete_records([record_id])
    assert success is True


@pytest.mark.asyncio
async def test_create_text_record(api_client):
    """Проверка создания записи из текста с автоматической векторизацией."""
    # Уникальные метаданные
    test_id = str(uuid.uuid4())
    metadata = {"source": "create_text_record_test", "test_id": test_id}
    
    # Создаем запись из текста
    record_id = await api_client.create_text_record(
        text=TEST_TEXT,
        metadata=metadata,
        model=TEST_MODEL
    )
    
    assert isinstance(record_id, str)
    assert uuid.UUID(record_id, version=4)
    
    # Проверяем метаданные
    fetched_metadata = await api_client.get_metadata(record_id)
    assert fetched_metadata["source"] == metadata["source"]
    assert fetched_metadata["test_id"] == test_id
    
    # Проверяем, что текст сохранился
    fetched_text = await api_client.get_text(record_id)
    assert fetched_text == TEST_TEXT
    
    # Удаляем запись
    success = await api_client.delete_records([record_id])
    assert success is True


@pytest.mark.asyncio
async def test_search_by_vector(api_client, test_record):
    """Проверка поиска по вектору."""
    record_id, metadata = test_record
    
    # Ищем по тому же вектору - должны найти нашу запись
    results = await api_client.search_by_vector(
        vector=TEST_VECTOR,
        limit=5,
        include_vectors=True,
        include_metadata=True
    )
    
    assert len(results) > 0
    assert isinstance(results[0], SearchResult)
    
    # Проверяем, что наша запись есть в результатах
    found = False
    for result in results:
        if str(result.id) == record_id:
            found = True
            assert result.score > 0.9  # Должно быть высокое сходство
            assert result.metadata["test_id"] == metadata["test_id"]
            if result.vector:
                assert len(result.vector) == TEST_VECTOR_DIM
            break
    
    assert found, "Созданная запись не найдена в результатах поиска"


@pytest.mark.asyncio
async def test_search_by_text(api_client):
    """Проверка поиска по тексту."""
    # Создаем тестовую запись с текстом
    test_id = str(uuid.uuid4())
    unique_text = f"Уникальный текст для теста поиска {test_id}"
    metadata = {"source": "search_text_test", "test_id": test_id}
    
    record_id = await api_client.create_text_record(
        text=unique_text,
        metadata=metadata,
        model=TEST_MODEL
    )
    
    # Небольшая пауза, чтобы запись индексировалась
    time.sleep(1)
    
    # Ищем по части уникального текста
    search_query = "уникальный текст"
    results = await api_client.search_by_text(
        text=search_query,
        limit=5,
        model=TEST_MODEL["name"]  # Для поиска используем строковое имя модели
    )
    
    assert len(results) > 0
    
    # Проверяем, что наша запись найдена
    found = False
    for result in results:
        if str(result.id) == record_id:
            found = True
            assert result.score > 0  # Должно быть какое-то сходство
            break
    
    assert found, "Созданная запись не найдена в результатах поиска"
    
    # Удаляем запись
    await api_client.delete_records([record_id])


@pytest.mark.asyncio
async def test_filter_records(api_client):
    """Проверка фильтрации записей по метаданным."""
    # Создаем уникальный маркер для этого теста
    test_marker = str(uuid.uuid4())
    metadata = {
        "source": "filter_test",
        "test_marker": test_marker,
        "category": "test"
    }
    
    # Создаем несколько записей с одинаковыми метаданными
    record_ids = []
    for i in range(3):
        record_id = await api_client.create_text_record(
            text=f"Тестовый документ для фильтрации {i}",
            metadata=metadata
        )
        record_ids.append(record_id)
    
    # Фильтруем по уникальному маркеру
    results = await api_client.filter_records(
        criteria={"test_marker": test_marker}
    )
    
    # Должны найти все 3
    assert len(results) == 3
    
    # Фильтруем по комбинации полей
    results = await api_client.filter_records(
        criteria={
            "test_marker": test_marker,
            "category": "test"
        }
    )
    
    assert len(results) == 3
    
    # Фильтруем по несуществующему значению
    results = await api_client.filter_records(
        criteria={
            "test_marker": test_marker,
            "category": "nonexistent"
        }
    )
    
    assert len(results) == 0
    
    # Удаляем тестовые записи
    success = await api_client.delete_records(record_ids)
    assert success is True


@pytest.mark.asyncio
async def test_get_metadata(api_client, test_record):
    """Проверка получения метаданных по ID записи."""
    record_id, original_metadata = test_record
    
    # Получаем метаданные
    metadata = await api_client.get_metadata(record_id)
    
    # Проверяем поля
    assert metadata["source"] == original_metadata["source"]
    assert metadata["test_id"] == original_metadata["test_id"]
    assert "timestamp" in metadata


@pytest.mark.asyncio
async def test_get_text(api_client):
    """Проверка получения текста по ID записи."""
    # Создаем запись с текстом
    test_text = f"Тестовый текст {uuid.uuid4()}"
    metadata = {"source": "get_text_test"}
    
    record_id = await api_client.create_text_record(
        text=test_text,
        metadata=metadata
    )
    
    # Получаем текст
    fetched_text = await api_client.get_text(record_id)
    
    # Проверяем
    assert fetched_text == test_text
    
    # Удаляем запись
    await api_client.delete_records([record_id])


@pytest.mark.asyncio
async def test_delete_records(api_client):
    """Проверка удаления записей."""
    # Создаем тестовую запись
    metadata = {"source": "delete_test"}
    record_id = await api_client.create_record(
        vector=TEST_VECTOR,
        metadata=metadata
    )
    
    # Проверяем, что запись создана
    _ = await api_client.get_metadata(record_id)
    
    # Удаляем запись
    success = await api_client.delete_records([record_id])
    assert success is True
    
    # Проверяем, что запись удалена
    try:
        await api_client.get_metadata(record_id)
        # Если мы дошли сюда, значит запись не удалена
        assert False, "Запись не была удалена"
    except Exception as e:
        # Ожидаем ошибку, так как записи больше нет
        assert "not found" in str(e).lower() or "не найден" in str(e).lower()


@pytest.mark.asyncio
async def test_bulk_operations(api_client):
    """Проверка массовых операций."""
    # Создаем несколько записей
    record_ids = []
    batch_size = 5
    test_batch_id = str(uuid.uuid4())
    
    for i in range(batch_size):
        metadata = {
            "source": "bulk_test",
            "batch_id": test_batch_id,
            "index": i
        }
        
        record_id = await api_client.create_record(
            vector=TEST_VECTOR,
            metadata=metadata
        )
        record_ids.append(record_id)
    
    # Проверяем поиск - должны найти все созданные записи
    results = await api_client.search_by_vector(
        vector=TEST_VECTOR,
        limit=batch_size * 2  # С запасом
    )
    
    # Проверяем, что нашли наши записи
    found_count = 0
    for result in results:
        if str(result.id) in record_ids:
            found_count += 1
    
    assert found_count == batch_size, f"Найдено {found_count} из {batch_size} записей"
    
    # Удаляем все записи пакетом
    success = await api_client.delete_records(record_ids)
    assert success is True


@pytest.mark.asyncio
async def test_advanced_metadata_filtering(api_client):
    """Проверка расширенных возможностей фильтрации по метаданным."""
    # Создаем тестовые записи с различными метаданными
    test_group = str(uuid.uuid4())
    record_ids = []
    
    # Запись 1: числовое значение
    metadata1 = {
        "source": "filter_advanced_test",
        "group": test_group,
        "type": "numeric",
        "value": 100,
        "tags": ["test", "numeric", "high"]
    }
    record_id1 = await api_client.create_text_record(
        text="Документ с числовым значением 100",
        metadata=metadata1
    )
    record_ids.append(record_id1)
    
    # Запись 2: другое числовое значение
    metadata2 = {
        "source": "filter_advanced_test",
        "group": test_group,
        "type": "numeric",
        "value": 50,
        "tags": ["test", "numeric", "medium"]
    }
    record_id2 = await api_client.create_text_record(
        text="Документ с числовым значением 50",
        metadata=metadata2
    )
    record_ids.append(record_id2)
    
    # Запись 3: строковое значение
    metadata3 = {
        "source": "filter_advanced_test",
        "group": test_group,
        "type": "string",
        "value": "test_value",
        "tags": ["test", "string"]
    }
    record_id3 = await api_client.create_text_record(
        text="Документ со строковым значением",
        metadata=metadata3
    )
    record_ids.append(record_id3)
    
    try:
        # Тест 1: фильтрация по группе (все записи)
        results = await api_client.filter_records(
            criteria={"group": test_group}
        )
        assert len(results) == 3
        
        # Тест 2: фильтрация по типу
        results = await api_client.filter_records(
            criteria={"group": test_group, "type": "numeric"}
        )
        assert len(results) == 2
        
        # Тест 3: фильтрация по числовому значению
        results = await api_client.filter_records(
            criteria={"group": test_group, "value": 100}
        )
        assert len(results) == 1
        assert str(results[0].id) == record_id1
        
        # Тест 4: фильтрация по строковому значению
        results = await api_client.filter_records(
            criteria={"group": test_group, "value": "test_value"}
        )
        assert len(results) == 1
        assert str(results[0].id) == record_id3
        
        # Тест 5: фильтрация по тегам (если поддерживается)
        try:
            results = await api_client.filter_records(
                criteria={"group": test_group, "tags": "high"}
            )
            assert len(results) == 1
            assert str(results[0].id) == record_id1
        except Exception as e:
            print(f"Фильтрация по массивам не поддерживается: {e}")
    
    finally:
        # Удаляем тестовые записи
        await api_client.delete_records(record_ids)


@pytest.mark.asyncio
async def test_error_handling(api_client):
    """Проверка обработки ошибок."""
    # Тест 1: невалидный UUID
    try:
        await api_client.get_metadata("invalid-uuid")
        assert False, "Должно возникнуть исключение при невалидном UUID"
    except Exception as e:
        assert "invalid" in str(e).lower() or "неверный" in str(e).lower()
    
    # Тест 2: несуществующий ID
    nonexistent_id = str(uuid.uuid4())
    try:
        await api_client.get_metadata(nonexistent_id)
        assert False, "Должно возникнуть исключение при несуществующем ID"
    except Exception as e:
        assert "not found" in str(e).lower() or "не найден" in str(e).lower()
    
    # Тест 3: невалидный вектор
    try:
        await api_client.create_record(vector=[0.1] * 10)  # Неверная размерность
        assert False, "Должно возникнуть исключение при невалидном векторе"
    except Exception as e:
        assert "dimension" in str(e).lower() or "размерность" in str(e).lower()


if __name__ == "__main__":
    print("Запустите этот файл с помощью pytest: pytest tests/live_api_tests.py -v") 