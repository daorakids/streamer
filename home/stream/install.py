#!/usr/bin/env python3
import os
import subprocess
import getpass
import socket
from urllib.parse import urlparse

def run_cmd(cmd, sudo=False):
    if sudo: cmd = f"sudo {cmd}"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def get_ips():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal = s.getsockname()[0]
        s.close()
    except: internal = "N/A"
    return internal

def setup_wizard():
    print("\n" + "="*40)
    print(" 🎨 BEM-VINDO AO INSTALADOR DAORA KIDS v2.0 ")
    print("="*40 + "\n")

    # 1. YouTube
    yt_pt = input("Chave YouTube (PT): ").strip()
    yt_en = input("Chave YouTube (EN): ").strip()
    yt_es = input("Chave YouTube (ES): ").strip()

    # 2. Telegram
    tg_token = input("Token do Bot Telegram: ").strip()
    tg_chat_id = input("Chat ID do Telegram: ").strip()

    # 3. Sync Server
    print("\n📂 Configurações de Sincronização de Vídeos:")
    sync_url = input("URL do Servidor [https://daorakids.com.br/util/stream/]: ").strip() or "https://daorakids.com.br/util/stream/"
    sync_user = input("Usuário do Servidor [stream]: ").strip() or "stream"
    sync_pass = input("Senha do Servidor [stream]: ").strip() or "stream"

    # Cálculo do cut-dirs para o wget (quantas pastas pular na URL)
    parsed_url = urlparse(sync_url)
    path_parts = [p for p in parsed_url.path.split('/') if p]
    cut_dirs = len(path_parts)

    # 4. Senha local
    stream_pass = getpass.getpass("\nDefina a senha para o usuário local 'stream': ")

    # 5. Gerar .env
    env_content = f"""YT_KEY_PT="{yt_pt}"
YT_KEY_EN="{yt_en}"
YT_KEY_ES="{yt_es}"
TELEGRAM_TOKEN="{tg_token}"
TELEGRAM_CHAT_ID="{tg_chat_id}"
SYNC_URL="{sync_url}"
SYNC_USER="{sync_user}"
SYNC_PASS="{sync_pass}"
"""
    with open("/home/stream/.env", "w") as f:
        f.write(env_content)
    run_cmd("chown stream:stream /home/stream/.env", sudo=True)

    # 6. Pendrive
    usb_dev = "/dev/sda1" 
    run_cmd("mkdir -p /mnt/videos", sudo=True)
    with open("/etc/fstab", "r") as f:
        if usb_dev not in f.read():
            line = f"\n{usb_dev} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000 0 0\n"
            with open("/tmp/fstab", "w") as tmp_f:
                tmp_f.write(f.read() + line)
            run_cmd("cp /tmp/fstab /etc/fstab", sudo=True)
    run_cmd("mount -a", sudo=True)

    # 7. Sync Service (Preservando Estrutura de Pastas)
    # -nH (No Host): não cria pasta do domínio
    # --cut-dirs: remove o caminho do servidor para salvar pt/ en/ es/ direto na raiz do pendrive
    sync_service = f"""[Unit]
Description=Sincroniza videos do site para o Pi
After=network-online.target

[Service]
Type=oneshot
User=stream
ExecStart=/usr/bin/wget --user={sync_user} --password={sync_pass} -c -N -r -np -nH --cut-dirs={cut_dirs} -A mp4 --tries=10 -P /mnt/videos {sync_url}
"""
    with open("/tmp/daorakids-sync.service", "w") as f:
        f.write(sync_service)
    run_cmd("cp /tmp/daorakids-sync.service /etc/systemd/system/daorakids-sync.service", sudo=True)

    # 8. Auto-login e Outros
    run_cmd("systemctl daemon-reload", sudo=True)
    run_cmd("systemctl enable --now daorakids-sync.timer", sudo=True)
    
    # Cron
    cron_jobs = f"""*/5 * * * * /usr/bin/python3 /home/stream/cerebro.py >> /home/stream/cerebro.log 2>&1
00 01 * * * /bin/bash /home/stream/manutencao_diaria.sh >> /home/stream/manutencao.log 2>&1
"""
    with open("/tmp/mycron", "w") as f:
        f.write(cron_jobs)
    run_cmd("crontab -u stream /tmp/mycron", sudo=True)

    print("\n✅ Instalação concluída. Reiniciando...")
    run_cmd("sleep 5 && reboot", sudo=True)

if __name__ == "__main__":
    setup_wizard()
