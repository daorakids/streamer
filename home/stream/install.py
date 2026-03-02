#!/usr/bin/env python3
import os
import subprocess
import getpass
import socket
from urllib.parse import urlparse

def run_cmd(cmd, sudo=False):
    if sudo: cmd = f"sudo {cmd}"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def setup_wizard():
    print("\n" + "="*40)
    print(" 🎨 INSTALADOR/UPDATER DAORA KIDS v2.3 ")
    print("="*40 + "\n")

    is_update = False
    if os.path.exists("/home/stream/.env"):
        choice = input("⚠️  Instalação detectada! Deseja [U] Atualizar Scripts ou [R] Reinstalar tudo? (U/R): ").strip().lower()
        if choice == 'u':
            is_update = True
            print("🚀 Modo Update: Preservando configurações e atualizando serviços...")
        else:
            print("🧹 Modo Reinstalação: Solicitando novas configurações...")

    # Parar serviços antes de mexer
    print("⏹ Parando serviços para manutenção...")
    run_cmd("systemctl stop daorakids-live.service daorakids-sync.service daorakids-sync.timer", sudo=True)
    run_cmd("pkill -f ffmpeg", sudo=True)

    if not is_update:
            # 1. YouTube
            print("🌐 Configurando DNS de backup (8.8.8.8, 1.1.1.1)...")
            dns_conf = "\nstatic domain_name_servers=8.8.8.8 1.1.1.1\n"
            with open("/etc/dhcpcd.conf", "r") as f:
                if "static domain_name_servers" not in f.read():
                    with open("/tmp/dhcpcd.conf", "w") as tmp_f:
                        tmp_f.write(f.read() + dns_conf)
                    run_cmd("cp /tmp/dhcpcd.conf /etc/dhcpcd.conf", sudo=True)
            
            # Força DNS imediato para o restante da instalação
            run_cmd("echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf", sudo=False)
            run_cmd("echo 'nameserver 1.1.1.1' | sudo tee -a /etc/resolv.conf", sudo=False)
        
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
    else:
        # No modo update, apenas carregamos os dados do .env existente para o sync_service
        from dotenv import load_dotenv
        load_dotenv("/home/stream/.env")
        sync_url = os.getenv("SYNC_URL")
        sync_user = os.getenv("SYNC_USER")
        sync_pass = os.getenv("SYNC_PASS")

    # Re-calcula cut_dirs (importante se mudou a URL)
    parsed_url = urlparse(sync_url)
    path_parts = [p for p in parsed_url.path.split('/') if p]
    cut_dirs = len(path_parts)

    # 6. Pendrive (Otimizado para evitar corrupção)
    usb_dev = "/dev/sda1" 
    run_cmd("mkdir -p /mnt/videos", sudo=True)
    with open("/etc/fstab", "r") as f:
        if usb_dev not in f.read():
            # flush: grava dados imediatamente / noatime: reduz escritas no disco
            line = f"\n{usb_dev} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0\n"
            with open("/tmp/fstab", "w") as tmp_f:
                tmp_f.write(f.read() + line)
            run_cmd("cp /tmp/fstab /etc/fstab", sudo=True)
    run_cmd("mount -a", sudo=True)

    # 7. Sync Service (Com retentativa automática e proteção de rede)
    sync_service = f"""[Unit]
Description=Sincroniza videos do site para o Pi
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=stream
ExecStart=/usr/bin/wget --user={sync_user} --password={sync_pass} -c -N -r -np -nH --cut-dirs={cut_dirs} -A mp4 --tries=10 -P /mnt/videos {sync_url}
Restart=on-failure
RestartSec=30s
"""
    with open("/tmp/daorakids-sync.service", "w") as f:
        f.write(sync_service)
    run_cmd("cp /tmp/daorakids-sync.service /etc/systemd/system/daorakids-sync.service", sudo=True)

    # 7.1 Live Service (Esperando explicitamente pelo pendrive)
    live_service = """[Unit]
Description=Daora Kids Live Streaming Service
After=network-online.target mnt-videos.mount
Requires=mnt-videos.mount

[Service]
Type=simple
User=stream
WorkingDirectory=/home/stream
ExecStart=/bin/bash /home/stream/iniciar_live.sh
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
"""
    with open("/tmp/daorakids-live.service", "w") as f:
        f.write(live_service)
    run_cmd("cp /tmp/daorakids-live.service /etc/systemd/system/daorakids-live.service", sudo=True)

    # ... (restante do código até o final) ...

    print("\n✅ Operação concluída com sucesso!")
    print("💾 Sincronizando e desmontando volumes com segurança...")
    run_cmd("sync", sudo=True)
    run_cmd("umount /mnt/videos", sudo=True)
    print("🔄 O sistema irá reiniciar em 5 segundos...")
    run_cmd("sleep 5 && sudo reboot", sudo=False) # reboot já é chamado via sudo se necessário na func

if __name__ == "__main__":
    setup_wizard()
