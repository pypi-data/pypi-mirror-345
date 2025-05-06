"""
Contains response models for the Subtxt API.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal

class StructuredDataResponse(BaseModel):
     source_url: str
     main_title: str
     main_description: str
     generation_timestamp: str
     sections: Dict[str, List[Dict[str, Any]]]
     pages: List[Dict[str, Any]]
     error: Optional[str] = None

class WatchStartResponse(BaseModel):
    message: str
    identifier: str
    pid: Optional[int] = None

class WatchStatusResponse(BaseModel):
    identifier: str
    status: str
    pid: Optional[int] = None

class ListWatchersResponse(BaseModel):
    watchers: List[Dict[str, Any]]

class WatchUpdateEvent(BaseModel):
    event: Literal["update", "error"] = "update"
    identifier: str
    timestamp: str
    error: Optional[str] = None