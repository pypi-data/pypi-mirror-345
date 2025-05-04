"""Fixtures for integration tests."""

import pytest
import asyncio
from typing import AsyncGenerator, Optional
from vector_store_client import VectorStoreClient

# Configuration
TEST_SERVER = "http://localhost:8007"
TEST_TIMEOUT = 10.0
TEST_VECTOR_DIM = 384

@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client() -> AsyncGenerator[VectorStoreClient, None]:
    """Create client instance connected to test server."""
    async with VectorStoreClient(
        base_url=TEST_SERVER,
        timeout=TEST_TIMEOUT
    ) as client:
        # Check server availability
        try:
            await client._make_request("health", {})
        except Exception as e:
            pytest.skip(f"Vector Store server not available: {e}")
        yield client 