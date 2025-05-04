import pytest
import httpx
from vector_store_client import VectorStoreClient, ValidationError, ConnectionError

@pytest.mark.asyncio
async def test_load_schema_success(mocker):
    schema = {"commands": {"create_record": {"params": {}}}}
    mock_get = mocker.patch.object(
        httpx.AsyncClient, "get",
        return_value=httpx.Response(
            status_code=200,
            json=schema,
            request=httpx.Request("GET", "http://test/api/commands")
        )
    )
    client = VectorStoreClient(base_url="http://test")
    await client.load_schema()
    assert client.schema == schema
    mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_load_schema_invalid_schema(mocker):
    # Нет ключа 'commands'
    bad_schema = {"not_commands": {}}
    mocker.patch.object(
        httpx.AsyncClient, "get",
        return_value=httpx.Response(
            status_code=200,
            json=bad_schema,
            request=httpx.Request("GET", "http://test/api/commands")
        )
    )
    client = VectorStoreClient(base_url="http://test")
    with pytest.raises(ConnectionError):
        await client.load_schema()

@pytest.mark.asyncio
async def test_load_schema_server_unavailable(mocker):
    mocker.patch.object(
        httpx.AsyncClient, "get",
        side_effect=httpx.ConnectError("Server unavailable")
    )
    client = VectorStoreClient(base_url="http://test")
    with pytest.raises(ConnectionError):
        await client.load_schema() 