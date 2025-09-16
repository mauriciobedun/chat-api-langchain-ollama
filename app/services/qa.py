import os
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QAService:
    """Serviço de QA usando LangChain com Ollama"""
    
    def __init__(self, model_name: str = None, base_url: str = None):
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "llama3")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self.sessions: Dict[str, ConversationBufferMemory] = {}
        self.documents: List[Document] = []
        
        # Templates de prompt
        self.chat_template = """Você é um assistente inteligente e prestativo. Responda de forma clara, precisa e educada.

Histórico da conversa:
{history}

Pergunta: {question}

Resposta:"""

        self.rag_template = """Baseado nos documentos fornecidos, responda a pergunta de forma precisa e detalhada. 
Se a informação não estiver nos documentos, diga que não encontrou a informação.

Contexto dos documentos:
{context}

Pergunta: {question}

Resposta baseada nos documentos:"""
        
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Inicializa o modelo Ollama"""
        try:
            self.llm = OllamaLLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.1,      # Menos criativo = mais rápido
                num_predict=256,      # Limitar tokens de resposta
                num_ctx=2048,         # Contexto menor
                repeat_penalty=1.1,   # Evitar repetições
                top_k=20,            # Limitar vocabulário
                top_p=0.9            # Nucleus sampling
            )
            
            self.embeddings = OllamaEmbeddings(
                model=self.model_name,
                base_url=self.base_url
            )
            
            logger.info(f"LLM inicializado com sucesso: {self.model_name}")
        except Exception as e:
            logger.error(f"Erro ao inicializar LLM: {e}")
            raise
    
    def check_ollama_connection(self) -> bool:
        """Verifica se o Ollama está conectado"""
        try:
            # Teste simples para verificar conexão
            response = self.llm.invoke("Hello")
            return True
        except Exception as e:
            logger.error(f"Erro na conexão com Ollama: {e}")
            return False
    
    async def get_chat_response(self, message: str, session_id: Optional[str] = None) -> Tuple[str, int]:
        """
        Obtém resposta do chat com medição de latência
        
        Args:
            message: Mensagem do usuário
            session_id: ID da sessão para manter histórico
            
        Returns:
            Tuple com (resposta, latência_ms)
        """
        start_time = time.time()
        
        try:
            # Configurar memória da sessão
            memory = self._get_or_create_session_memory(session_id)
            
            # Criar prompt template
            prompt = PromptTemplate(
                input_variables=["history", "question"],
                template=self.chat_template
            )
            
            # Criar chain
            chain = LLMChain(
                llm=self.llm,
                prompt=prompt,
                memory=memory,
                verbose=False
            )
            
            # Executar chain
            response = await asyncio.get_event_loop().run_in_executor(
                None, chain.run, {"question": message}
            )
            
            # Calcular latência
            latency_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Resposta gerada em {latency_ms}ms para sessão {session_id}")
            
            return response.strip(), latency_ms
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            latency_ms = int((time.time() - start_time) * 1000)
            return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}", latency_ms
    
    def _get_or_create_session_memory(self, session_id: Optional[str]) -> ConversationBufferMemory:
        """Obtém ou cria memória para uma sessão"""
        if not session_id:
            return ConversationBufferMemory()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationBufferMemory()
        
        return self.sessions[session_id]
    
    def clear_session_memory(self, session_id: str):
        """Limpa a memória de uma sessão específica"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Memória da sessão {session_id} limpa")
    
    def add_document(self, content: str, filename: str, document_type: str = "text"):
        """
        Adiciona um documento ao vector store para RAG
        
        Args:
            content: Conteúdo do documento
            filename: Nome do arquivo
            document_type: Tipo do documento
        """
        try:
            # Criar documento
            doc = Document(
                page_content=content,
                metadata={
                    "filename": filename,
                    "type": document_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            self.documents.append(doc)
            
            # Dividir texto em chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.split_documents(self.documents)
            
            # Criar ou atualizar vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            else:
                # Adicionar novos documentos ao vector store existente
                new_vector_store = FAISS.from_documents([doc], self.embeddings)
                self.vector_store.merge_from(new_vector_store)
            
            logger.info(f"Documento {filename} adicionado ao vector store")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documento: {e}")
            raise
    
    async def get_rag_response(self, question: str, session_id: Optional[str] = None) -> Tuple[str, List[str], int]:
        """
        Obtém resposta usando RAG (Retrieval Augmented Generation)
        
        Args:
            question: Pergunta do usuário
            session_id: ID da sessão
            
        Returns:
            Tuple com (resposta, fontes, latência_ms)
        """
        start_time = time.time()
        
        try:
            if self.vector_store is None:
                latency_ms = int((time.time() - start_time) * 1000)
                return "Nenhum documento foi carregado ainda. Por favor, faça upload de documentos primeiro.", [], latency_ms
            
            # Criar chain de retrieval
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            # Executar query
            result = await asyncio.get_event_loop().run_in_executor(
                None, qa_chain, {"query": question}
            )
            
            # Extrair resposta e fontes
            answer = result["result"].strip()
            source_docs = result["source_documents"]
            
            # Formatar fontes
            sources = []
            for doc in source_docs:
                source_text = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                filename = doc.metadata.get("filename", "documento")
                sources.append(f"[{filename}] {source_text}")
            
            # Calcular latência
            latency_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Resposta RAG gerada em {latency_ms}ms para sessão {session_id}")
            
            return answer, sources, latency_ms
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta RAG: {e}")
            latency_ms = int((time.time() - start_time) * 1000)
            return f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}", [], latency_ms
    
    def get_document_count(self) -> int:
        """Retorna o número de documentos carregados"""
        return len(self.documents)
    
    def get_session_count(self) -> int:
        """Retorna o número de sessões ativas"""
        return len(self.sessions)
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do serviço"""
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "documents_loaded": self.get_document_count(),
            "active_sessions": self.get_session_count(),
            "ollama_connected": self.check_ollama_connection()
        }


# Instância global do serviço
qa_service = QAService() 