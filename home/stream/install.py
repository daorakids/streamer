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

def setup_wizard():
    print("\n" + "="*40)
    print(" 🎨 INSTALADOR/UPDATER DAORA KIDS v2.9.5 ")
    print("="*40 + "\n")

    BASE_DIR = "/home/stream"
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    # Pegar dados do .env
    sync_url = os.getenv("SYNC_URL") or "https://daorakids.com.br/util/stream/"
    sync_user = os.getenv("SYNC_USER") or "stream"
    sync_pass = os.getenv("SYNC_PASS") or "stream"
    
    parsed_url = urlparse(sync_url)
    path_parts = [p for p in parsed_url.path.split('/') if p]
    cut_dirs = len(path_parts)

    # Parar serviços
    print("⏹ Parando servicos...")
    run_cmd("systemctl stop daorakids-live.service daorakids-sync.service daorakids-sync.timer daorakids-cerebro.timer", sudo=True)
    run_cmd("pkill -f ffmpeg", sudo=True)

    # 1. DNS
    run_cmd("echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf", sudo=False)
    
    # 2. EXPURGO HDMI (Opcao Nuclear)
    print("🧹 Expurgando cloud-init e mods...")
    run_cmd("killall apt apt-get dpkg", sudo=True)
    run_cmd("rm -f /var/lib/dpkg/lock*", sudo=True)
    run_cmd("DEBIAN_FRONTEND=noninteractive apt-get purge -y --allow-remove-essential cloud-init rpi-cloud-init-mods", sudo=True)
    run_cmd("rm -rf /etc/cloud /var/lib/cloud", sudo=True)

    # 3. Pendrive
    print("💾 Configurando Pendrive...")
    run_cmd("mkdir -p /mnt/videos", sudo=True)
    run_cmd("chmod 777 /mnt/videos", sudo=True)
    device = ""
    for dev in ['sda1', 'sdb1', 'sdc1']:
        if os.path.exists(f"/dev/{dev}"):
            device = f"/dev/{dev}"
            break
    if device:
        run_cmd("grep -v '/mnt/videos' /etc/fstab > /tmp/fstab.clean", sudo=True)
        run_cmd("cp /tmp/fstab.clean /etc/fstab", sudo=True)
        res = run_cmd(f"blkid -s UUID -o value {device}", sudo=True, capture=True)
        uuid = res.stdout.strip() if res.stdout else ""
        line = f"UUID={uuid} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0" if uuid else f"{device} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0"
        run_cmd(f'echo "{line}" | sudo tee -a /etc/fstab', sudo=False)
        run_cmd("mount -a", sudo=True)

    # 4. AUTO-LOGIN FORCADO
    print("🖥️  Forcando Auto-login no console (HDMI)...")
    run_cmd("mkdir -p /etc/systemd/system/getty@tty1.service.d", sudo=True)
    conf_content = "[Service]\nExecStart=\nExecStart=-/sbin/agetty --autologin stream --noclear %I $TERM\n"
    with open("/tmp/autologin.conf", "w") as f: f.write(conf_content)
    run_cmd("cp /tmp/autologin.conf /etc/systemd/system/getty@tty1.service.d/autologin.conf", sudo=True)

    # 5. REBUILD CMDLINE
    print("🔇 Reconstruindo boot silencioso...")
    cmdline_path = "/boot/firmware/cmdline.txt"
    if not os.path.exists(cmdline_path): cmdline_path = "/boot/cmdline.txt"
    if os.path.exists(cmdline_path):
        run_cmd(f"mount -o remount,rw $(dirname {cmdline_path})", sudo=True)
        with open(cmdline_path, "r") as f: orig = f.read().strip()
        parts = orig.split()
        clean_parts = [p for p in parts if not any(x in p for x in ["console=", "quiet", "loglevel", "logo.nologo", "enable_hdmi", "vt.global_cursor"])]
        new_line = " ".join(clean_parts) + " console=tty3 quiet loglevel=3 logo.nologo vt.global_cursor_default=0 snd_bcm2835.enable_hdmi=1"
        with open("/tmp/cmdline.txt", "w") as f: f.write(new_line + "\n")
        run_cmd(f"cp /tmp/cmdline.txt {cmdline_path}", sudo=True)

    # 6. Servicos Systemd (Otimizados v2.8.25)
    print("⚙️  Configurando servicos do systemd...")
    
    sync_service = f"""[Unit]
Description=Daora Kids Sync Service
After=network-online.target mnt-videos.mount
Wants=network-online.target

[Service]
Type=simple
User=stream
ExecStart=/usr/bin/wget --user={sync_user} --password={sync_pass} -c -N -r -np -nH --cut-dirs={cut_dirs} -A mp4 --tries=10 --no-verbose --no-if-modified-since --modify-window=2 -P /mnt/videos {sync_url}
Restart=on-failure
RestartSec=60s

[Install]
WantedBy=multi-user.target
"""
    with open("/tmp/daorakids-sync.service", "w") as f: f.write(sync_service)
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
    with open("/tmp/daorakids-live.service", "w") as f: f.write(live_service)
    run_cmd("cp /tmp/daorakids-live.service /etc/systemd/system/daorakids-live.service", sudo=True)

    # 7. Dashboard .bashrc
    bashrc_path = "/home/stream/.bashrc"
    bashrc_addon = """
# --- DAORA KIDS DASHBOARD v2.9.5 ---
alias ver='/home/stream/ver_live.sh'
alias log='sudo journalctl -u daorakids-live.service -u daorakids-cerebro.service -u daorakids-sync.service -f'
alias monitor='/home/stream/ver_live.sh'
if [ "$(tty)" = "/dev/tty1" ]; then
    sleep 3
    clear
    /home/stream/ver_live.sh
fi
"""
    run_cmd(f"sed -i '/DAORA KIDS/,/fi/d' {bashrc_path}", sudo=True)
    with open(bashrc_path, "a") as f_a: f_a.write(bashrc_addon)

    print("⚙️  Ativando servicos...")
    run_cmd("systemctl daemon-reload", sudo=True)
    for srv in ["daorakids-cerebro.timer", "daorakids-sync.timer", "daorakids-live.service"]:
        run_cmd(f"systemctl enable {srv}", sudo=True)
        run_cmd(f"systemctl start {srv}", sudo=True)

    # Roda o Cérebro uma vez
    print("🧠 Inicializando Cerebro...")
    run_cmd(f"sudo -u stream /usr/bin/python3 {BASE_DIR}/cerebro.py")
    
    print("\n✅ Setup v2.9.5 concluído! Reiniciando em 5s...")
    run_cmd("sync", sudo=True)
    time.sleep(5)
    run_cmd("reboot", sudo=True)

if __name__ == "__main__":
    setup_wizard()
