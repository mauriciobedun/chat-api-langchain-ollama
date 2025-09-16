#!/bin/sh
set -eu

# 1) Sobe o servidor em background
ollama serve &
PID=$!

# 2) Espera a API responder (usando ollama list em vez de curl)
echo "Aguardando Ollama em http://localhost:11434..."
i=0
until ollama list >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -gt 300 ]; then
    echo "Timeout aguardando o Ollama (10 min)."
    exit 1
  fi
  sleep 2
done
echo "Ollama pronto."

# 3) Se habilitado, baixa o modelo (bloqueia até terminar)
if [ "${OLLAMA_AUTO_PULL:-}" = "1" ]; then
  MODEL="${OLLAMA_MODEL:-llama3}"
  echo "Baixando modelo: $MODEL"
  # o pull pode demorar MUITO na primeira vez
  if ! ollama pull "$MODEL"; then
    echo "Falha no pull de $MODEL"
    exit 1
  fi
  echo "Modelo $MODEL baixado."
fi

# 4) Mantém o processo principal vivo
wait "$PID"
