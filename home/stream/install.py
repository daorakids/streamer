#!/usr/bin/env python3
import os
import subprocess
import getpass
import socket
from urllib.parse import urlparse
from dotenv import load_dotenv

def run_cmd(cmd, sudo=False):
    if sudo: cmd = f"sudo {cmd}"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def get_input(prompt, required=True):
    while True:
        val = input(prompt).strip()
        if required and not val:
            print("⚠️  Este campo é obrigatório. Por favor, digite um valor.")
            continue
        return val

def setup_wizard():
    print("\n" + "="*40)
    print(" 🎨 INSTALADOR/UPDATER DAORA KIDS v2.7 ")
    print("="*40 + "\n")

    # ... (bloco de detecção de update e parada de serviços mantido) ...

    if not is_update:
        # 1. DNS & YouTube
        print("🌐 Configurando DNS de backup (8.8.8.8, 1.1.1.1)...")
        # ... (DNS config mantido) ...

        yt_pt = get_input("Chave YouTube (PT): ")
        yt_en = get_input("Chave YouTube (EN): ")
        yt_es = get_input("Chave YouTube (ES): ")

        # 2. Telegram
        tg_token = get_input("Token do Bot Telegram: ")
        tg_chat_id = get_input("Chat ID do Telegram: ")

        # 3. Sync Server
        print("\n📂 Configurações de Sincronização de Vídeos:")
        sync_url = get_input("URL do Servidor [https://daorakids.com.br/util/stream/]: ", required=False) or "https://daorakids.com.br/util/stream/"
        sync_user = get_input("Usuário do Servidor [stream]: ", required=False) or "stream"
        sync_pass = get_input("Senha do Servidor [stream]: ", required=False) or "stream"

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
        # No modo update, apenas carregamos os dados do .env existente
        load_dotenv("/home/stream/.env")
        sync_url = os.getenv("SYNC_URL")
        sync_user = os.getenv("SYNC_USER")
        sync_pass = os.getenv("SYNC_PASS")

    # Re-calcula cut_dirs (importante se mudou a URL)
    parsed_url = urlparse(sync_url)
    path_parts = [p for p in parsed_url.path.split('/') if p]
    cut_dirs = len(path_parts)

    # 6. Pendrive (Otimizado: Busca UUID para evitar erro de montagem)
    run_cmd("mkdir -p /mnt/videos", sudo=True)
    uuid_raw = run_cmd("blkid -s UUID -o value /dev/sda1").stdout.strip()
    if uuid_raw:
        with open("/etc/fstab", "r") as f:
            if uuid_raw not in f.read():
                line = f"\nUUID={uuid_raw} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0\n"
                with open("/tmp/fstab", "w") as tmp_f:
                    tmp_f.write(f.read() + line)
                run_cmd("cp /tmp/fstab /etc/fstab", sudo=True)
    else:
        usb_dev = "/dev/sda1"
        with open("/etc/fstab", "r") as f:
            if usb_dev not in f.read():
                line = f"\n{usb_dev} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0\n"
                with open("/tmp/fstab", "w") as tmp_f:
                    tmp_f.write(f.read() + line)
                run_cmd("cp /tmp/fstab /etc/fstab", sudo=True)
    run_cmd("mount -a", sudo=True)

    # 6.1 Ativar Hardware Watchdog
    print("🐕 Ativando Hardware Watchdog (Proteção contra travamentos)...")
    run_cmd("modprobe bcm2835_wdt", sudo=True)
    with open("/etc/modules", "r") as f:
        if "bcm2835_wdt" not in f.read():
            run_cmd('echo "bcm2835_wdt" | sudo tee -a /etc/modules', sudo=False)
    run_cmd("apt-get install -y watchdog", sudo=True)
    run_cmd('echo "watchdog-device = /dev/watchdog" | sudo tee -a /etc/watchdog.conf', sudo=False)
    run_cmd('echo "watchdog-timeout = 15" | sudo tee -a /etc/watchdog.conf', sudo=False)
    run_cmd('echo "max-load-1 = 24" | sudo tee -a /etc/watchdog.conf', sudo=False)
    run_cmd("systemctl enable --now watchdog", sudo=True)

    # 7. Sync Service
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

    # 7.1 Live Service
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

    # 8. Sudo sem senha para journalctl
    sudo_rule = "stream ALL=(ALL) NOPASSWD: /usr/bin/journalctl"
    with open("/tmp/daorakids-logs", "w") as f:
        f.write(sudo_rule)
    run_cmd("cp /tmp/daorakids-logs /etc/sudoers.d/daorakids-logs", sudo=True)

    # 9. Monitoramento Automático no Login
    bashrc_path = "/home/stream/.bashrc"
    with open(bashrc_path, "r") as f:
        if "ver_live.sh" not in f.read():
            monitor_cmd = "\n# --- MONITORAMENTO AUTOMÁTICO DA LIVE ---\n/home/stream/ver_live.sh\n"
            with open(bashrc_path, "a") as f_append:
                f_append.write(monitor_cmd)

    # 10. Auto-login e Outros
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
    run_cmd("systemctl enable daorakids-sync.timer", sudo=True)
    run_cmd("systemctl enable daorakids-live.service", sudo=True)
    
    # Cron
    cron_jobs = f"""*/5 * * * * /usr/bin/python3 /home/stream/cerebro.py >> /home/stream/cerebro.log 2>&1
00 01 * * * /bin/bash /home/stream/manutencao_diaria.sh >> /home/stream/manutencao.log 2>&1
"""
    with open("/tmp/mycron", "w") as f:
        f.write(cron_jobs)
    run_cmd("crontab -u stream /tmp/mycron", sudo=True)

    print("\n✅ Operação concluída com sucesso!")
    print("💾 Sincronizando e desmontando volumes com segurança...")
    run_cmd("sync", sudo=True)
    run_cmd("umount /mnt/videos", sudo=True)
    print("🔄 O sistema irá reiniciar em 5 segundos...")
    run_cmd("sleep 5 && sudo reboot", sudo=False)

if __name__ == "__main__":
    setup_wizard()
