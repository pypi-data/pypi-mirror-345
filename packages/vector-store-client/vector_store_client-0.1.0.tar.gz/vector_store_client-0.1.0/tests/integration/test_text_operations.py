"""Integration tests for text-based operations."""

import pytest
from typing import Dict, List
from uuid import uuid4

from vector_store_client import VectorStoreClient

# Test data
TEST_TEXT = "This is a sample document for testing text operations in Vector Store"
TEST_METADATA = {"source": "integration_test_text", "test_id": str(uuid4())}

@pytest.mark.asyncio
# @pytest.mark.skip("Requires running Vector Store server")
async def test_create_text_and_search(client: VectorStoreClient):
    """Test text-based record creation and search workflow."""
    # Create record from text
    record_id = await client.create_text_record(
        text=TEST_TEXT,
        metadata=TEST_METADATA
    )
    
    # Verify record exists
    metadata = await client.get_metadata(record_id)
    assert metadata["source"] == TEST_METADATA["source"]
    
    # Get original text
    text = await client.get_text(record_id)
    assert text == TEST_TEXT
    
    # Search by text
    search_query = "sample document"
    results = await client.search_by_text(
        text=search_query,
        limit=5
    )
    
    # Should find our record
    assert len(results) > 0
    found = False
    for result in results:
        if str(result.id) == record_id:
            found = True
            break
    assert found, "Created record not found in search results"
    
    # Clean up
    success = await client.delete_records([record_id])
    assert success is True

@pytest.mark.asyncio
# @pytest.mark.skip("Requires running Vector Store server")
async def test_filter_by_metadata(client: VectorStoreClient):
    """Test filtering records by metadata."""
    # Create unique marker for this test run
    test_marker = str(uuid4())
    metadata = {
        "source": "integration_test",
        "test_marker": test_marker,
        "category": "test"
    }
    
    # Create multiple records
    record_ids = []
    for i in range(3):
        record_id = await client.create_text_record(
            text=f"Test document {i}",
            metadata=metadata
        )
        record_ids.append(record_id)
    
    # Filter by our unique marker
    results = await client.filter_records(
        criteria={"test_marker": test_marker}
    )
    
    # Should find exactly our 3 records
    assert len(results) == 3
    
    # Clean up
    success = await client.delete_records(record_ids)
    assert success is True 