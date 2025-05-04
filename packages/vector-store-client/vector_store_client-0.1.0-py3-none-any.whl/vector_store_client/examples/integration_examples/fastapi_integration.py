"""
FastAPI Integration Example

This example demonstrates how to integrate VectorStoreClient with FastAPI to create
a semantic search API service.

Requirements:
    - fastapi
    - uvicorn
    - pydantic

To run:
    uvicorn examples.integration_examples.fastapi_integration:app --reload
"""

from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from vector_store_client import VectorStoreClient, VectorStoreError

# Initialize FastAPI app
app = FastAPI(
    title="Semantic Search API",
    description="REST API for vector-based semantic search using VectorStoreClient",
    version="1.0.0"
)

# Initialize VectorStoreClient
# In production, you would want to get these from environment variables
VECTOR_STORE_URL = "http://localhost:8080"
vector_store = VectorStoreClient(base_url=VECTOR_STORE_URL)

# Pydantic models for request/response validation
class TextSearchRequest(BaseModel):
    text: str = Field(..., description="Text to search for")
    limit: int = Field(default=5, ge=1, le=100, description="Maximum number of results to return")
    include_vectors: bool = Field(default=False, description="Whether to include vectors in response")
    model: Optional[str] = Field(default=None, description="Model to use for text vectorization")

class VectorSearchRequest(BaseModel):
    vector: List[float] = Field(..., description="Vector to search for")
    limit: int = Field(default=5, ge=1, le=100, description="Maximum number of results to return")
    include_vectors: bool = Field(default=False, description="Whether to include vectors in response")

class CreateRecordRequest(BaseModel):
    text: str = Field(..., description="Text to vectorize and store")
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata")
    model: Optional[str] = Field(default=None, description="Model to use for text vectorization")

class ErrorResponse(BaseModel):
    detail: str

# API endpoints
@app.post("/search/text", response_model=List[Dict], responses={400: {"model": ErrorResponse}})
async def search_by_text(request: TextSearchRequest):
    """
    Search for similar records using text input.
    The text will be automatically converted to a vector using the specified model.
    """
    try:
        results = await vector_store.search_by_text(
            text=request.text,
            limit=request.limit,
            model=request.model,
            include_vectors=request.include_vectors
        )
        return [result.dict() for result in results]
    except VectorStoreError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/search/vector", response_model=List[Dict], responses={400: {"model": ErrorResponse}})
async def search_by_vector(request: VectorSearchRequest):
    """
    Search for similar records using a vector input.
    Expects a vector of the correct dimensionality (384).
    """
    try:
        results = await vector_store.search_by_vector(
            vector=request.vector,
            limit=request.limit,
            include_vectors=request.include_vectors
        )
        return [result.dict() for result in results]
    except VectorStoreError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/records", response_model=str, responses={400: {"model": ErrorResponse}})
async def create_record(request: CreateRecordRequest):
    """
    Create a new record from text input.
    The text will be automatically converted to a vector using the specified model.
    """
    try:
        record_id = await vector_store.create_text_record(
            text=request.text,
            metadata=request.metadata,
            model=request.model
        )
        return record_id
    except VectorStoreError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    Also verifies connection to the vector store.
    """
    try:
        # Perform a simple search to verify vector store connection
        await vector_store.search_by_text("test", limit=1)
        return {"status": "healthy"}
    except VectorStoreError:
        raise HTTPException(status_code=503, detail="Vector store connection failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 