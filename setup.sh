#!/bin/bash

# ===============================================
#  🚀 BOOTSTRAP DAORA KIDS LIVE 24H (v2.8.9)
# ===============================================

# 1. Verificar Privilégios e Estado do Disco
if [ "$(id -u)" -ne 0 ]; then
    echo "🚨 Por favor, rode com sudo: sudo bash setup.sh"
    exit 1
fi

echo "🛡️ Verificando integridade do disco e preparando montagem..."
mount -o remount,rw / 2>/dev/null
mkdir -p /mnt/videos
chmod 777 /mnt/videos
if [ ! -d "/mnt/videos" ]; then
    echo "🚨 ERRO FATAL: Nao foi possivel criar /mnt/videos. O disco pode estar em modo Read-Only ou corrompido."
    exit 1
fi
echo "   ✅ Pasta /mnt/videos pronta."

echo "🔄 Iniciando Setup do Sistema..."

# 2. Instalar dependências essenciais apenas se necessário
echo "📦 Verificando dependências (git, ffmpeg, python3)..."
if ! command -v git &>/dev/null || ! command -v ffmpeg &>/dev/null; then
    echo "   ▶ Instalando pacotes faltantes (isso pode demorar um pouco)..."
    apt-get update -qq
    apt-get install -y -qq git python3-pip curl python3-dotenv python3-requests ffmpeg
else
    echo "   ✅ Dependências básicas já instaladas."
fi

# 3. Criar usuário 'stream' se não existir
if ! id "stream" &>/dev/null; then
    echo "👤 Criando usuário 'stream'..."
    useradd -m -s /bin/bash stream
    echo "stream:stream" | chpasswd
    usermod -aG sudo,video,audio stream
    # Permitir sudo sem senha para o stream facilitar a instalação
    echo "stream ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/stream
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
cp -a $TEMP_DIR/home/stream/. $BASE_DIR/

# Instalação de serviços systemd (Removendo o perigoso cp -r /etc)
echo "⚙️ Instalando serviços do sistema..."
cp $BASE_DIR/*.service /etc/systemd/system/
cp $BASE_DIR/*.timer /etc/systemd/system/
systemctl daemon-reload

# 7. Ajuste de permissões
chown -R stream:stream $BASE_DIR
chmod +x $BASE_DIR/*.sh
chmod +x $BASE_DIR/*.py

# 8. Wizard de Configuração em BASH (Pensando fora da caixa - Máxima estabilidade)
echo -e "\n\033[1;32m🎨 CONFIGURAÇÃO DAORA KIDS v2.8.9\033[0m"

ENV_FILE="$BASE_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo -n "⚠️  Instalação detectada! Deseja [U] Atualizar Scripts ou [R] Reinstalar tudo? (U/R): "
    read choice < /dev/tty
    if [[ "$choice" =~ ^[Uu]$ ]]; then
        echo "🚀 Modo Update: Preservando configurações..."
        MODE="update"
    fi
fi

if [ "$MODE" != "update" ]; then
    echo -e "\n🔔 Digite as chaves do YouTube agora (obtidas no Painel de Transmissão):"
    echo -n "   Chave YT (PT): "; read yt_pt < /dev/tty
    echo -n "   Chave YT (EN): "; read yt_en < /dev/tty
    echo -n "   Chave YT (ES): "; read yt_es < /dev/tty
    
    echo -e "\n🔔 Dados do Telegram (para avisos e monitoramento):"
    echo -n "   Token do Bot: "; read tg_token < /dev/tty
    echo -n "   Chat ID:      "; read tg_chat_id < /dev/tty
    
    echo -e "\n📂 Servidor de Sincronização:"
    echo -n "   URL [https://daorakids.com.br/util/stream/]: "; read sync_url < /dev/tty
    sync_url=${sync_url:-"https://daorakids.com.br/util/stream/"}
    echo -n "   Usuário [stream]: "; read sync_user < /dev/tty
    sync_user=${sync_user:-"stream"}
    echo -n "   Senha [stream]:   "; read sync_pass < /dev/tty
    sync_pass=${sync_pass:-"stream"}

    # Criar .env
    cat <<EOF > $ENV_FILE
YT_KEY_PT="$yt_pt"
YT_KEY_EN="$yt_en"
YT_KEY_ES="$yt_es"
TELEGRAM_TOKEN="$tg_token"
TELEGRAM_CHAT_ID="$tg_chat_id"
SYNC_URL="$sync_url"
SYNC_USER="$sync_user"
SYNC_PASS="$sync_pass"
EOF
    chown stream:stream $ENV_FILE
fi

echo -e "\n🐍 Rodando instalador técnico..."
python3 $BASE_DIR/install.py --auto

# 9. Limpeza final
rm -rf $TEMP_DIR
echo "✅ Setup concluído com sucesso!"
echo " "
echo "⚠️ ATENÇÃO: Para entrar no terminal do Streamer agora mesmo, digite:"
echo "   sudo su - stream"
echo " "
echo "🚀 Após o reboot automático (pelo install.py), o sistema entrará direto no usuário 'stream'."
echo " "
