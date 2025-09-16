from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from app.schemas.chat import (
    ChatRequest, ChatResponse, HealthResponse,
    DocumentUploadRequest, RAGQueryRequest, RAGQueryResponse
)
from app.services.qa import qa_service

# Configurar logging
logger = logging.getLogger(__name__)

# Criar router
router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Endpoint principal para chat com o LLM
    
    Recebe uma mensagem do usuário e retorna a resposta do modelo com latência medida.
    Suporta manutenção de histórico através de session_id.
    """
    try:
        logger.info(f"Processando mensagem para sessão {request.session_id}: {request.message[:50]}...")
        
        # Obter resposta do serviço QA
        answer, latency_ms = await qa_service.get_chat_response(
            message=request.message,
            session_id=request.session_id
        )
        
        # Criar resposta
        response = ChatResponse(
            answer=answer,
            latency_ms=latency_ms,
            session_id=request.session_id
        )
        
        logger.info(f"Resposta enviada com sucesso em {latency_ms}ms")
        return response
        
    except Exception as e:
        logger.error(f"Erro no endpoint /chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Endpoint de health check
    
    Verifica o status da API e da conexão com o Ollama.
    """
    try:
        # Verificar conexão com Ollama
        ollama_connected = qa_service.check_ollama_connection()
        ollama_status = "connected" if ollama_connected else "disconnected"
        
        # Status geral da API
        api_status = "healthy" if ollama_connected else "degraded"
        
        response = HealthResponse(
            status=api_status,
            ollama_status=ollama_status
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthResponse(
            status="unhealthy",
            ollama_status="error"
        )


@router.post("/upload-document", tags=["RAG"])
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(default="text")
):
    """
    Endpoint para upload de documentos para RAG
    
    Permite upload de arquivos .txt ou .md para indexação no vector store.
    """
    try:
        # Verificar tipo do arquivo
        if not file.filename.endswith(('.txt', '.md')):
            raise HTTPException(
                status_code=400,
                detail="Apenas arquivos .txt e .md são suportados"
            )
        
        # Ler conteúdo do arquivo
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Verificar se o conteúdo não está vazio
        if not content_str.strip():
            raise HTTPException(
                status_code=400,
                detail="O arquivo está vazio"
            )
        
        # Adicionar documento ao serviço
        qa_service.add_document(
            content=content_str,
            filename=file.filename,
            document_type=document_type
        )
        
        logger.info(f"Documento {file.filename} carregado com sucesso")
        
        return {
            "message": f"Documento {file.filename} carregado com sucesso",
            "filename": file.filename,
            "size": len(content_str),
            "type": document_type,
            "total_documents": qa_service.get_document_count()
        }
        
    except Exception as e:
        logger.error(f"Erro no upload do documento: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar documento: {str(e)}"
        )


@router.post("/ask", response_model=RAGQueryResponse, tags=["RAG"])
async def ask_documents(request: RAGQueryRequest):
    """
    Endpoint para fazer perguntas sobre documentos carregados (RAG)
    
    Utiliza Retrieval Augmented Generation para responder perguntas
    baseadas nos documentos previamente carregados.
    """
    try:
        logger.info(f"Processando pergunta RAG para sessão {request.session_id}: {request.question[:50]}...")
        
        # Obter resposta RAG do serviço
        answer, sources, latency_ms = await qa_service.get_rag_response(
            question=request.question,
            session_id=request.session_id
        )
        
        # Criar resposta
        response = RAGQueryResponse(
            answer=answer,
            sources=sources,
            latency_ms=latency_ms,
            session_id=request.session_id
        )
        
        logger.info(f"Resposta RAG enviada com sucesso em {latency_ms}ms")
        return response
        
    except Exception as e:
        logger.error(f"Erro no endpoint /ask: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.delete("/session/{session_id}", tags=["Session"])
async def clear_session(session_id: str):
    """
    Endpoint para limpar histórico de uma sessão específica
    """
    try:
        qa_service.clear_session_memory(session_id)
        
        return {
            "message": f"Histórico da sessão {session_id} limpo com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar sessão {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar sessão: {str(e)}"
        )


@router.get("/stats", tags=["Admin"])
async def get_stats():
    """
    Endpoint para obter estatísticas do serviço
    """
    try:
        stats = qa_service.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        ) 