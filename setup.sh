#!/bin/bash

# ===============================================
#  🚀 BOOTSTRAP DAORA KIDS LIVE 24H (v2.4)
# ===============================================

echo "🔄 Atualizando sistema e instalando dependências base..."
sudo apt-get update && sudo apt-get install -y git python3-pip curl python3-dotenv python3-requests

# 1. Definir Pastas
TEMP_DIR="/tmp/daorakids_setup"
BASE_DIR="/home/stream"

echo "📂 Preparando instalação em $BASE_DIR..."
sudo mkdir -p $BASE_DIR
sudo rm -rf $TEMP_DIR
git clone https://github.com/daorakids/streamer.git $TEMP_DIR

# 2. Distribuir Arquivos
echo "🚚 Movendo arquivos..."
sudo cp -r $TEMP_DIR/home/stream/* $BASE_DIR/
if [ -d "$TEMP_DIR/etc" ]; then
    sudo cp -r $TEMP_DIR/etc/* /etc/
fi

# 3. Permissões Robustas
sudo chown -R $(whoami):$(whoami) $BASE_DIR
sudo chmod +x $BASE_DIR/*.sh
sudo chmod +x $BASE_DIR/*.py

# 4. Iniciar Wizard
echo "🐍 Iniciando o Wizard de Configuração (Python)..."
cd $BASE_DIR
# Rodamos o install.py diretamente para garantir interatividade total
python3 install.py

# Limpeza
rm -rf $TEMP_DIR
