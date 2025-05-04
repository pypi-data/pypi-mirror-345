"""Data models for Vector Store Client."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class JsonRpcRequest(BaseModel):
    """Base model for JSON-RPC requests."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name to call")
    params: Dict = Field(default_factory=dict, description="Method parameters")
    id: Optional[Union[str, int]] = Field(default=None, description="Request identifier")

class JsonRpcError(BaseModel):
    """JSON-RPC error object."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Dict] = Field(default=None, description="Additional error data")

class JsonRpcResponse(BaseModel):
    """Base model for JSON-RPC responses."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    result: Optional[Union[Dict, List, str, bool]] = Field(default=None, description="Method execution result")
    error: Optional[JsonRpcError] = Field(default=None, description="Error information")
    id: Optional[Union[str, int]] = Field(default=None, description="Request identifier")

class VectorRecord(BaseModel):
    """Model for vector records."""
    id: UUID = Field(..., description="Unique record identifier")
    vector: List[float] = Field(..., description="Vector data")
    metadata: Dict = Field(default_factory=dict, description="Record metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    text: Optional[str] = Field(default=None, description="Original text if created from text")
    model: Optional[str] = Field(default=None, description="Model used for vectorization")
    session_id: Optional[UUID] = Field(default=None, description="Session identifier")
    message_id: Optional[UUID] = Field(default=None, description="Message identifier")

class SearchResult(BaseModel):
    """Model for search results."""
    id: UUID = Field(..., description="Record identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    vector: Optional[List[float]] = Field(default=None, description="Vector data if requested")
    metadata: Optional[Dict] = Field(default=None, description="Record metadata if requested")
    text: Optional[str] = Field(default=None, description="Original text if available")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp") 