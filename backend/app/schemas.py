from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class DatasetOut(BaseModel):
    id: int
    name: str
    type: str
    description: str
    table_name: Optional[str] = None
    schema_json: Optional[Any] = None
    chunk_count: int = 0
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DatasetListResponse(BaseModel):
    datasets: List[DatasetOut]
    total: int


class UploadResponse(BaseModel):
    dataset_id: int
    name: str
    type: str
    rows: Optional[int] = None
    columns: Optional[List[dict]] = None
    chunks: Optional[int] = None
    message: str = ""


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    extra: Optional[Any] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=64)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    token: str
    username: str
    role: str
