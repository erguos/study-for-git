from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from .database import Base


class Dataset(Base):
    """Metadata for an uploaded dataset (structured table or document)."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(16), nullable=False)  # 'table' | 'doc'
    description = Column(String(500), default="")
    # For table datasets: actual MySQL table name created for the data.
    table_name = Column(String(128), nullable=True)
    # JSON describing columns: [{"name": "...", "type": "...", "comment": "..."}]
    schema_json = Column(JSON, nullable=True)
    # For doc datasets: total number of chunks stored.
    chunk_count = Column(Integer, default=0)
    status = Column(String(16), default="ready")  # ready | failed
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentChunk(Base):
    """Chunks of uploaded documents, used for TF-IDF based retrieval."""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    source_file = Column(String(255), default="")


class ChatMessage(Base):
    """Chat history between user and agent."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(16), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    extra = Column(JSON, nullable=True)  # structured result / chart config
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Application user with role-based access."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(16), nullable=False, default="client")  # admin | client
    created_at = Column(DateTime, default=datetime.utcnow)
