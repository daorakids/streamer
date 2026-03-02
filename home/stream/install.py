#!/usr/bin/env python3
import os
import subprocess
import getpass
import socket
import datetime
import time
from urllib.parse import urlparse
from dotenv import load_dotenv

def run_cmd(cmd, sudo=False, capture=False):
    if sudo: cmd = f"sudo {cmd}"
    if capture:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return subprocess.run(cmd, shell=True, text=True)

def get_input(prompt, required=True):
# ... (rest of function unchanged)
    while True:
        try:
            val = input(prompt).strip()
            if required and not val:
                print("⚠️  Este campo é obrigatório. Por favor, digite um valor.")
                continue
            return val
        except EOFError:
            return ""

def setup_wizard():
    print("\n" + "="*40)
    print(" 🎨 INSTALADOR/UPDATER DAORA KIDS v2.8.2 ")
    print("="*40 + "\n")

    # Detecta se é Update ou Nova Instalação
    is_update = os.path.exists("/home/stream/.env")
    load_dotenv("/home/stream/.env")

    # Parar serviços antes de mexer
    print("⏹ Parando serviços para manutenção...")
    run_cmd("systemctl stop daorakids-live.service daorakids-sync.service daorakids-sync.timer", sudo=True)
    run_cmd("pkill -f ffmpeg", sudo=True)

    if not is_update:
        # 1. DNS
        print("🌐 Configurando DNS de backup (8.8.8.8, 1.1.1.1)...")
        dns_conf = "\nstatic domain_name_servers=8.8.8.8 1.1.1.1\n"
        try:
            with open("/etc/dhcpcd.conf", "r") as f:
                content = f.read()
            if "static domain_name_servers" not in content:
                with open("/tmp/dhcpcd.conf", "w") as tmp_f:
                    tmp_f.write(content + dns_conf)
                run_cmd("cp /tmp/dhcpcd.conf /etc/dhcpcd.conf", sudo=True)
        except: pass
        
        # Força DNS imediato
        run_cmd("echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf", sudo=False)
        run_cmd("echo 'nameserver 1.1.1.1' | sudo tee -a /etc/resolv.conf", sudo=False)

    # Pegar dados do .env (Já preenchido pelo setup.sh)
    sync_url = os.getenv("SYNC_URL") or "https://daorakids.com.br/util/stream/"
    sync_user = os.getenv("SYNC_USER") or "stream"
    sync_pass = os.getenv("SYNC_PASS") or "stream"

    # Re-calcula cut_dirs
    parsed_url = urlparse(sync_url)
    path_parts = [p for p in parsed_url.path.split('/') if p]
    cut_dirs = len(path_parts)

    # 6. Pendrive (Otimizado e Seguro)
    print("💾 Configurando montagem do Pendrive...")
    run_cmd("mkdir -p /mnt/videos", sudo=True)
    
    # Lê o fstab atual do sistema
    try:
        with open("/etc/fstab", "r") as f:
            fstab_content = f.read()
    except:
        fstab_content = ""

    # SEGURO: Só mexemos no fstab se o ponto de montagem /mnt/videos NÃO existir
    if "/mnt/videos" not in fstab_content:
        # Busca UUID do sda1 (pendrive) com sudo e captura de texto
        res = run_cmd("blkid -s UUID -o value /dev/sda1", sudo=True, capture=True)
        uuid_raw = res.stdout.strip() if res.stdout else ""
        
        line = ""
        if uuid_raw:
            print(f"   ✅ Pendrive encontrado (UUID: {uuid_raw})")
            line = f"\n# Montagem automatica do Pendrive Daora Kids\nUUID={uuid_raw} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0\n"
        else:
            print("   ⚠️ Pendrive nao detectado, preparando entrada generica /dev/sda1.")
            line = "\n# Montagem automatica do Pendrive Daora Kids\n/dev/sda1 /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0\n"
        
        if line:
            # APPEND SEGURO: Nunca sobrescreve, apenas anexa ao final
            with open("/tmp/fstab_append", "w") as tmp_f:
                tmp_f.write(line)
            run_cmd("cat /tmp/fstab_append | sudo tee -a /etc/fstab", sudo=False)
            print("   📝 Entrada adicionada ao fstab.")
    else:
        print("   ✅ O ponto de montagem /mnt/videos ja esta configurado. Pulando...")
    
    run_cmd("systemctl daemon-reload", sudo=True)
    run_cmd("mount -a", sudo=True)

    # 6.1 Hardware Watchdog
    print("🐕 Ativando Hardware Watchdog...")
    run_cmd("modprobe bcm2835_wdt", sudo=True)
    with open("/etc/modules", "r") as f:
        if "bcm2835_wdt" not in f.read():
            run_cmd('echo "bcm2835_wdt" | sudo tee -a /etc/modules', sudo=False)
    run_cmd("apt-get install -y watchdog", sudo=True)
    run_cmd('echo "watchdog-device = /dev/watchdog" | sudo tee -a /etc/watchdog.conf', sudo=False)
    run_cmd('echo "watchdog-timeout = 15" | sudo tee -a /etc/watchdog.conf', sudo=False)
    run_cmd("systemctl enable --now watchdog", sudo=True)

    # 7. Serviços
    print("⚙️  Configurando servicos do systemd...")
    sync_service = f"""[Unit]
Description=Daora Kids Sync Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=stream
ExecStart=/usr/bin/wget --user={sync_user} --password={sync_pass} -c -N -r -np -nH --cut-dirs={cut_dirs} -A mp4 --tries=10 -P /mnt/videos {sync_url}
Restart=on-failure
RestartSec=30s

[Install]
WantedBy=multi-user.target
"""
    with open("/tmp/daorakids-sync.service", "w") as f:
        f.write(sync_service)
    run_cmd("cp /tmp/daorakids-sync.service /etc/systemd/system/daorakids-sync.service", sudo=True)

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

    # 8. Logs & Monitor
    print("📊 Configurando permissoes de logs e monitoramento...")
    with open("/tmp/daorakids-logs", "w") as f:
        f.write("stream ALL=(ALL) NOPASSWD: /usr/bin/journalctl, /usr/bin/systemctl, /usr/bin/tail\n")
    run_cmd("cp /tmp/daorakids-logs /etc/sudoers.d/daorakids-logs", sudo=True)
    
    bashrc_path = "/home/stream/.bashrc"
    with open(bashrc_path, "r") as f:
        if "ver_live.sh" not in f.read():
            with open(bashrc_path, "a") as f_a:
                f_a.write("\n/home/stream/ver_live.sh\n")

    # 10. Auto-login & Log2Ram
    autologin_dir = "/etc/systemd/system/getty@tty1.service.d"
    run_cmd(f"mkdir -p {autologin_dir}", sudo=True)
    with open("/tmp/autologin.conf", "w") as f:
        f.write("[Service]\nExecStart=\nExecStart=-/sbin/agetty --autologin stream --noclear %I $TERM\n")
    run_cmd(f"cp /tmp/autologin.conf {autologin_dir}/autologin.conf", sudo=True)

    if not is_update:
        choice = input("\n🛡️ Deseja instalar Log2Ram para proteger seu Cartão SD? (S/N): ").strip().lower()
        if choice == 's':
            print("📦 Instalando Log2Ram...")
            run_cmd("curl -L https://github.com/azlux/log2ram/archive/master.tar.gz | tar zx && cd log2ram-master && sudo ./install.sh", sudo=False)

    run_cmd("systemctl daemon-reload", sudo=True)
    run_cmd("systemctl enable daorakids-sync.timer", sudo=True)
    run_cmd("systemctl enable daorakids-live.service", sudo=True)
    
    print("\n✅ Operação concluída!")
    run_cmd("sync", sudo=True)
    run_cmd("umount /mnt/videos", sudo=True)
    print("🔄 Reiniciando em 5s...")
    time.sleep(5)
    run_cmd("reboot", sudo=True)

if __name__ == "__main__":
    setup_wizard()
