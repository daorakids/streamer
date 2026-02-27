#!/bin/bash

# ===============================================
#  🚀 SETUP INICIAL DAORA KIDS LIVE 24H
# ===============================================

# 1. Update Geral de Pacotes (A seu pedido)
echo "🔄 Atualizando o sistema (pode demorar alguns minutos)..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Instalação de Dependências de Sistema
echo "📦 Instalando ferramentas necessárias (FFmpeg, Python, etc)..."
sudo apt-get install -y ffmpeg python3-pip python3-dotenv python3-requests git ntfs-3g cifs-utils curl bash-completion

# 3. Criação do Usuário 'stream' (Se não existir)
if ! id "stream" &>/dev/null; then
    echo "👤 Criando usuário 'stream'..."
    sudo useradd -m -s /bin/bash stream
    sudo usermod -aG sudo,video,audio stream
    # A senha será definida no Wizard Python
fi

# 4. Configurar Pasta de Trabalho
echo "📂 Preparando diretórios..."
sudo mkdir -p /home/stream
sudo chown stream:stream /home/stream

# 5. Download do Projeto (Supondo que você subiu para o seu GitHub)
# No momento do setup real, você trocará a URL abaixo:
# git clone https://github.com/bruno/daorakids.git /tmp/daorakids
# sudo cp -r /tmp/daorakids/* /home/stream/

# Como estou montando para você agora, vamos assumir que os arquivos já estão lá
# ou que o script será executado de dentro da pasta clonada.

# 6. Charme do .bashrc (O seu arquivo custom_bashrc)
if [ -f "/home/stream/custom_bashrc" ]; then
    echo "✨ Injetando o charme no .bashrc do stream..."
    cat /home/stream/custom_bashrc >> /home/stream/.bashrc
    sudo chown stream:stream /home/stream/.bashrc
fi

# 7. Disparar o Wizard de Instalação (Python)
echo "🐍 Iniciando o Wizard de Configuração..."
sudo python3 /home/stream/install.py
