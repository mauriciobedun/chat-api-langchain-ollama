# Desafio Técnico – Dev Python (FastAPI + LangChain)

## 🎯 Objetivo
Criar uma **API de chat de Perguntas & Respostas** usando **FastAPI** e **LangChain**.  

O sistema deve receber uma pergunta do usuário e responder utilizando um **LLM** conectado via LangChain.  

---

## ✅ Requisitos mínimos

1. **Endpoint `/chat`**
   - Método: `POST`
   - Entrada (exemplo):
     ```json
     {"message": "Qual a capital da França?"}
     ```
   - Saída (exemplo):
     ```json
     {
       "answer": "A capital da França é Paris.",
       "latency_ms": 123
     }
     ```

2. **Uso de LangChain**
   - Implementar uma chain simples (`LLMChain`) com um prompt básico.
   - Retornar a resposta do modelo e medir o tempo de execução.

3. **Estrutura do projeto**
   - Código organizado em módulos, exemplo:
     ```
     app/
       ├── main.py
       ├── api/
       │    └── chat.py
       ├── services/
       │    └── qa.py
       └── schemas/
            └── chat.py
     ```
   - **Pydantic** para schemas de request/response.
   - **.env** para variáveis de configuração.

4. **Configuração**
   - A API deve rodar **mesmo sem chave paga de LLM**.
   - Deve estar documentado no README como executar (`uvicorn app.main:app --reload`).

---

## 🔄 Alternativas para não depender de LLM paga

Você pode escolher uma das opções abaixo:

- **Mock LLM (mais simples)**
  - Usar `FakeListLLM` do LangChain para responder com textos pré-definidos.
  ```python
  from langchain.llms import FakeListLLM
  llm = FakeListLLM(responses=["Paris é a capital da França."])
  ```

- **Modelos open-source gratuitos**
  - **Hugging Face Inference API** (gratuita, precisa só de token do Hugging Face).
    ```bash
    curl https://api-inference.huggingface.co/models/distilbert-base-uncased \
         -H "Authorization: Bearer hf_xxx" \
         -d '{"inputs": "Hello world"}'
    ```
  - **Ollama** (executa modelos localmente, ex.: `llama3`, `mistral`).
    - Instale [Ollama](https://ollama.ai/) e rode:
      ```bash
      ollama run llama3
      ```

---

## 🚀 Desafios adicionais (opcionais)

1. **Integração com RAG (Retrieval Augmented Generation)**
   - Criar um endpoint `/ask` que permita o upload de documentos `.txt` ou `.md`.
   - Indexar o conteúdo em FAISS ou Chroma.
   - Fazer perguntas sobre esses documentos e retornar trechos citados como fontes.

2. **Memória de conversa**
   - Permitir que um `session_id` mantenha o histórico do chat.

3. **Observabilidade**
   - Adicionar `/health` para mostrar status da API.
   - Log estruturado com tempo de execução por requisição.

---

## 📦 Entrega

- Repositório GitHub (ou ZIP) com:
  - Código fonte.
  - `requirements.txt`.
  - README com instruções de instalação, execução e exemplos de requisições.

---

## 📝 Critérios de avaliação

- Funcionalidade básica do chat atendida.
- Código limpo e organizado.
- Uso correto do FastAPI e LangChain.
- README claro e objetivo.
- (Bônus) Desafios adicionais implementados.