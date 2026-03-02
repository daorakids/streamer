#!/bin/bash

# ===============================================
#  🚀 SUPER-BOOTSTRAP DAORA KIDS LIVE (v2.8.22)
#  (Single File Domination - No Cache Issues)
# ===============================================

# 1. Privilégios e Remontagem
if [ "$(id -u)" -ne 0 ]; then
    echo "🚨 Rode com sudo!"
    exit 1
fi

clear
echo -e "\033[1;32m🎨 INICIANDO DOMINAÇÃO HDMI v2.8.22\033[0m"

# 2. Garantir Sudoers para o usuário stream
echo "👤 Configurando privilegios do usuario stream..."
if ! id "stream" &>/dev/null; then
    useradd -m -s /bin/bash stream
    echo "stream:stream" | chpasswd
    usermod -aG sudo,video,audio stream
fi
echo "stream ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/stream
chmod 0440 /etc/sudoers.d/stream

# 3. OPÇÃO NUCLEAR: Expurgo total do que suja o HDMI
echo "🧹 Expurgando fantasmas (cloud-init)..."
killall apt apt-get dpkg 2>/dev/null
rm -f /var/lib/dpkg/lock* 2>/dev/null
DEBIAN_FRONTEND=noninteractive apt-get purge -y --allow-remove-essential cloud-init rpi-cloud-init-mods
rm -rf /etc/cloud /var/lib/cloud

# 4. AUTO-LOGIN FORÇADO (Direct systemd override)
echo "🖥️  Forcando Auto-login no tty1..."
mkdir -p /etc/systemd/system/getty@tty1.service.d
cat <<EOF > /etc/systemd/system/getty@tty1.service.d/autologin.conf
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin stream --noclear %I \$TERM
EOF
systemctl daemon-reload

# 5. RECONSTRUÇÃO DO CMDLINE (Boot limpo e HDMI ON)
echo "🔇 Reconstruindo cmdline.txt..."
CMDLINE="/boot/firmware/cmdline.txt"
[ ! -f "$CMDLINE" ] && CMDLINE="/boot/cmdline.txt"

if [ -f "$CMDLINE" ]; then
    mount -o remount,rw $(dirname $CMDLINE) 2>/dev/null
    # Pega apenas os parametros essenciais (root e console serial)
    ROOT_PART=$(grep -o "root=PARTUUID=[^ ]*" $CMDLINE)
    # Monta a nova linha do zero para nao ter erro
    echo "console=tty3 quiet loglevel=3 logo.nologo vt.global_cursor_default=0 snd_bcm2835.enable_hdmi=1 $ROOT_PART rootfstype=ext4 fsck.repair=yes rootwait" > $CMDLINE
fi

# 6. Preparação de Pastas e Vídeos
echo "📂 Preparando diretorios..."
mkdir -p /mnt/videos
chmod 777 /mnt/videos
mkdir -p /home/stream

# 7. Wizard de Configuração (Interativo)
echo -e "\n\033[1;33m📝 CONFIGURAÇÃO DE CREDENCIAIS\033[0m"
ENV_FILE="/home/stream/.env"

if [ -f "$ENV_FILE" ]; then
    echo -n "⚠️  Instalacao detectada! Deseja [U] Atualizar ou [R] Reconfigurar? (U/R): "
    read choice < /dev/tty
    [ "$choice" != "U" ] && [ "$choice" != "u" ] && MODE="reconfig"
else
    MODE="reconfig"
fi

if [ "$MODE" == "reconfig" ]; then
    echo -n "   Chave YT (PT): "; read yt_pt < /dev/tty
    echo -n "   Chave YT (EN): "; read yt_en < /dev/tty
    echo -n "   Chave YT (ES): "; read yt_es < /dev/tty
    echo -n "   Token Telegram: "; read tg_token < /dev/tty
    echo -n "   Chat ID Telegram: "; read tg_chat_id < /dev/tty
    
    cat <<EOF > $ENV_FILE
YT_KEY_PT="$yt_pt"
YT_KEY_EN="$yt_en"
YT_KEY_ES="$yt_es"
TELEGRAM_TOKEN="$tg_token"
TELEGRAM_CHAT_ID="$tg_chat_id"
SYNC_URL="https://daorakids.com.br/util/stream/"
EOF
    chown stream:stream $ENV_FILE
fi

# 8. Download Final dos Scripts (Via GIT agora que o sistema esta limpo)
echo "📦 Baixando scripts atualizados..."
TEMP_GIT="/tmp/daorakids_git"
rm -rf $TEMP_GIT
git clone --depth 1 https://github.com/daorakids/streamer.git $TEMP_GIT
cp -a $TEMP_GIT/home/stream/. /home/stream/
chown -R stream:stream /home/stream
chmod +x /home/stream/*.sh /home/stream/*.py

# 9. Ativando Serviços
echo "⚙️  Ativando servicos..."
cp /home/stream/*.service /etc/systemd/system/
cp /home/stream/*.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable daorakids-cerebro.timer daorakids-sync.timer daorakids-live.service
systemctl start daorakids-cerebro.timer

# 10. Dashboard HDMI
echo "📊 Configurando Dashboard..."
BASHRC="/home/stream/.bashrc"
sed -i '/DAORA KIDS/,/fi/d' $BASHRC
cat <<EOF >> $BASHRC
# --- DAORA KIDS DASHBOARD v2.8.22 ---
alias ver='/home/stream/ver_live.sh'
alias log='sudo journalctl -u daorakids-live.service -u daorakids-cerebro.service -u daorakids-sync.service -f'
if [ "\$(tty)" = "/dev/tty1" ]; then
    sleep 3
    clear
    /home/stream/ver_live.sh
fi
EOF

echo -e "\n\033[1;32m✅ SUCESSO ABSOLUTO! v2.8.22\033[0m"
echo "🔄 Reiniciando em 5 segundos para dominar o HDMI..."
sync
sleep 5
reboot
