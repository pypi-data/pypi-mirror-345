"""Custom exceptions for Vector Store Client."""

from typing import Dict, Optional
from pydantic import BaseModel

class VectorStoreError(Exception):
    """Base exception class for Vector Store Client."""
    pass

class ConnectionError(VectorStoreError):
    """Raised when API is unreachable."""
    pass

class TimeoutError(VectorStoreError):
    """Raised when request times out."""
    pass

class ValidationError(VectorStoreError):
    """Raised when input validation fails."""
    pass

class JsonRpcException(VectorStoreError):
    """Raised when API returns an error response."""
    def __init__(self, error, message: Optional[str] = None):
        # If already our JsonRpcException, just copy fields
        if isinstance(error, JsonRpcException):
            self.code = error.code
            self.message = error.message
            self.data = getattr(error, 'data', None)
            super().__init__(self.message)
            return
        # If pydantic model
        if isinstance(error, BaseModel):
            error = error.model_dump()
        # If dict
        if isinstance(error, dict):
            self.code = error.get("code")
            self.message = message or error.get("message")
            self.data = error.get("data")
            super().__init__(self.message)
            return
        raise TypeError(f"Invalid error type for JsonRpcException: {type(error)}")

class AuthenticationError(VectorStoreError):
    """Raised when authentication fails."""
    pass

class ResourceNotFoundError(VectorStoreError):
    """Raised when requested resource is not found."""
    pass

class DuplicateError(VectorStoreError):
    """Raised when trying to create duplicate resource."""
    pass

class ServerError(VectorStoreError):
    """Raised when server encounters an error."""
    pass

class RateLimitError(VectorStoreError):
    """Raised when rate limit is exceeded."""
    pass

class InvalidRequestError(VectorStoreError):
    """Raised when request is invalid."""
    pass 