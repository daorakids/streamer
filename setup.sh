#!/bin/bash

# ===============================================
#  🚀 BOOTSTRAP DAORA KIDS LIVE 24H (v2.7)
# ===============================================

# 1. Verificar Privilégios
if [ "$(id -u)" -ne 0 ]; then
    echo "🚨 Por favor, rode com sudo: sudo bash setup.sh"
    exit 1
fi

echo "🔄 Iniciando Setup do Sistema (isso pode demorar alguns minutos)..."

# 2. Instalar Git e dependências essenciais primeiro
apt-get update
apt-get install -y git python3-pip curl python3-dotenv python3-requests ffmpeg

# 3. Criar usuário 'stream' se não existir
if ! id "stream" &>/dev/null; then
    echo "👤 Criando usuário 'stream'..."
    useradd -m -s /bin/bash stream
    echo "stream:stream" | chpasswd # Senha temporária, você mudará no install.py
    usermod -aG sudo,video,audio stream
fi

# 4. Definir Pastas
BASE_DIR="/home/stream"
TEMP_DIR="/tmp/daorakids_setup"

echo "📂 Preparando diretórios..."
rm -rf $TEMP_DIR
mkdir -p $BASE_DIR

# 5. Download do Código
echo "📦 Baixando código do GitHub..."
git clone https://github.com/daorakids/streamer.git $TEMP_DIR

if [ ! -d "$TEMP_DIR/home/stream" ]; then
    echo "🚨 ERRO: Falha ao clonar o repositório. Verifique sua internet."
    exit 1
fi

# 6. Distribuição de arquivos
echo "🚚 Movendo arquivos para os locais de destino..."
cp -r $TEMP_DIR/home/stream/* $BASE_DIR/
if [ -d "$TEMP_DIR/etc" ]; then
    cp -r $TEMP_DIR/etc/* /etc/
fi

# 7. Ajuste de permissões
chown -R stream:stream $BASE_DIR
chmod +x $BASE_DIR/*.sh
chmod +x $BASE_DIR/*.py

# 8. Execução INTERATIVA do Wizard
echo "🐍 Iniciando Wizard de Configuração..."
cd $BASE_DIR
# Usamos o usuário stream para rodar o instalador
sudo -u stream python3 $BASE_DIR/install.py < /dev/tty

# 9. Limpeza final
rm -rf $TEMP_DIR
echo "✅ Setup concluído com sucesso!"
