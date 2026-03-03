#!/bin/bash

# =================================================
#  📺 MONITOR COMPLETO - DAORA KIDS 24H (v3.2.2)
# =================================================

# Força suporte a cores se estiver no console físico
if [ "$TERM" = "linux" ]; then
    export TERM=xterm-256color
fi

# Definição de Cores ANSI
C_MAGENTA="\033[1;35m"
C_CYAN="\033[1;36m"
C_GREEN="\033[1;32m"
C_RESET="\033[0m"

clear
echo -e "${C_MAGENTA}-------------------------------------------------${C_RESET}"
echo -e "${C_MAGENTA}  📺 MONITOR COMPLETO - DAORA KIDS v3.2.2${C_RESET}"
echo -e "${C_MAGENTA}-------------------------------------------------${C_RESET}"

echo " "
echo "📌 [STATUS ATUAL]"
if [ -f "/home/stream/.current_config" ]; then
    source "/home/stream/.current_config"
    TEMP=$(vcgencmd measure_temp | cut -d'=' -f2)
    echo "   ▶ Idioma: ${PASTA_VIDEOS##*/}"
    echo "   ▶ Modo:   $MODO"
    echo "   ▶ Temp:   $TEMP"
else
    echo "   ▶ Status: Aguardando Cérebro..."
fi
echo " "
echo "-------------------------------------------------"
echo " 📝 LOGS CONSOLIDADOS (Ctrl+C para sair): "
echo "-------------------------------------------------"

# Monitora Live, Scheduler e Sincronizador juntos
# Filtramos o FFmpeg 'frame=' para não poluir a tela, mas mantemos o resto
sudo journalctl -u daorakids-live.service -u daorakids-sync.service -u daorakids-scheduler.service -f -n 20 | grep --line-buffered -v "frame="

