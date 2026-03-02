#!/bin/bash

# ===============================================
#  🚀 BOOTSTRAP DAORA KIDS LIVE 24H (v2.7)
# ===============================================

# 1. Verificar Privilégios e Estado do Disco
if [ "$(id -u)" -ne 0 ]; then
    echo "🚨 Por favor, rode com sudo: sudo bash setup.sh"
    exit 1
fi

echo "🛡️ Verificando integridade do disco..."
mount -o remount,rw / 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ AVISO: Não foi possível remontar como RW. O disco pode estar corrompido ou protegido."
fi

echo "🔄 Iniciando Setup do Sistema (isso pode demorar alguns minutos)..."

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

# 8. Execução INTERATIVA do Wizard
echo -e "\a" # BEEP!
echo "🐍 Iniciando Wizard de Configuração..."
cd $BASE_DIR
# Usamos o usuário stream para rodar o instalador com o TTY conectado
sudo -u stream python3 $BASE_DIR/install.py < /dev/tty

# 9. Limpeza final
rm -rf $TEMP_DIR
echo "✅ Setup concluído com sucesso!"
echo " "
echo "⚠️ ATENÇÃO: Para entrar no terminal do Streamer agora mesmo, digite:"
echo "   sudo su - stream"
echo " "
echo "🚀 Após o reboot automático (pelo install.py), o sistema entrará direto no usuário 'stream'."
echo " "
