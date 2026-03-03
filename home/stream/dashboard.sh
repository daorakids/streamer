#!/bin/bash

# =================================================
#  📺 MONITOR COMPLETO - DAORA KIDS 24H (v3.3)
# =================================================

# Força suporte a cores se estiver no console físico
if [ "$TERM" = "linux" ]; then
    export TERM=xterm-256color
fi

# Definição de Cores ANSI
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_RED="\033[1;31m"
C_GREEN="\033[1;32m"
C_YELLOW="\033[1;33m"
C_BLUE="\033[1;34m"
C_MAGENTA="\033[1;35m"
C_CYAN="\033[1;36m"

clear
echo -e "${C_MAGENTA}-------------------------------------------------${C_RESET}"
echo -e "${C_MAGENTA}${C_BOLD}  📺 MONITOR COMPLETO - DAORA KIDS v3.3${C_RESET}"
echo -e "${C_MAGENTA}-------------------------------------------------${C_RESET}"

echo " "
echo -e "${C_BOLD}📌 [STATUS ATUAL]${C_RESET}"
if [ -f "/home/stream/.current_config" ]; then
    source "/home/stream/.current_config"
    TEMP=$(vcgencmd measure_temp | cut -d'=' -f2)
    echo -e "   ▶ Idioma: ${C_CYAN}${PASTA_VIDEOS##*/}${C_RESET}"
    echo -e "   ▶ Modo:   ${C_CYAN}$MODO${C_RESET}"
    echo -e "   ▶ Temp:   ${C_YELLOW}$TEMP${C_RESET}"
else
    echo -e "   ▶ Status: ${C_YELLOW}Aguardando Scheduler...${C_RESET}"
fi
echo " "
echo -e "${C_MAGENTA}-------------------------------------------------${C_RESET}"
echo -e " ${C_BOLD}📝 LOGS CONSOLIDADOS (Ctrl+C para sair): ${C_RESET}"
echo -e "${C_MAGENTA}-------------------------------------------------${C_RESET}"

# Motor de Colorização Inteligente (AWK)
# Live = Verde, Scheduler = Magenta, Sync = Ciano, Erros = Vermelho
sudo journalctl -u daorakids-live.service -u daorakids-sync.service -u daorakids-scheduler.service -f -n 20 | \
awk -v grn="$C_GREEN" -v mag="$C_MAGENTA" -v cyn="$C_CYAN" -v red="$C_RED" -v rst="$C_RESET" '
    /daorakids-live/ { print grn $0 rst; next }
    /daorakids-scheduler/ { print mag $0 rst; next }
    /daorakids-sync/ { print cyn $0 rst; next }
    /ERROR|Fail|fail|crit/ { print red $0 rst; next }
    { print $0 }
' | grep --line-buffered -v "frame="
