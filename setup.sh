#!/bin/bash

# ===============================================
#  🚀 BOOTSTRAP DAORA KIDS LIVE 24H (v2.5 FINAL)
# ===============================================

# 1. Garantir que o usuário atual seja o 'stream' ou tenha permissão sudo
if [ "$(id -u)" -ne 0 ]; then
    echo "🚨 Por favor, rode com sudo: sudo bash setup.sh"
    exit 1
fi

echo "🔄 Limpando instalações anteriores e atualizando dependências..."
BASE_DIR="/home/stream"
TEMP_DIR="/tmp/daorakids_setup"

# Limpa a "matrioska" e versões antigas
sudo rm -rf $BASE_DIR/*

# 2. Download limpo
echo "📦 Baixando versão v2.5 do repositório..."
sudo rm -rf $TEMP_DIR
git clone https://github.com/daorakids/streamer.git $TEMP_DIR

# 3. Distribuição de arquivos
echo "🚚 Organizando diretórios..."
sudo mkdir -p $BASE_DIR
sudo cp -r $TEMP_DIR/home/stream/* $BASE_DIR/
if [ -d "$TEMP_DIR/etc" ]; then
    sudo cp -r $TEMP_DIR/etc/* /etc/
fi

# 4. Ajuste de permissões
sudo chown -R stream:stream $BASE_DIR
sudo chmod +x $BASE_DIR/*.sh
sudo chmod +x $BASE_DIR/*.py

# 5. Execução INTERATIVA
echo "🐍 Iniciando Wizard de Configuração..."
echo "⚠️  Se solicitado, digite as informações com atenção."
cd $BASE_DIR

# O segredo para o EOFError: forçamos o Python a ler do terminal real
python3 $BASE_DIR/install.py < /dev/tty

# Limpeza final
sudo rm -rf $TEMP_DIR
echo "✅ Processo concluído!"
