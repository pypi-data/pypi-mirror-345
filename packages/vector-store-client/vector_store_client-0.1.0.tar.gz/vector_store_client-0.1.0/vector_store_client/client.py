"""Vector Store Client implementation.

This module provides the main client class for interacting with the Vector Store API.
"""

import logging
from typing import Dict, List, Optional, Union
from uuid import UUID
import httpx
from datetime import datetime
from .models import JsonRpcRequest, JsonRpcResponse, SearchResult, VectorRecord
from .exceptions import ValidationError, JsonRpcException, ConnectionError, TimeoutError
import json
import jsonschema

logger = logging.getLogger(__name__)

class VectorStoreClient:
    """Client for interacting with Vector Store API."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8007",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        async_client: Optional[httpx.AsyncClient] = None
    ):
        """Initialize Vector Store client.
        
        Args:
            base_url: Base URL of the Vector Store API
            timeout: Request timeout in seconds
            headers: Optional custom headers
            async_client: Optional pre-configured async HTTP client
        """
        self.base_url = base_url.rstrip('/')
        self._timeout = timeout
        self._headers = headers or {}
        self._client = async_client or httpx.AsyncClient(
            timeout=timeout,
            headers=self._headers
        )
        self.schema = None

    async def load_schema(self):
        """Loads the API command schema from the server."""
        try:
            resp = await self._client.get(f"{self.base_url}/api/commands")
            resp.raise_for_status()
            self.schema = resp.json()
            if not self.schema or "commands" not in self.schema:
                raise ValidationError("Invalid or empty API schema from server")
        except Exception as e:
            raise ConnectionError(f"Failed to load API schema: {e}")

    @classmethod
    async def create(cls, *args, **kwargs):
        """Async constructor that loads schema and returns ready client."""
        self = cls(*args, **kwargs)
        await self.load_schema()
        return self

    async def create_record(
        self,
        vector: List[float],
        metadata: Optional[Dict] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        **kwargs
    ) -> str:
        """Creates a new record with vector and metadata.
        
        Args:
            vector: Vector data as list of floats
            metadata: Optional metadata dictionary
            session_id: Optional session ID
            message_id: Optional message ID
            timestamp: Optional timestamp
            **kwargs: Additional parameters
            
        Returns:
            Record ID as string
            
        Raises:
            ValidationError: If vector dimensions are invalid
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error
        """
        if len(vector) != 384:
            raise ValidationError("Vector must have 384 dimensions")
            
        params = {
            "vector": vector,
            "metadata": metadata or {},
            **kwargs
        }
        
        if session_id:
            try:
                UUID(session_id)
                params["session_id"] = session_id
            except ValueError:
                raise ValidationError("Invalid session_id format")
                
        if message_id:
            try:
                UUID(message_id)
                params["message_id"] = message_id
            except ValueError:
                raise ValidationError("Invalid message_id format")
                
        if timestamp:
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                params["timestamp"] = timestamp
            except ValueError:
                raise ValidationError("Invalid timestamp format")
        
        response = await self._make_request(
            "create_record",
            params
        )
        return str(response["result"])

    async def create_text_record(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        model: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        **kwargs
    ) -> str:
        """Creates a new record from text with automatic vectorization.
        
        Args:
            text: Text to vectorize
            metadata: Optional metadata dictionary
            model: Optional model name for vectorization
            session_id: Optional session ID
            message_id: Optional message ID
            timestamp: Optional timestamp
            **kwargs: Additional parameters
            
        Returns:
            Record ID as string
        """
        params = {
            "text": text,
            "metadata": metadata or {},
            **kwargs
        }
        
        if model:
            params["model"] = model
            
        if session_id:
            try:
                UUID(session_id)
                params["session_id"] = session_id
            except ValueError:
                raise ValidationError("Invalid session_id format")
                
        if message_id:
            try:
                UUID(message_id)
                params["message_id"] = message_id
            except ValueError:
                raise ValidationError("Invalid message_id format")
                
        if timestamp:
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                params["timestamp"] = timestamp
            except ValueError:
                raise ValidationError("Invalid timestamp format")
        
        response = await self._make_request(
            "create_text_record",
            params
        )
        return str(response["result"])

    async def search_by_vector(
        self,
        vector: List[float],
        limit: int = 5,
        include_vectors: bool = False,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """Search for records by vector similarity.
        
        Args:
            vector: Query vector
            limit: Maximum number of results
            include_vectors: Whether to include vectors in results
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of search results
        """
        if len(vector) != 384:
            raise ValidationError("Query vector must have 384 dimensions")
            
        params = {
            "vector": vector,
            "limit": limit,
            "include_vectors": include_vectors,
            "include_metadata": include_metadata
        }
        
        response = await self._make_request(
            "search_by_vector",
            params
        )
        return [SearchResult(**r) for r in response["result"]]

    async def search_by_text(
        self,
        text: str,
        limit: int = 5,
        model: Optional[str] = None,
        include_vectors: bool = False,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """Search for records by text similarity.
        
        Args:
            text: Query text
            limit: Maximum number of results
            model: Optional model name for vectorization
            include_vectors: Whether to include vectors in results
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of search results
        """
        params = {
            "text": text,
            "limit": limit,
            "include_vectors": include_vectors,
            "include_metadata": include_metadata
        }
        
        if model:
            params["model"] = model
        
        response = await self._make_request(
            "search_by_text",
            params
        )
        return [SearchResult(**r) for r in response["result"]]

    async def filter_records(
        self,
        criteria: Dict,
        limit: int = 100,
        include_vectors: bool = False,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """Filter records by metadata criteria.
        
        Args:
            criteria: Filter criteria
            limit: Maximum number of results
            include_vectors: Whether to include vectors in results
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of filtered results
        """
        params = {
            "criteria": criteria,
            "limit": limit,
            "include_vectors": include_vectors,
            "include_metadata": include_metadata
        }
        
        response = await self._make_request(
            "filter_records",
            params
        )
        
        results = []
        for r in response["result"]:
            # Add default score if not present
            if "score" not in r:
                r["score"] = 1.0
            results.append(SearchResult(**r))
            
        return results

    async def get_metadata(self, record_id: str) -> Dict:
        """Get metadata for a record by its ID."""
        try:
            UUID(record_id)
        except ValueError:
            raise ValidationError("Invalid record_id format")
            
        params = {"record_id": record_id}
        response = await self._make_request("get_metadata", params)
        return response["result"]

    async def get_text(self, record_id: str) -> str:
        """Get text for a record by its ID."""
        try:
            UUID(record_id)
        except ValueError:
            raise ValidationError("Invalid record_id format")
            
        params = {"record_id": record_id}
        response = await self._make_request("get_text", params)
        return response["result"]

    async def delete_records(self, record_ids: List[str]) -> bool:
        """Delete records by their IDs."""
        for record_id in record_ids:
            try:
                UUID(record_id)
            except ValueError:
                raise ValidationError(f"Invalid record_id format: {record_id}")
                
        params = {"record_ids": record_ids}
        response = await self._make_request("delete_records", params)
        return bool(response["result"])

    async def _make_request(
        self,
        method: str,
        params: Dict
    ) -> Dict:
        """Make JSON-RPC request to API.
        
        Args:
            method: RPC method name
            params: Method parameters
            
        Returns:
            Response data
            
        Raises:
            ConnectionError: If API is unreachable
            TimeoutError: If request times out
            JsonRpcException: If API returns an error
        """
        request = JsonRpcRequest(
            method=method,
            params=params
        )
        
        try:
            response = await self._client.post(
                f"{self.base_url}/cmd",
                json=request.model_dump()
            )
            response.raise_for_status()
            
            rpc_response = JsonRpcResponse(**response.json())
            if rpc_response.error:
                raise JsonRpcException(rpc_response.error)
                
            return rpc_response.model_dump()
            
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}")
        except httpx.HTTPError as e:
            raise ConnectionError(f"HTTP error occurred: {e}")
            
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()

    async def call_command(self, command: str, **params):
        """Call a command defined in the loaded schema with parameter validation.
        Args:
            command: Command name (as in schema)
            **params: Parameters for the command
        Returns:
            Result of the command
        Raises:
            ValidationError: If command or parameters are invalid
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error
        """
        if not self.schema or "commands" not in self.schema:
            raise ValidationError("API schema is not loaded. Use VectorStoreClient.create() or load_schema().")
        if command not in self.schema["commands"]:
            raise ValidationError(f"Unknown command: {command}")
        # Формируем JSON Schema для параметров
        cmd_info = self.schema["commands"][command]
        param_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        for pname, pinfo in cmd_info.get("params", {}).items():
            param_schema["properties"][pname] = {"type": pinfo.get("type", "string")}
            if pinfo.get("required", False):
                param_schema["required"].append(pname)
        # Валидация параметров
        try:
            jsonschema.validate(instance=params, schema=param_schema)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Parameter validation error for command '{command}': {e.message}")
        # Отправка команды
        response = await self._make_request(command, params)
        return response["result"] 