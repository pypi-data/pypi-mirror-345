"""Type definitions for Vector Store Client."""

from typing import Dict, List, TypedDict, Optional, Union
from datetime import datetime
from uuid import UUID

class MetadataDict(TypedDict, total=False):
    """Type for record metadata."""
    text: Optional[str]
    model: Optional[str]
    source: Optional[str]
    tags: Optional[List[str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    session_id: Optional[UUID]
    message_id: Optional[UUID]
    timestamp: Optional[str]
    type: Optional[str]
    version: Optional[Union[str, int]]
    language: Optional[str]
    encoding: Optional[str]
    mime_type: Optional[str]
    size: Optional[int]
    checksum: Optional[str]
    url: Optional[str]
    author: Optional[str]
    title: Optional[str]
    description: Optional[str]
    category: Optional[str]
    status: Optional[str]
    priority: Optional[int]
    expires_at: Optional[datetime]
    custom: Optional[Dict]

class FilterCriteria(TypedDict, total=False):
    """Type for filter criteria."""
    text: Optional[str]
    model: Optional[str]
    source: Optional[str]
    tags: Optional[List[str]]
    type: Optional[str]
    created_at: Optional[Dict[str, datetime]]  # {"$gt": datetime, "$lt": datetime}
    updated_at: Optional[Dict[str, datetime]]
    session_id: Optional[UUID]
    message_id: Optional[UUID]
    version: Optional[Union[str, int, Dict[str, Union[str, int]]]]
    language: Optional[str]
    category: Optional[str]
    status: Optional[str]
    priority: Optional[Union[int, Dict[str, int]]]
    custom: Optional[Dict]

class SearchOptions(TypedDict, total=False):
    """Type for search options."""
    limit: Optional[int]
    offset: Optional[int]
    min_score: Optional[float]
    include_vectors: Optional[bool]
    include_metadata: Optional[bool]
    sort_by: Optional[str]
    sort_order: Optional[str]
    filter: Optional[FilterCriteria]

# Type aliases for common types
Vector = List[float]
RecordId = str
JsonRpcId = Union[str, int, None]
JsonRpcParams = Dict
JsonRpcResult = Union[Dict, List, str, int, float, bool, None]
JsonRpcError = Dict[str, Union[int, str, Dict]] 