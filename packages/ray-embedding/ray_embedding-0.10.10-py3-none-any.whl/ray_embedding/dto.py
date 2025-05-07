from typing import Union, List, Optional
from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    """Schema of embedding requests (compatible with OpenAI)"""
    model: str  # Model name (for compatibility; only one model is used here)
    input: Union[str, List[str]]  # List of strings to embed
    dimensions: Optional[int] = None


class EmbeddingResponse(BaseModel):
    """Schema of embedding response (compatible with OpenAI)"""
    object: str
    data: List[dict]  # Embedding data including index and vector
    model: str  # Model name used for embedding