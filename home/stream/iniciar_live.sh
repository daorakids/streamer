#!/bin/bash

# DEPOSITAR ESSE ARQUIVO EM
# /home/stream/iniciar_live.sh

# MUDAR O ACESSO DO ARQUIVO PARA EXECUTAVEL/PROGRAMA
# chmod +x /home/stream/iniciar_live.sh

# SERVICO QUE INICIA A TRANSMISSAO QDO O PC LIGAR
# sudo nano /etc/systemd/system/daorakids-live.service

# HABILITANDO O SERVICO NO BOOT PELA PRIMEIRA VEZ
# sudo systemctl daemon-reload
# sudo systemctl enable daorakids-live.service
# sudo systemctl start daorakids-live.service

# PARAR A TRANSMISSAO
# sudo systemctl stop daorakids-live.service

# VOLTAR A TRANSMISSAO
# sudo systemctl start daorakids-live.service

# DESABILITAR O SERVICO DE BOOT
# sudo systemctl disable daorakids-live.service


# ================================


# ATIVE O TIMER
# sudo systemctl daemon-reload
# sudo systemctl enable --now daorakids-sync.timer

# Configurações do YouTube
RTMP_URL="rtmp://a.rtmp.youtube.com/live2"
CONFIG_FILE="/home/stream/.current_config"
PLAYLIST="/tmp/playlist_daorakids.txt"

echo "================================================="
echo " 🚀 INICIANDO SERVIÇO DAORA KIDS LIVE 24H "
echo "================================================="
echo " "
echo "⏳ Dando um respiro de 10s estabilizar..."

sleep 10
while true; do
    # 1. Carregar Configuração Dinâmica
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    else
        echo "⚠️ Aguardando Cerebro.py gerar configuracao..."
        echo "   (Dica: Use 'log' para ver detalhes do Cerebro)"
        sleep 30
        continue
    fi

    HORA=$(date +'%H:%M:%S')
    echo " "
    echo "🔄 [$HORA] Preparando live ($MODO - $PASTA_VIDEOS)..."
    
    # 2. Montar Playlist baseada no MODO (Sequential ou Random)
    if [ "$MODO" == "random" ]; then
        ls "$PASTA_VIDEOS"/*.mp4 | shuf > "$PLAYLIST.tmp"
    else
        ls "$PASTA_VIDEOS"/*.mp4 > "$PLAYLIST.tmp"
    fi

    # Formatar para o FFmpeg
    > "$PLAYLIST"
    CONTAGEM=0
    while read -r video; do
        echo "file '$video'" >> "$PLAYLIST"
        CONTAGEM=$((CONTAGEM+1))
    done < "$PLAYLIST.tmp"
    rm "$PLAYLIST.tmp"
    
    if [ $CONTAGEM -eq 0 ]; then
        echo "🚨 ERRO: Nenhum vídeo encontrado em $PASTA_VIDEOS"
        sleep 60
        continue
    fi

    echo "📋 Fila atualizada! Total: $CONTAGEM vídeos ($MODO)."
    echo "▶️  Iniciando streaming para o YouTube..."
    echo "-------------------------------------------------"
    
    # 3. Inicia o FFmpeg
    # O Cérebro matará esse processo se o idioma mudar.
    ffmpeg -re -thread_queue_size 4096 -f concat -safe 0 -i "$PLAYLIST" -max_muxing_queue_size 4096 -c copy -f flv "$RTMP_URL/$CHAVE"
    
    echo " "
    echo "⚠️ [$HORA] FFmpeg parou (fim da fila, queda ou interrupção do Cérebro)."
    echo "⏳ Reiniciando o ciclo em 5 segundos..."
    sleep 5
done
