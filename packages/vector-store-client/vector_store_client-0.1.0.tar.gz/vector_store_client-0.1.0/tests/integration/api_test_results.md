# Результаты тестирования API Vector Store

## Тестирование help
```python
await client._make_request("help", {})
```
**Проблемы:**
1. Не работает детализация по командам
2. Описание команд дублирует summary
3. Не показывает параметры команд

## Тестируем каждую команду

### 1. create_record
```python
# Минимальный набор
await client._make_request("create_record", {
    "vector": [0.1] * 384
})
```
**Результат:** Ошибка 500
```json
{
    "error": {
        "code": 500,
        "message": "Error executing command 'create_record': Parameter 'vector' must be a 384-dimensional list of floats.",
        "details": "Error executing command 'create_record': Error executing command 'create_record': Parameter 'vector' must be a 384-dimensional list of floats."
    }
}
```

**Проблемы:**
1. Ошибка дублируется в сообщении трижды
2. Сообщение об ошибке не информативно - вектор как раз 384-мерный
3. Нет информации о других обязательных параметрах

```python
# С метаданными
await client._make_request("create_record", {
    "vector": [0.1] * 384,
    "metadata": {"test": "test"}
})
```
**Результат:** Та же ошибка 500

### 2. add_vector
```python
# Пробуем то же самое с add_vector
await client._make_request("add_vector", {
    "vector": [0.1] * 384,
    "metadata": {"test": "test"}
})
```
**Результат:** Та же ошибка 500, но с другим именем команды
```json
{
    "error": {
        "code": 500,
        "message": "Error executing command 'add_vector': Parameter 'vector' must be a 384-dimensional list of floats.",
        "details": "Error executing command 'add_vector': Error executing command 'add_vector': Parameter 'vector' must be a 384-dimensional list of floats."
    }
}
```

**Проблемы:**
1. Команда ведет себя идентично create_record
2. Нет документации о различиях между командами
3. Одинаковые ошибки с разными именами команд

### 3. create_text_record
```python
# Минимальный набор
await client._make_request("create_text_record", {
    "text": "Test document"
})
```
**Результат:** Успех
```json
{
    "result": "39388fe8-4c25-475e-b863-c8b8e1040a00"
}
```

**Особенности:**
1. В отличие от векторных команд, работает с минимальным набором параметров
2. Автоматически создает вектор из текста
3. Возвращает UUID записи

### 4. add_text
```python
# Пробуем то же самое с add_text
await client._make_request("add_text", {
    "text": "Test document"
})
```
**Результат:** Успех
```json
{
    "result": "77fe94e3-3d6d-48c6-a9d7-f718c8471d7e"
}
```

**Особенности:**
1. Команда ведет себя идентично create_text_record
2. Нет документации о различиях между командами
3. Успешно создает запись с тем же набором параметров

### 5. search_by_vector
```python
# Минимальный набор
await client._make_request("search_by_vector", {
    "vector": [0.1] * 384
})
```
**Результат:** Ошибка 500
```json
{
    "error": {
        "code": 500,
        "message": "Error executing command 'search_by_vector': Vector must be a 384-dimensional list",
        "details": "Error executing command 'search_by_vector': Error executing command 'search_by_vector': Vector must be a 384-dimensional list"
    }
}
```

**Проблемы:**
1. Та же проблема с размерностью вектора, что и в create_record
2. Ошибка дублируется в сообщении
3. Нет информации о других параметрах (limit, include_vectors, include_metadata)

### 6. search_by_text
```python
# Минимальный набор
await client._make_request("search_by_text", {
    "text": "Test document"
})
```
**Результат:** Успех
```json
{
    "result": [
        {
            "id": "39388fe8-4c25-475e-b863-c8b8e1040a00",
            "score": 1.0,
            "distance": 0.0,
            "metadata": {
                "text": "Test document",
                "timestamp": "2025-05-02T05:30:35Z",
                "created_at": "2025-05-02T05:30:35Z",
                "updated_at": "2025-05-02T05:30:35Z"
            }
        },
        {
            "id": "77fe94e3-3d6d-48c6-a9d7-f718c8471d7e",
            "score": 1.0,
            "distance": 0.0,
            "metadata": {
                "text": "Test document",
                "timestamp": "2025-05-02T05:30:52Z",
                "created_at": "2025-05-02T05:30:52Z",
                "updated_at": "2025-05-02T05:30:52Z"
            }
        },
        {
            "id": "b01874fd-2222-4425-a790-cf3266a84c2e",
            "score": 0.0,
            "distance": 4.766139030456543,
            "metadata": {
                "source": "integration_test",
                "test_marker": "1d7d1b1b-1004-4ecd-9be9-6c8ff0713f24",
                "category": "test",
                "text": "Test document 1",
                "timestamp": "2025-05-02T04:48:19Z",
                "created_at": "2025-05-02T04:48:19Z",
                "updated_at": "2025-05-02T04:48:19Z"
            }
        }
    ]
}
```

