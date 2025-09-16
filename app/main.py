from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.api.chat import router as chat_router
from app.services.qa import qa_service

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando API de Chat com FastAPI + LangChain + Ollama")
    
    # Verificar conexão com Ollama
    try:
        if qa_service.check_ollama_connection():
            logger.info("✅ Conexão com Ollama estabelecida")
        else:
            logger.warning("⚠️  Ollama não está conectado - algumas funcionalidades podem não funcionar")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com Ollama: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando API de Chat")


# Criar aplicação FastAPI
app = FastAPI(
    title="API de Chat com LangChain e Ollama",
    description="""
    🤖 **API de Chat Inteligente**
    
    Esta API fornece funcionalidades de chat usando LangChain e Ollama, incluindo:
    
    - **Chat básico**: Conversas com modelo de linguagem
    - **Memória de sessão**: Manutenção de histórico por sessão
    - **RAG (Retrieval Augmented Generation)**: Perguntas sobre documentos
    - **Upload de documentos**: Suporte para .txt e .md
    - **Observabilidade**: Health checks e métricas
    
    ## 🚀 Como usar
    
    1. **Chat básico**: Use o endpoint `/chat` para conversas simples
    2. **Upload de documentos**: Use `/upload-document` para carregar arquivos
    3. **Perguntas sobre documentos**: Use `/ask` para RAG
    4. **Health check**: Use `/health` para verificar status
    
    ## 📊 Monitoramento
    
    - `/health`: Status da API e Ollama
    - `/stats`: Estatísticas detalhadas do serviço
    """,
    version="1.0.0",
    contact={
        "name": "Desenvolvedor",
        "email": "dev@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para log estruturado de requisições"""
    start_time = time.time()
    
    # Log da requisição
    logger.info(
        f"📥 {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    # Processar requisição
    response = await call_next(request)
    
    # Calcular tempo de processamento
    process_time = time.time() - start_time
    process_time_ms = int(process_time * 1000)
    
    # Log da resposta
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time_ms}ms"
    )
    
    # Adicionar header com tempo de processamento
    response.headers["X-Process-Time"] = str(process_time_ms)
    
    return response


# Incluir routers
app.include_router(chat_router, prefix="/api/v1")


# Endpoint raiz
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "🤖 API de Chat com FastAPI + LangChain + Ollama",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "chat": "/api/v1/chat",
            "upload": "/api/v1/upload-document", 
            "ask": "/api/v1/ask",
            "health": "/api/v1/health",
            "stats": "/api/v1/stats"
        }
    }


# Handler global de exceções
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"❌ Erro não tratado em {request.url.path}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "message": "Ocorreu um erro inesperado. Tente novamente mais tarde.",
            "path": str(request.url.path)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🔧 Iniciando servidor de desenvolvimento")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 