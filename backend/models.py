from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import json

# --- Database Models ---

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    mime_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    page_count: int
    # Storing normalized content as a JSON string for simplicity in SQLite
    # In Postgres, we would use JSONB
    normalized_content_json: str 

class TaskResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_type: str
    status: str # "pending", "completed", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result_json: Optional[str] = None
    error_message: Optional[str] = None
    
    # Link to documents (Many-to-Many is better, but for MVP we can store doc_ids list in JSON)
    document_ids_json: str 

# --- Pydantic Schemas for API ---

class DocumentResponse(SQLModel):
    id: int
    filename: str
    mime_type: str
    page_count: int
    upload_timestamp: datetime

class TaskRequest(SQLModel):
    task_type: str
    document_ids: List[int]
    jurisdiction: Optional[str] = None
    instructions: Optional[str] = None

class TaskResponse(SQLModel):
    id: int
    task_type: str
    status: str
    created_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
