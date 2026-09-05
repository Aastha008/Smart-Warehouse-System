"""Pydantic schemas for AI assistant."""
from pydantic import BaseModel
from typing import Optional, Any


class AssistantQuery(BaseModel):
    """Query to the AI assistant."""
    query: str
    context: dict = {}


class AssistantResponse(BaseModel):
    """Response from the AI assistant."""
    response: str
    sources: list = []
    data_used: dict = {}
    confidence: Optional[str] = "high"
