# Vector Store Client

[![PyPI version](https://badge.fury.io/py/vector-store-client.svg)](https://badge.fury.io/py/vector-store-client)
[![Python versions](https://img.shields.io/pypi/pyversions/vector-store-client.svg)](https://pypi.org/project/vector-store-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Асинхронный Python клиент для работы с Vector Store API. Предоставляет удобный интерфейс для хранения и поиска векторных представлений.

[English documentation](README.md)

## Особенности

- ✨ Полностью асинхронный API
- 🔍 Поиск по векторам и тексту
- 📝 Автоматическая векторизация текста
- 🛡️ Строгая типизация
- 🧪 Полное тестовое покрытие
- 📚 Подробная документация

## Установка

```bash
pip install vector-store-client
```

## Быстрый старт

```python
from vector_store_client import VectorStoreClient

async def main():
    # Инициализация клиента
    client = VectorStoreClient(base_url="http://localhost:8007")
    
    # Создание записи из текста
    record_id = await client.create_text_record(
        text="Пример текста для векторизации",
        metadata={"source": "example"}
    )
    
    # Поиск похожих записей
    results = await client.search_by_text(
        text="похожий текст",
        limit=5
    )
    
    for result in results:
        print(f"Схожесть: {result.score}, Текст: {result.text}")

```

## Документация

Подробная документация доступна на [Read the Docs](https://vector-store-client.readthedocs.io/).

### Основные операции

#### Создание записей

```python
# Создание из вектора
record_id = await client.create_record(
    vector=[0.1, 0.2, ...],  # 384-мерный вектор
    metadata={"key": "value"}
)

# Создание из текста
record_id = await client.create_text_record(
    text="Пример текста",
    metadata={"source": "example"},
    model="default"  # опционально
)
```

#### Поиск

```python
# Поиск по вектору
results = await client.search_by_vector(
    vector=[0.1, 0.2, ...],
    limit=5
)

# Поиск по тексту
results = await client.search_by_text(
    text="поисковый запрос",
    limit=5
)

# Фильтрация по метаданным
results = await client.filter_records(
    criteria={"source": "example"},
    limit=10
)
```

## Разработка

### Установка зависимостей для разработки

```bash
pip install -e ".[dev]"
```

### Запуск тестов

```bash
pytest
```

### Линтинг и форматирование

```bash
# Форматирование кода
black .
isort .

# Проверка типов
mypy .

# Линтинг
ruff check .
```

## Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE). 