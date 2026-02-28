#!/bin/bash

# ===============================================
#  🚀 BOOTSTRAP DAORA KIDS LIVE 24H (v2.3 - Corrigido)
# ===============================================

echo "🔄 Atualizando sistema e instalando dependências base..."
sudo apt-get update && sudo apt-get install -y git python3-pip curl

# 1. Definir Pasta Temporária para o Clone
TEMP_DIR="/tmp/daorakids_setup"
BASE_DIR="/home/stream"

echo "📂 Preparando instalação..."
sudo mkdir -p $BASE_DIR
rm -rf $TEMP_DIR
git clone https://github.com/daorakids/streamer.git $TEMP_DIR

# 2. Distribuir Arquivos Corretamente
echo "🚚 Movendo arquivos para os locais de destino..."

# Move o conteúdo de home/stream/ do Git para /home/stream/ do sistema
sudo cp -r $TEMP_DIR/home/stream/* $BASE_DIR/

# Move as configurações de sistema para /etc/
if [ -d "$TEMP_DIR/etc" ]; then
    sudo cp -r $TEMP_DIR/etc/* /etc/
fi

# 3. Limpeza e Permissões
sudo chown -R stream:stream $BASE_DIR
chmod +x $BASE_DIR/*.sh
chmod +x $BASE_DIR/*.py

# 4. Disparar o Wizard de Instalação (Python)
echo "🐍 Iniciando o Wizard de Configuração (Python)..."
cd $BASE_DIR
sudo python3 $BASE_DIR/install.py

# Limpar rastro temporário
rm -rf $TEMP_DIR
