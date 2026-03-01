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

    # 7. Sync Service (Sempre gera de novo para garantir que está atualizado)
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

    # 8. Sudo sem senha para o journalctl
    sudo_rule = "stream ALL=(ALL) NOPASSWD: /usr/bin/journalctl"
    with open("/tmp/daorakids-logs", "w") as f:
        f.write(sudo_rule)
    run_cmd("cp /tmp/daorakids-logs /etc/sudoers.d/daorakids-logs", sudo=True)

    # 9. Configurar Monitoramento Automático no Login (Verifica se já existe para não duplicar)
    bashrc_path = "/home/stream/.bashrc"
    with open(bashrc_path, "r") as f:
        if "monitor" not in f.read():
            monitor_cmd = "\n# --- MONITORAMENTO AUTOMÁTICO DA LIVE ---\n/home/stream/ver_live.sh\n"
            with open(bashrc_path, "a") as f_append:
                f_append.write(monitor_cmd)

    # 10. Auto-login e Outros (Forçar usuário 'stream' no terminal)
    print("👤 Configurando auto-login para o usuário 'stream'...")
    autologin_dir = "/etc/systemd/system/getty@tty1.service.d"
    run_cmd(f"mkdir -p {autologin_dir}", sudo=True)
    
    autologin_conf = """[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin stream --noclear %I $TERM
"""
    with open("/tmp/autologin.conf", "w") as f:
        f.write(autologin_conf)
    run_cmd(f"cp /tmp/autologin.conf {autologin_dir}/autologin.conf", sudo=True)

    run_cmd("systemctl daemon-reload", sudo=True)
    run_cmd("systemctl enable --now daorakids-sync.timer", sudo=True)
    run_cmd("systemctl enable --now daorakids-live.service", sudo=True)
    
    # Cron
    cron_jobs = f"""*/5 * * * * /usr/bin/python3 /home/stream/cerebro.py >> /home/stream/cerebro.log 2>&1
00 01 * * * /bin/bash /home/stream/manutencao_diaria.sh >> /home/stream/manutencao.log 2>&1
"""
    with open("/tmp/mycron", "w") as f:
        f.write(cron_jobs)
    run_cmd("crontab -u stream /tmp/mycron", sudo=True)

    print("\n✅ Operação concluída com sucesso!")
    print("🔄 O sistema irá reiniciar em 10 segundos...")
    run_cmd("sleep 10 && sudo reboot", sudo=False) # reboot já é chamado via sudo se necessário na func

if __name__ == "__main__":
    setup_wizard()

if __name__ == "__main__":
    setup_wizard()
