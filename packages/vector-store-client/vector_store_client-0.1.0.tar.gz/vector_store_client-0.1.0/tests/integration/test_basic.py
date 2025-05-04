"""Basic integration tests for Vector Store Client."""

import pytest
from typing import Dict, List
from uuid import uuid4

from vector_store_client import VectorStoreClient

# Test data
TEST_VECTOR = [0.1] * 384
TEST_TEXT = "Test document for integration testing"
TEST_METADATA = {"source": "integration_test", "test_id": str(uuid4())}

@pytest.mark.asyncio
# @pytest.mark.skip("Requires running Vector Store server")
async def test_create_and_search(client: VectorStoreClient):
    """Test basic record creation and search workflow."""
    # Create record
    record_id = await client.create_record(
        vector=TEST_VECTOR,
        metadata=TEST_METADATA
    )
    
    # Verify record exists and metadata matches
    metadata = await client.get_metadata(record_id)
    assert metadata["source"] == TEST_METADATA["source"]
    assert metadata["test_id"] == TEST_METADATA["test_id"]
    
    # Search by vector
    results = await client.search_by_vector(
        vector=TEST_VECTOR,
        limit=5
    )
    
    # First result should be the record we just created
    assert len(results) > 0
    assert str(results[0].id) == record_id
    assert results[0].score > 0.9  # High similarity expected with identical vector
    
    # Clean up - delete the test record
    success = await client.delete_records([record_id])
    assert success is True 