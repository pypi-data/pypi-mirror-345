import pytest
from vector_store_client import VectorStoreClient, ValidationError, JsonRpcException

@pytest.mark.asyncio
def make_client_with_schema(schema):
    client = VectorStoreClient(base_url="http://test")
    client.schema = schema
    return client

@pytest.mark.asyncio
async def test_call_command_success(mocker):
    schema = {
        "commands": {
            "create_record": {
                "params": {
                    "vector": {"type": "array", "required": True},
                    "metadata": {"type": "object", "required": False}
                }
            }
        }
    }
    client = make_client_with_schema(schema)
    mocker.patch.object(client, "_make_request", return_value={"result": "ok"})
    result = await client.call_command("create_record", vector=[0.1]*384)
    assert result == "ok"

@pytest.mark.asyncio
async def test_call_command_invalid_params(mocker):
    schema = {
        "commands": {
            "create_record": {
                "params": {
                    "vector": {"type": "array", "required": True}
                }
            }
        }
    }
    client = make_client_with_schema(schema)
    with pytest.raises(ValidationError):
        await client.call_command("create_record", metadata={})  # vector отсутствует

@pytest.mark.asyncio
async def test_call_command_unknown_command(mocker):
    schema = {"commands": {"create_record": {"params": {}}}}
    client = make_client_with_schema(schema)
    with pytest.raises(ValidationError):
        await client.call_command("unknown_command", foo=1)

@pytest.mark.asyncio
async def test_call_command_server_error(mocker):
    schema = {"commands": {"create_record": {"params": {"vector": {"type": "array", "required": True}}}}}
    client = make_client_with_schema(schema)
    # Используем функцию, которая выбрасывает исключение
    def raise_jsonrpc_exception(*a, **kw):
        raise JsonRpcException({"code": -32000, "message": "Server error"})
    mocker.patch.object(client, "_make_request", side_effect=raise_jsonrpc_exception)
    with pytest.raises(JsonRpcException):
        await client.call_command("create_record", vector=[0.1]*384) 