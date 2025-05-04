"""Vector Store Client package."""

from .client import VectorStoreClient
from .models import (
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcError,
    VectorRecord,
    SearchResult
)
from .exceptions import (
    VectorStoreError,
    ConnectionError,
    TimeoutError,
    ValidationError,
    JsonRpcException,
    AuthenticationError,
    ResourceNotFoundError,
    DuplicateError,
    ServerError,
    RateLimitError,
    InvalidRequestError
)
from .types import (
    MetadataDict,
    FilterCriteria,
    SearchOptions
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    # Client
    "VectorStoreClient",
    
    # Models
    "JsonRpcRequest",
    "JsonRpcResponse",
    # "JsonRpcError",  # Only for model, not for exceptions
    "VectorRecord",
    "SearchResult",
    
    # Exceptions
    "VectorStoreError",
    "ConnectionError",
    "TimeoutError",
    "ValidationError",
    "JsonRpcException",
    "AuthenticationError",
    "ResourceNotFoundError",
    "DuplicateError",
    "ServerError",
    "RateLimitError",
    "InvalidRequestError",
    
    # Types
    "MetadataDict",
    "FilterCriteria",
    "SearchOptions"
] 