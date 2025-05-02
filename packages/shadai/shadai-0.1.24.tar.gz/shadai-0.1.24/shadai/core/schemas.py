from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    config_name: str
    alias: Optional[str] = None
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = None
    llm_max_tokens: Optional[int] = None
    query_mode: Optional[str] = None
    language: Optional[str] = None


class SessionResponse(SessionCreate):
    session_id: str
    cost: float = 0


class JobStatus(str, Enum):
    """Job status enumeration."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, Enum):
    INGESTION = "ingestion"
    DELETE = "delete"
    QUERY = "query"
    DELETE_SESSION = "delete_session"
    SUMMARY = "summary"
    ARTICLE = "article"
    COMPLETION = "completion"
    CHAT = "chat"
    CLEANUP_CHAT = "cleanup_chat"
    CLEANUP_NAMESPACE = "cleanup_namespace"


class JobResponse(BaseModel):
    """Typed job response container."""

    job_id: str
    user_id: str
    session_id: str
    job_type: JobType
    status: JobStatus
    progress: Optional[float] = None
    result: Optional[str] = "in progress"


class Query(BaseModel):
    query: str
    role: Optional[str] = None
    display_in_console: bool = False


class QueryResponse(BaseModel):
    query: Query
    response: str
    display_in_console: bool = False
