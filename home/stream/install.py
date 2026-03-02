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
    print(" 🎨 INSTALADOR/UPDATER DAORA KIDS v2.8.15 ")
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

    # 6. Pendrive (Super Detecção v2.8.5)
    print("💾 Configurando montagem do Pendrive...")
    run_cmd("mkdir -p /mnt/videos", sudo=True)
    
    try:
        # 1. Limpeza: Remove qualquer linha antiga do /mnt/videos para evitar conflitos
        run_cmd("grep -v '/mnt/videos' /etc/fstab > /tmp/fstab.clean", sudo=True)
        run_cmd("cp /tmp/fstab.clean /etc/fstab", sudo=True)

        # 2. Busca Automática do Dispositivo
        device = ""
        for dev in ['sda1', 'sdb1', 'sdc1']:
            if os.path.exists(f"/dev/{dev}"):
                device = f"/dev/{dev}"
                break
        
        if device:
            print(f"   🔍 Dispositivo detectado: {device}")
            res = run_cmd(f"blkid -s UUID -o value {device}", sudo=True, capture=True)
            uuid = res.stdout.strip() if res.stdout else ""
            
            if uuid:
                print(f"   ✅ UUID encontrado: {uuid}")
                line = f"UUID={uuid} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0"
            else:
                print(f"   ⚠️ UUID nao encontrado para {device}, usando caminho direto.")
                line = f"{device} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0"
            
            # Adiciona ao fstab
            run_cmd(f'echo "{line}" | sudo tee -a /etc/fstab', sudo=False)
            print("   📝 Configuraçao adicionada ao /etc/fstab")

            # 3. Forçar Montagem
            run_cmd("systemctl daemon-reload", sudo=True)
            print("   🚀 Tentando montar...")
            run_cmd("mount /mnt/videos", sudo=True)
        else:
            print("   ❌ AVISO: Nenhum pendrive detectado! A live podera falhar.")
    except Exception as e:
        print(f"   ⚠️ Erro durante configuracao do pendrive: {e}")

    if os.path.ismount("/mnt/videos"):
        print("   ✨ SUCESSO! Pendrive montado em /mnt/videos")
    else:
        print("   ⚠️ Pendrive nao montado.")

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
    
    # 7.1 Cérebro (Agenda) - Roda a cada 5 minutos
    cerebro_service = f"""[Unit]
Description=Daora Kids Cerebro Service
After=network-online.target

[Service]
Type=oneshot
User=stream
WorkingDirectory={BASE_DIR}
ExecStart=/usr/bin/python3 {BASE_DIR}/cerebro.py
"""
    cerebro_timer = """[Unit]
Description=Daora Kids Cerebro Timer

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
Unit=daorakids-cerebro.service

[Install]
WantedBy=timers.target
"""
    with open("/tmp/daorakids-cerebro.service", "w") as f: f.write(cerebro_service)
    with open("/tmp/daorakids-cerebro.timer", "w") as f: f.write(cerebro_timer)
    run_cmd("cp /tmp/daorakids-cerebro.* /etc/systemd/system/", sudo=True)

    # 7.2 Sincronizador de Vídeos
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
    # ... rest of services ...
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
    bashrc_addon = """
# --- DAORA KIDS AUTO-MONITOR ---
alias ver='/home/stream/ver_live.sh'
alias log='sudo journalctl -u daorakids-live.service -u daorakids-cerebro.service -u daorakids-sync.service -f'
alias monitor='/home/stream/ver_live.sh'

# Inicia o monitor automaticamente apenas no terminal físico (HDMI)
if [ "$(tty)" = "/dev/tty1" ]; then
    /home/stream/ver_live.sh
fi
"""
    with open(bashrc_path, "r") as f:
        if "DAORA KIDS AUTO-MONITOR" not in f.read():
            with open(bashrc_path, "a") as f_a:
                f_a.write(bashrc_addon)

    # 10. Auto-login (Forca Bruta v2.8.15) & Log2Ram
    print("🖥️  Configurando Auto-login REAL no console (HDMI)...")
    # 1. Desativa cloud-init para parar de sujar a tela
    run_cmd("systemctl disable cloud-init.service cloud-init-local.service cloud-config.service cloud-final.service", sudo=True)
    run_cmd("touch /etc/cloud/cloud-init.disabled", sudo=True)

    # 2. Cria o override manual do Getty (TTY1) ignorando raspi-config
    autologin_dir = "/etc/systemd/system/getty@tty1.service.d"
    run_cmd(f"mkdir -p {autologin_dir}", sudo=True)
    with open("/tmp/autologin.conf", "w") as f:
        f.write("[Service]\nExecStart=\nExecStart=-/sbin/agetty --autologin stream --noclear %I $TERM\n")
    run_cmd(f"cp /tmp/autologin.conf {autologin_dir}/autologin.conf", sudo=True)

    # 11. Silenciador de Boot (Limpeza do HDMI)
    print("🔇 Silenciando mensagens de boot no HDMI...")
    cmdline = "/boot/firmware/cmdline.txt"
    if not os.path.exists(cmdline): cmdline = "/boot/cmdline.txt"
    if os.path.exists(cmdline):
        with open(cmdline, "r") as f:
            content = f.read().strip()
        if "quiet" not in content:
            # Limpa console=tty1 e adiciona quiet loglevel=3
            new_params = "quiet loglevel=3 logo.nologo vt.global_cursor_default=0"
            content = content.replace("console=tty1", "console=tty3")
            with open("/tmp/cmdline.txt", "w") as f: f.write(content + " " + new_params + "\n")
            run_cmd(f"cp /tmp/cmdline.txt {cmdline}", sudo=True)

    # 12. Ajuste no Dashboard (Atraso para estabilidade)
    bashrc_path = "/home/stream/.bashrc"
    bashrc_addon = """
# --- DAORA KIDS AUTO-MONITOR v2.8.15 ---
alias ver='/home/stream/ver_live.sh'
alias log='sudo journalctl -u daorakids-live.service -u daorakids-cerebro.service -u daorakids-sync.service -f'
alias monitor='/home/stream/ver_live.sh'

# Inicia o monitor automaticamente apenas no terminal físico (HDMI)
if [ "$(tty)" = "/dev/tty1" ]; then
    sleep 2 # Espera o sistema "assentar"
    clear
    /home/stream/ver_live.sh
fi
"""
    # Remove addon antigo se existir
    run_cmd(f"sed -i '/DAORA KIDS AUTO-MONITOR/,/fi/d' {bashrc_path}", sudo=True)
    with open(bashrc_path, "a") as f_a:
        f_a.write(bashrc_addon)

    if not is_update:
        choice = input("\n🛡️ Deseja instalar Log2Ram para proteger seu Cartão SD? (S/N): ").strip().lower()
        if choice == 's':
            print("📦 Instalando Log2Ram...")
            run_cmd("curl -L https://github.com/azlux/log2ram/archive/master.tar.gz | tar zx && cd log2ram-master && sudo ./install.sh", sudo=False)

    run_cmd("systemctl daemon-reload", sudo=True)
    run_cmd("systemctl enable daorakids-cerebro.timer", sudo=True)
    run_cmd("systemctl start daorakids-cerebro.timer", sudo=True)
    run_cmd("systemctl enable daorakids-sync.timer", sudo=True)
    run_cmd("systemctl enable daorakids-live.service", sudo=True)

    # Roda o Cérebro uma vez agora para já criar o .current_config
    print("🧠 Inicializando configuracoes do Cerebro...")
    run_cmd(f"sudo -u stream /usr/bin/python3 {BASE_DIR}/cerebro.py")
    
    print("\n✅ Operação concluída!")
    run_cmd("sync", sudo=True)
    if os.path.ismount("/mnt/videos"):
        run_cmd("umount /mnt/videos", sudo=True)
    print("🔄 Reiniciando em 5s...")
    time.sleep(5)
    run_cmd("reboot", sudo=True)

if __name__ == "__main__":
    setup_wizard()
