"""
Contains request models for the Subtxt API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class GenerateConfigRequest(BaseModel):
    url: str = Field(..., examples=["https://docs.stripe.com"])
    include_paths: Optional[List[str]] = Field(None)
    exclude_paths: Optional[List[str]] = Field(None)
    replace_title: Optional[List[str]] = Field(None)
    output_title: Optional[str] = Field(None)
    output_description: Optional[str] = Field(None)
    concurrency: int = Field(10, ge=1, le=50)
    user_agent: Optional[str] = Field(None)


class WatchStartRequest(GenerateConfigRequest):
    interval_seconds: int = Field(3600, ge=60)
    identifier: str = Field(..., examples=["stripe-docs-watch"])

class WatchActionRequest(BaseModel):
    identifier: str = Field(...)    
