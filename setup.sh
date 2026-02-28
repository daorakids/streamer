#!/bin/bash

# ===============================================
#  🚀 BOOTSTRAP DAORA KIDS LIVE 24H (v2.2)
# ===============================================

echo "🔄 Atualizando sistema e instalando dependências base..."
sudo apt-get update && sudo apt-get install -y git python3-pip curl

# 1. Definir Pasta de Trabalho
BASE_DIR="/home/stream"
echo "📂 Preparando diretório $BASE_DIR..."
sudo mkdir -p $BASE_DIR
sudo chown $(whoami):$(whoami) $BASE_DIR

# 2. Download do Projeto Completo
# Se você tornar o repo público, esse comando não pedirá senha.
echo "📦 Baixando o código do Daora Kids v2.0 do GitHub..."
if [ -d "$BASE_DIR/.git" ]; then
    cd $BASE_DIR && git pull
else
    git clone https://github.com/daorakids/streamer.git $BASE_DIR
fi

# 3. Dar permissão aos scripts
chmod +x $BASE_DIR/setup.sh
chmod +x $BASE_DIR/iniciar_live.sh
chmod +x $BASE_DIR/manutencao_diaria.sh

# 4. Disparar o Wizard de Instalação (Python)
echo "🐍 Iniciando o Wizard de Configuração (Python)..."
sudo python3 $BASE_DIR/install.py
