#!/bin/bash

# =================================================
#  📺 MONITOR COMPLETO - DAORA KIDS 24H
# =================================================

clear
echo "-------------------------------------------------"
echo " 📡 MONITOR DE TRANSMISSÃO EM TEMPO REAL "
echo "-------------------------------------------------"
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

# Monitora Live, Cérebro e Sincronizador juntos
# Filtramos o FFmpeg 'frame=' para não poluir a tela, mas mantemos o resto
sudo journalctl -u daorakids-live.service -u daorakids-sync.service -u daorakids-cerebro.service -f -n 20 | grep --line-buffered -v "frame="