**Особенности:**
1. Работает с минимальным набором параметров
2. Возвращает массив результатов с score и distance
3. Включает метаданные по умолчанию
4. Сортирует по релевантности (score)
5. Показывает как точные совпадения (score=1.0), так и частичные (score=0.0)

### 7. search_text_records
```python
# Минимальный набор
await client._make_request("search_text_records", {
    "text": "Test document"
})
```
**Результат:** Идентичен search_by_text
```json
{
    "result": [
        {
            "id": "39388fe8-4c25-475e-b863-c8b8e1040a00",
            "score": 1.0,
            "distance": 0.0,
            "metadata": {
                "text": "Test document",
                "timestamp": "2025-05-02T05:30:35Z",
                "created_at": "2025-05-02T05:30:35Z",
                "updated_at": "2025-05-02T05:30:35Z"
            }
        },
        {
            "id": "77fe94e3-3d6d-48c6-a9d7-f718c8471d7e",
            "score": 1.0,
            "distance": 0.0,
            "metadata": {
                "text": "Test document",
                "timestamp": "2025-05-02T05:30:52Z",
                "created_at": "2025-05-02T05:30:52Z",
                "updated_at": "2025-05-02T05:30:52Z"
            }
        },
        {
            "id": "b01874fd-2222-4425-a790-cf3266a84c2e",
            "score": 0.0,
            "distance": 4.766139030456543,
            "metadata": {
                "source": "integration_test",
                "test_marker": "1d7d1b1b-1004-4ecd-9be9-6c8ff0713f24",
                "category": "test",
                "text": "Test document 1",
                "timestamp": "2025-05-02T04:48:19Z",
                "created_at": "2025-05-02T04:48:19Z",
                "updated_at": "2025-05-02T04:48:19Z"
            }
        }
    ]
}
```

**Проблемы:**
1. Команда возвращает те же результаты, что и search_by_text
2. Нет документации о различиях между командами
3. Непонятно, зачем нужны обе команды, если они делают одно и то же

### 8. filter_records
```python
# Минимальный набор
await client._make_request("filter_records", {
    "criteria": {"text": "Test document"}
})
```
**Результат:** Успех, но формат отличается от поисковых команд
```json
{
    "result": [
        {
            "id": "39388fe8-4c25-475e-b863-c8b8e1040a00",
            "metadata": {
                "text": "Test document",
                "timestamp": "2025-05-02T05:30:35Z",
                "created_at": "2025-05-02T05:30:35Z",
                "updated_at": "2025-05-02T05:30:35Z"
            }
        },
        {
            "id": "77fe94e3-3d6d-48c6-a9d7-f718c8471d7e",
            "metadata": {
                "text": "Test document",
                "timestamp": "2025-05-02T05:30:52Z",
                "created_at": "2025-05-02T05:30:52Z",
                "updated_at": "2025-05-02T05:30:52Z"
            }
        }
    ]
}
```

**Особенности:**
1. В отличие от поисковых команд, не возвращает score и distance
2. Возвращает только точные совпадения по критериям
3. Работает как точный фильтр по метаданным, а не семантический поиск

### 9. get_metadata
```python
# Используем ID из предыдущих тестов
await client._make_request("get_metadata", {
    "record_id": "39388fe8-4c25-475e-b863-c8b8e1040a00"
})
```
**Результат:** Успех
```json
{
    "result": {
        "text": "Test document",
        "timestamp": "2025-05-02T05:30:35Z",
        "created_at": "2025-05-02T05:30:35Z",
        "updated_at": "2025-05-02T05:30:35Z"
    }
}
```

**Особенности:**
1. Возвращает только метаданные без ID записи
2. Формат ответа отличается от других команд
3. Требует точный UUID записи

### 10. get_text
```python
# Используем тот же ID
await client._make_request("get_text", {
    "record_id": "39388fe8-4c25-475e-b863-c8b8e1040a00"
})
```
**Результат:** Успех
```json
{
    "result": "Test document"
}
```

**Особенности:**
1. Возвращает только текст без метаданных
2. Самый простой формат ответа
3. Требует точный UUID записи

### 11. delete_records
```python
# Удаляем запись
await client._make_request("delete_records", {
    "record_ids": ["39388fe8-4c25-475e-b863-c8b8e1040a00"]
})
```
**Результат:** Успех
```json
{
    "result": {
        "deleted": ["39388fe8-4c25-475e-b863-c8b8e1040a00"],
        "not_found": []
    }
}
```

**Особенности:**
1. Поддерживает массовое удаление
2. Возвращает информацию об успешно удаленных и ненайденных записях
3. Требует точные UUID записей

### 12. delete
```python
# Пробуем удалить ту же запись через алиас
await client._make_request("delete", {
    "record_ids": ["39388fe8-4c25-475e-b863-c8b8e1040a00"]
})