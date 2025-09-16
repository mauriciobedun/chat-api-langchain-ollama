from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Schema para requisições do chat"""
    message: str = Field(..., min_length=1, max_length=2000, description="Mensagem do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão para manter histórico")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Qual a capital da França?",
                "session_id": "user-123"
            }
        }


class ChatResponse(BaseModel):
    """Schema para respostas do chat"""
    answer: str = Field(..., description="Resposta do modelo de linguagem")
    latency_ms: int = Field(..., description="Tempo de resposta em milissegundos")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da resposta")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "A capital da França é Paris.",
                "latency_ms": 123,
                "session_id": "user-123",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Schema para resposta do health check"""
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp do health check")
    ollama_status: str = Field(..., description="Status do Ollama")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "ollama_status": "connected"
            }
        }


class DocumentUploadRequest(BaseModel):
    """Schema para upload de documentos (RAG)"""
    content: str = Field(..., min_length=1, description="Conteúdo do documento")
    filename: str = Field(..., description="Nome do arquivo")
    document_type: str = Field(default="text", description="Tipo do documento")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Este é o conteúdo do documento...",
                "filename": "documento.txt",
                "document_type": "text"
            }
        }


class RAGQueryRequest(BaseModel):
    """Schema para consultas RAG"""
    question: str = Field(..., min_length=1, max_length=2000, description="Pergunta sobre os documentos")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "O que o documento diz sobre inteligência artificial?",
                "session_id": "user-123"
            }
        }


class RAGQueryResponse(BaseModel):
    """Schema para respostas RAG"""
    answer: str = Field(..., description="Resposta baseada nos documentos")
    sources: list[str] = Field(default=[], description="Trechos dos documentos usados como fonte")
    latency_ms: int = Field(..., description="Tempo de resposta em milissegundos")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da resposta")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Baseado nos documentos, inteligência artificial é...",
                "sources": ["Trecho 1 do documento", "Trecho 2 do documento"],
                "latency_ms": 234,
                "session_id": "user-123",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        } 