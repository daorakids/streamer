#!/bin/bash

# ===============================================
#  🚀 SUPER-BOOTSTRAP DAORA KIDS LIVE (v2.9.2)
# ===============================================

# 1. Privilégios e Argumentos
if [ "$(id -u)" -ne 0 ]; then
    echo "🚨 Rode com sudo!"
    exit 1
fi

# Detecta modo forçado via argumento ($1)
FORCE_MODE=$(echo "$1" | tr '[:upper:]' '[:lower:]')

clear
echo -e "\033[1;32m🎨 INICIANDO DOMINAÇÃO v2.9.2\033[0m"

# 2. Garantir Sudoers para o usuário stream
if ! id "stream" &>/dev/null; then
    useradd -m -s /bin/bash stream
    echo "stream:stream" | chpasswd
    usermod -aG sudo,video,audio stream
fi
echo "stream ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/stream
chmod 0440 /etc/sudoers.d/stream

echo "🔄 Iniciando Setup do Sistema..."

# 3. Instalar dependências essenciais
echo "📦 Verificando dependências (ffmpeg, python3, libs)..."
apt-get update -qq
apt-get install -y -qq git python3-pip curl python3-dotenv python3-requests ffmpeg

# 4. OPÇÃO NUCLEAR: Expurgo total
echo "🧹 Expurgando cloud-init..."
systemctl stop cloud-init cloud-config cloud-final cloud-init-local 2>/dev/null
systemctl disable cloud-init cloud-config cloud-final cloud-init-local 2>/dev/null
DEBIAN_FRONTEND=noninteractive apt-get purge -y --allow-remove-essential cloud-init rpi-cloud-init-mods 2>/dev/null
rm -rf /etc/cloud /var/lib/cloud

# 5. AUTO-LOGIN FORÇADO
mkdir -p /etc/systemd/system/getty@tty1.service.d
cat <<EOF > /etc/systemd/system/getty@tty1.service.d/autologin.conf
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin stream --noclear %I \$TERM
EOF
systemctl daemon-reload

# 6. RECONSTRUÇÃO DO CMDLINE
CMDLINE="/boot/firmware/cmdline.txt"
[ ! -f "$CMDLINE" ] && CMDLINE="/boot/cmdline.txt"
if [ -f "$CMDLINE" ]; then
    mount -o remount,rw $(dirname $CMDLINE) 2>/dev/null
    ROOT_PART=$(grep -o "root=PARTUUID=[^ ]*" $CMDLINE)
    echo "console=tty3 quiet loglevel=3 logo.nologo vt.global_cursor_default=0 snd_bcm2835.enable_hdmi=1 $ROOT_PART rootfstype=ext4 fsck.repair=yes rootwait" > $CMDLINE
fi

# 7. Preparação de Pastas
mkdir -p /mnt/videos
chmod 777 /mnt/videos
mkdir -p /home/stream

# 8. Wizard de Configuração
ENV_FILE="/home/stream/.env"
MODE="update"

if [ "$FORCE_MODE" == "reconfig" ] || [ ! -f "$ENV_FILE" ]; then
    MODE="reconfig"
fi

echo -e "\n\033[1;33m📝 CONFIGURAÇÃO (Modo: $MODE)\033[0m"

if [ "$MODE" == "reconfig" ]; then
    OLD_SYNC_URL=$(grep "SYNC_URL=" $ENV_FILE 2>/dev/null | cut -d'"' -f2)
    DEFAULT_URL=${OLD_SYNC_URL:-"https://daorakids.com.br/util/stream/"}

    echo -n "   Chave YT (PT): "; read yt_pt < /dev/tty
    echo -n "   Chave YT (EN): "; read yt_en < /dev/tty
    echo -n "   Chave YT (ES): "; read yt_es < /dev/tty
    echo -n "   Token Telegram: "; read tg_token < /dev/tty
    echo -n "   Chat ID Telegram: "; read tg_chat_id < /dev/tty
    echo -n "   URL Sync [$DEFAULT_URL]: "; read sync_url < /dev/tty
    sync_url=${sync_url:-$DEFAULT_URL}
    echo -n "   Usuario Sync [stream]: "; read sync_user < /dev/tty
    sync_user=${sync_user:-"stream"}
    echo -n "   Senha Sync [stream]:   "; read sync_pass < /dev/tty
    sync_pass=${sync_pass:-"stream"}
    
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
else
    echo "✅ Usando configuracoes existentes (.env)"
fi

# 9. Download Final dos Scripts
echo "📦 Baixando scripts v2.9.2..."
TEMP_GIT="/tmp/daorakids_git"
rm -rf $TEMP_GIT
git clone --depth 1 https://github.com/daorakids/streamer.git $TEMP_GIT
cp -a $TEMP_GIT/home/stream/. /home/stream/
rm -rf /home/stream/videos
chown -R stream:stream /home/stream
chmod +x /home/stream/*.sh /home/stream/*.py

# 10. Ativando Serviços
echo "⚙️  Ativando servicos..."
cp /home/stream/*.service /etc/systemd/system/
cp /home/stream/*.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable daorakids-cerebro.timer daorakids-sync.timer daorakids-live.service
systemctl start daorakids-cerebro.timer daorakids-sync.timer

# 11. Dashboard HDMI
BASHRC="/home/stream/.bashrc"
sed -i '/DAORA KIDS/,/fi/d' $BASHRC
cat <<EOF >> $BASHRC
# --- DAORA KIDS DASHBOARD v2.9.2 ---
alias ver='/home/stream/ver_live.sh'
alias log='sudo journalctl -u daorakids-live.service -u daorakids-cerebro.service -u daorakids-sync.service -f'
alias monitor='/home/stream/ver_live.sh'
alias daora-stop='sudo systemctl stop daorakids-live.service daorakids-sync.timer daorakids-cerebro.timer && sudo pkill -f ffmpeg && echo "🛑 PARADO."'
alias daora-start='sudo systemctl start daorakids-cerebro.timer daorakids-sync.timer daorakids-live.service && echo "🚀 INICIADO."'

if [ "\$(tty)" = "/dev/tty1" ]; then
    sleep 3
    clear
    /home/stream/ver_live.sh
fi
EOF

echo -e "\n\033[1;32m✅ SUCESSO v2.9.2!\033[0m"
echo "🔄 Reiniciando..."
sync
sleep 5
reboot
