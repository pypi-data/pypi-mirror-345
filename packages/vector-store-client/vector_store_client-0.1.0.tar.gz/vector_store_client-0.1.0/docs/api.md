# Vector Store Client API Reference

## Client

### VectorStoreClient

Main client class for interacting with Vector Store API.

#### Methods

##### create_record
Creates a new record with vector and metadata.

```python
async def create_record(
    vector: List[float],
    metadata: Optional[Dict] = None,
    **kwargs
) -> str
```

##### create_text_record
Creates a new record from text with automatic vectorization.

```python
async def create_text_record(
    text: str,
    metadata: Optional[Dict] = None,
    model: Optional[str] = None,
    **kwargs
) -> str
```

##### search_by_vector
Search for records by vector similarity.

```python
async def search_by_vector(
    vector: List[float],
    limit: int = 5,
    include_vectors: bool = False,
    include_metadata: bool = True
) -> List[SearchResult]
```

##### search_by_text
Search for records by text similarity.

```python
async def search_by_text(
    text: str,
    limit: int = 5,
    model: Optional[str] = None,
    include_vectors: bool = False,
    include_metadata: bool = True
) -> List[SearchResult]
```

##### filter_records
Filter records by metadata criteria.

```python
async def filter_records(
    criteria: Dict,
    limit: int = 100,
    include_vectors: bool = False,
    include_metadata: bool = True
) -> List[SearchResult]
```

## Models

### SearchResult
Represents a search result with score and metadata.

### VectorRecord
Represents a stored vector record.

### JsonRpcRequest
Base model for JSON-RPC requests.

### JsonRpcResponse
Base model for JSON-RPC responses.

## Exceptions

### VectorStoreError
Base exception class.

### ConnectionError
Raised when API is unreachable.

### ValidationError
Raised when input validation fails.

### TimeoutError
Raised when request times out.

### JsonRpcError
Raised when API returns an error response. 