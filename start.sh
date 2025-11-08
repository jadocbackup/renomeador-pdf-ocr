#!/bin/bash

# Script para verificar e iniciar o Streamlit manualmente
# Uso: bash start.sh

echo "🔍 Verificando se o Streamlit está rodando..."

# Verificar se o processo está ativo
if pgrep -f "streamlit run app.py" > /dev/null; then
    echo "✅ Streamlit já está rodando!"
    
    # Verificar health check
    if curl -s http://localhost:5000/_stcore/health > /dev/null; then
        echo "✅ Health check OK - Aplicação disponível em http://localhost:5000"
        exit 0
    else
        echo "⚠️  Processo existe mas health check falhou. Reiniciando..."
        pkill -9 -f "streamlit run app.py"
        sleep 2
    fi
fi

echo "🚀 Iniciando Streamlit em segundo plano..."

# Iniciar Streamlit em background
nohup streamlit run app.py --server.port 5000 --server.headless true > /tmp/streamlit.log 2>&1 &

# Aguardar inicialização
echo "⏳ Aguardando inicialização (15 segundos)..."
sleep 15

# Verificar se iniciou corretamente
if curl -s http://localhost:5000/_stcore/health > /dev/null; then
    echo ""
    echo "✅ Streamlit iniciado com sucesso!"
    echo "📱 Acesse: http://localhost:5000"
    echo "📋 Logs: tail -f /tmp/streamlit.log"
    echo ""
else
    echo ""
    echo "❌ Falha ao iniciar Streamlit"
    echo "📋 Verifique os logs: cat /tmp/streamlit.log"
    echo ""
    exit 1
fi
