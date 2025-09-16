# 🤖 API de Chat com FastAPI + LangChain + Ollama (Docker)

🎯 **Objetivo**: API de chat de Perguntas & Respostas usando FastAPI, LangChain e Ollama, totalmente containerizada com Docker.

## 📋 Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **4GB+ de RAM livre** (para modelos LLM)
- **Conexão com internet** (para baixar modelo na primeira execução)

## 🚀 Quick Start (2 comandos)

```bash
# 1. Clone o repositório
git clone <repo-url>
cd DESAFIO-DGTALLAB

# 2. Iniciar tudo com Docker
docker-compose up -d
```

**🎉 Pronto!** 
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 📚 Comandos Úteis
```bash
# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Reconstruir imagens
docker-compose build --no-cache

# Ver status
docker-compose ps
```

## 🏗️ Arquitetura

```
┌─────────────────┐    HTTP     ┌─────────────────┐
│   FastAPI API   │◄──────────► │   Ollama LLM    │
│   (Port 8000)   │   Requests  │   (Port 11434)  │
└─────────────────┘             └─────────────────┘
        │                               │
        ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│  LangChain +    │             │  llama3 Model   │
│  Vector Store   │             │   (Auto-pull)   │
└─────────────────┘             └─────────────────┘
```

## 📚 Documentação da API

### Endpoints Principais

#### 🗨️ POST `/api/v1/chat`
Chat básico com o LLM.

**Request:**
```json
{
  "message": "Qual a capital da França?",
  "session_id": "user-123"
}
```

**Response:**
```json
{
  "answer": "A capital da França é Paris.",
  "latency_ms": 1250,
  "session_id": "user-123",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 📄 POST `/api/v1/upload-document`
Upload de documentos para RAG.

**Request:** (form-data)
- `file`: Arquivo .txt ou .md

**Response:**
```json
{
  "message": "Documento exemplo.txt carregado com sucesso",
  "filename": "exemplo.txt",
  "size": 1234,
  "total_documents": 1
}
```

#### ❓ POST `/api/v1/ask`
Perguntas sobre documentos carregados (RAG).

**Request:**
```json
{
  "question": "O que é machine learning?",
  "session_id": "user-123"
}
```

**Response:**
```json
{
  "answer": "Machine Learning é uma subárea da IA...",
  "sources": ["[exemplo.txt] Machine Learning é uma subárea..."],
  "latency_ms": 2340,
  "session_id": "user-123",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 🏥 GET `/api/v1/health`
Health check dos serviços.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "ollama_status": "connected",
  "model": "llama3",
  "documents_loaded": 1,
  "active_sessions": 2
}
```

## 🧪 Testando a API

### Teste Automatizado
```bash
# Executar todos os testes
docker-compose exec api python test_api.py
```

### Testes Manuais com curl
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Chat básico
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Olá! Como você está?"}'

# Upload documento
curl -X POST "http://localhost:8000/api/v1/upload-document" \
     -F "file=@example_document.txt"

# Pergunta sobre documento
curl -X POST "http://localhost:8000/api/v1/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "O que é inteligência artificial?"}'
```

### Teste com Python
```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/health")
print(f"Status: {response.json()}")

# Chat
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"message": "Explique machine learning"}
)
print(f"Resposta: {response.json()}")
```

## 🔧 Desenvolvimento

### Modo Desenvolvimento (Hot Reload)
```bash
# Iniciar com hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Acessar Containers
```bash
# Shell da API
docker-compose exec api bash

# Shell do Ollama  
docker-compose exec ollama bash

# Ver logs específicos
docker-compose logs -f api
docker-compose logs -f ollama
```

### Estrutura do Projeto
```
├── app/                    # Código da aplicação
│   ├── main.py            # FastAPI app
│   ├── api/               # Endpoints
│   ├── services/          # Lógica de negócio
│   └── schemas/           # Modelos Pydantic
├── docker-compose.yml     # Configuração principal
├── docker-compose.dev.yml # Configuração desenvolvimento
├── Dockerfile             # Imagem da API
├── requirements.txt      # Dependências Python
└── test_api.py           # Testes automatizados
```

## 🚀 Recursos Implementados

### ✅ Funcionalidades Básicas
- **Chat com LLM**: Conversas usando llama3 via Ollama
- **Medição de latência**: Tempo de resposta em milissegundos  
- **Validação de dados**: Schemas Pydantic robustos
- **Health checks**: Monitoramento de saúde dos serviços
- **Documentação automática**: Swagger UI integrado

### ✅ Funcionalidades Avançadas
- **RAG (Retrieval Augmented Generation)**:
  - Upload de documentos (.txt, .md)
  - Busca semântica com FAISS
  - Respostas baseadas em documentos
- **Memória de conversação**:
  - Sessões por usuário
  - Histórico mantido por sessão
- **Observabilidade**:
  - Logs estruturados
  - Métricas de performance
  - Headers de tempo de processamento

### ✅ DevOps e Produção
- **Containerização completa**: Docker + Docker Compose
- **Orquestração de serviços**: API + Ollama + Inicialização automática
- **Health checks**: Verificação automática de saúde
- **Volumes persistentes**: Dados do Ollama mantidos
- **Rede isolada**: Comunicação segura entre containers

## 📊 Monitoramento

### Verificar Status
```bash
# Status geral
docker-compose ps

# Health check
curl http://localhost:8000/api/v1/health
curl http://localhost:11434/api/tags

# Logs em tempo real
docker-compose logs -f
```

### Métricas Disponíveis
- Latência de respostas (ms)
- Número de sessões ativas
- Documentos carregados
- Status de conexão Ollama

## 🐛 Troubleshooting

### Serviços não iniciam
```bash
# Verificar logs
docker-compose logs -f

# Reconstruir imagens
docker-compose build --no-cache
docker-compose up -d
```

### Ollama não baixa modelo
```bash
# Verificar logs do Ollama
docker-compose logs -f ollama

# Reiniciar serviço
docker-compose restart ollama ollama-init
```

### API não responde
```bash
# Verificar saúde
curl http://localhost:8000/api/v1/health

# Reiniciar API
docker-compose restart api
```

### Limpar tudo e recomeçar
```bash
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

### Problemas de memória
- **Requisito**: Mínimo 4GB RAM livre
- **Solução**: Fechar outras aplicações pesadas
- **Alternativa**: Usar modelo menor (ajustar em docker-compose.yml)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adicionar nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

🎉 **Projeto pronto para avaliação!** 
Basta executar `docker-compose up -d` e testar em http://localhost:8000/docs