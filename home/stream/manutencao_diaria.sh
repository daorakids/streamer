#!/bin/bash

# ===============================================
#  🧹 ROTINA DE RECICLAGEM E CHECK-UP DAORA KIDS
# ===============================================

# Carregar variáveis do .env para o Telegram
source /home/stream/.env
LOG_FILE="/home/stream/manutencao.log"

send_tg() {
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID&text=$1&parse_mode=HTML" > /dev/null
}

echo "[$(date)] 🛑 Parando streaming para descanso..." >> $LOG_FILE
sudo systemctl stop daorakids-live.service

# Dorme das 01:00 até as 04:45
sleep 13500 

echo "[$(date)] 🩺 Iniciando Check-up de Saúde..." >> $LOG_FILE

ISSUES=""

# 1. Check de Temperatura (> 70°C é alerta para RPi3 em idle)
TEMP=$(vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*')
if (( $(echo "$TEMP > 70.0" | bc -l) )); then 
    ISSUES="$ISSUES\n⚠️ <b>Temperatura Alta:</b> $TEMP°C"
fi

# 2. Check de Disco MicroSD (> 90% usado)
DISK_SD=$(df -h / | awk '/\// {print $5}' | sed 's/%//')
if [ "$DISK_SD" -gt 90 ]; then
    ISSUES="$ISSUES\n💾 <b>MicroSD quase cheio:</b> $DISK_SD%"
fi

# 3. Check de Erros no File System (Modo Read-Only)
touch /home/stream/.fs_test 2>/dev/null && rm /home/stream/.fs_test 2>/dev/null
if [ $? -ne 0 ]; then
    ISSUES="$ISSUES\n🚨 <b>ERRO CRÍTICO:</b> File System em Read-Only!"
fi

# Só envia Telegram se houver problemas detectados
if [ ! -z "$ISSUES" ]; then
    REPORT="🚨 <b>ALERTA DE SAÚDE - DAORA KIDS</b>\n$ISSUES\n\n♻️ <i>Limpando lixo e reiniciando...</i>"
    send_tg "$REPORT"
fi

# Limpeza e Updates
sudo apt-get update && sudo apt-get autoremove -y && sudo apt-get autoclean
sudo journalctl --vacuum-time=1d

echo "[$(date)] 🔄 Rebootando!" >> $LOG_FILE
sudo reboot
