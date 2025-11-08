#!/bin/bash

# Script de deployment que usa porta dinâmica do Replit
# A variável $PORT é fornecida automaticamente pelo sistema de deployment

# Usar porta do ambiente ou 5000 como fallback
DEPLOY_PORT=${PORT:-5000}

echo "🚀 Iniciando Streamlit na porta $DEPLOY_PORT"

# Atualizar config.toml com porta dinâmica
cat > .streamlit/config.toml << EOF
[server]
headless = true
address = "0.0.0.0"
port = $DEPLOY_PORT
enableCORS = false
enableXsrfProtection = false

[browser]
serverAddress = "0.0.0.0"
gatherUsageStats = false
EOF

# Iniciar Streamlit
exec streamlit run app.py --server.port=$DEPLOY_PORT --server.address=0.0.0.0 --server.headless=true
