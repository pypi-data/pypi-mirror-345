"""Integration tests for base Vector Store commands (help, health)."""

import pytest
from vector_store_client import VectorStoreClient

@pytest.mark.asyncio
async def test_help_command(client: VectorStoreClient):
    """Test help command returns list of available commands."""
    response = await client._make_request("help", {})
    
    # Проверяем структуру ответа
    assert "commands" in response["result"]
    commands = response["result"]["commands"]
    
    # Проверяем наличие всех команд из схемы
    expected_commands = {
        "help", "create_record", "add_vector", 
        "create_text_record", "add_text",
        "delete_records", "delete",
        "search_by_vector", "search_by_text", "search_text_records",
        "filter_records", "get_metadata", "get_text",
        "health"
    }
    
    actual_commands = set(commands.keys())
    assert expected_commands.issubset(actual_commands), \
        f"Missing commands: {expected_commands - actual_commands}"
    
    # Проверяем структуру описания команд
    for cmd_name, cmd_info in commands.items():
        assert "summary" in cmd_info
        assert "description" in cmd_info
        assert "params_count" in cmd_info
        assert isinstance(cmd_info["params_count"], int)

@pytest.mark.asyncio
async def test_health_check(client: VectorStoreClient):
    """Test health check command."""
    response = await client._make_request("health", {})
    
    # Проверяем что сервис отвечает
    assert "result" in response
    health_info = response["result"]
    
    # Проверяем основные поля статуса
    assert "status" in health_info
    assert health_info["status"] in ["ok", "error"]
    
    if health_info["status"] == "ok":
        # Если статус ok, проверяем дополнительную информацию
        assert "version" in health_info
        assert "uptime" in health_info
        # Можно добавить проверки других полей, если они определены в API 