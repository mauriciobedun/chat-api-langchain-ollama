#!/usr/bin/env python3
"""
Script de teste para a API de Chat com FastAPI + LangChain + Ollama
"""

import requests
import json
import time
from pathlib import Path

# Configurações
BASE_URL = "http://localhost:8000/api/v1"
TEST_DOCUMENT = "example_document.txt"

def test_health():
    """Testa o endpoint de health check"""
    print("🏥 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_chat():
    """Testa o endpoint de chat básico"""
    print("\n💬 Testando chat básico...")
    try:
        data = {
            "message": "Olá! Como você está?",
            "session_id": "test-session-1"
        }
        response = requests.post(f"{BASE_URL}/chat", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Resposta: {result['answer']}")
        print(f"Latência: {result['latency_ms']}ms")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_upload_document():
    """Testa o upload de documento"""
    print("\n📄 Testando upload de documento...")
    try:
        if not Path(TEST_DOCUMENT).exists():
            print(f"❌ Arquivo {TEST_DOCUMENT} não encontrado")
            return False
        
        with open(TEST_DOCUMENT, "rb") as f:
            files = {"file": f}
            data = {"document_type": "text"}
            response = requests.post(f"{BASE_URL}/upload-document", files=files, data=data)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Documento carregado: {result.get('filename')}")
        print(f"Tamanho: {result.get('size')} caracteres")
        print(f"Total de documentos: {result.get('total_documents')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_rag_query():
    """Testa consulta RAG"""
    print("\n🔍 Testando consulta RAG...")
    try:
        data = {
            "question": "O que é machine learning e quais são seus tipos principais?",
            "session_id": "test-session-rag"
        }
        response = requests.post(f"{BASE_URL}/ask", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Resposta: {result['answer'][:200]}...")
        print(f"Fontes encontradas: {len(result.get('sources', []))}")
        print(f"Latência: {result['latency_ms']}ms")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_stats():
    """Testa endpoint de estatísticas"""
    print("\n📊 Testando estatísticas...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"Status: {response.status_code}")
        print(f"Stats: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API de Chat")
    print("=" * 50)
    
    # Aguardar um pouco para garantir que a API está rodando
    print("⏳ Aguardando API inicializar...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Chat Básico", test_chat),
        ("Upload de Documento", test_upload_document),
        ("Consulta RAG", test_rag_query),
        ("Estatísticas", test_stats)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        success = test_func()
        results.append((test_name, success))
    
    # Resumo dos resultados
    print(f"\n{'=' * 50}")
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A API está funcionando corretamente.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main() 