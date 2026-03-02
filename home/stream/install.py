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
    print(" 🎨 INSTALADOR/UPDATER DAORA KIDS v2.8.17 ")
    print("="*40 + "\n")

    BASE_DIR = "/home/stream"
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    # Parar serviços antes de mexer
    print("⏹ Parando serviços para manutenção...")
    run_cmd("systemctl stop daorakids-live.service daorakids-sync.service daorakids-sync.timer daorakids-cerebro.timer", sudo=True)
    run_cmd("pkill -f ffmpeg", sudo=True)

    # 1. DNS & Dependências
    print("🌐 Configurando DNS e limpando pacotes desnecessarios...")
    run_cmd("echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf", sudo=False)
    
    # 2. OPÇÃO NUCLEAR: Purgar cloud-init e mods que sujam o HDMI
    print("🧹 Removendo cloud-init e rpi-cloud-init-mods (Expurgo)...")
    run_cmd("DEBIAN_FRONTEND=noninteractive apt-get purge -y cloud-init rpi-cloud-init-mods", sudo=True)
    run_cmd("rm -rf /etc/cloud /var/lib/cloud", sudo=True)

    # 3. Pendrive (Super Detecção)
    print("💾 Configurando montagem do Pendrive...")
    run_cmd("mkdir -p /mnt/videos", sudo=True)
    run_cmd("chmod 777 /mnt/videos", sudo=True)
    
    # Busca Automática do Dispositivo
    device = ""
    for dev in ['sda1', 'sdb1', 'sdc1']:
        if os.path.exists(f"/dev/{dev}"):
            device = f"/dev/{dev}"
            break
    
    if device:
        # Limpeza e montagem segura
        run_cmd("grep -v '/mnt/videos' /etc/fstab > /tmp/fstab.clean", sudo=True)
        run_cmd("cp /tmp/fstab.clean /etc/fstab", sudo=True)
        res = run_cmd(f"blkid -s UUID -o value {device}", sudo=True, capture=True)
        uuid = res.stdout.strip() if res.stdout else ""
        line = f"UUID={uuid} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0" if uuid else f"{device} /mnt/videos auto nosuid,nodev,nofail,x-gvfs-show,umask=000,flush,noatime 0 0"
        run_cmd(f'echo "{line}" | sudo tee -a /etc/fstab', sudo=False)
        run_cmd("mount -a", sudo=True)

    # 4. Auto-login (Método Oficial + Cirurgia)
    print("🖥️  Configurando Auto-login REAL no console (HDMI)...")
    # Ativa o modo oficial (que cria a pasta e o arquivo corretamente)
    run_cmd("raspi-config nonint do_boot_behaviour B2", sudo=True)
    # Troca o usuário padrão 'pi' pelo 'stream' no arquivo oficial
    autologin_conf = "/etc/systemd/system/getty@tty1.service.d/autologin.conf"
    run_cmd(f"sed -i 's/pi/stream/g' {autologin_conf}", sudo=True)
    run_cmd(f"sed -i 's/agetty/agetty --noclear/g' {autologin_conf}", sudo=True)

    # 5. Reconstruir Cmdline (Limpeza Profunda do HDMI)
    print("🔇 Reconstruindo cmdline.txt para boot limpo...")
    cmdline_path = "/boot/firmware/cmdline.txt"
    if not os.path.exists(cmdline_path): cmdline_path = "/boot/cmdline.txt"
    
    if os.path.exists(cmdline_path):
        run_cmd(f"mount -o remount,rw $(dirname {cmdline_path})", sudo=True)
        with open(cmdline_path, "r") as f:
            orig = f.read().strip()
        parts = orig.split()
        clean_parts = [p for p in parts if not any(x in p for x in ["console=", "quiet", "loglevel", "logo.nologo", "enable_hdmi", "vt.global_cursor"])]
        new_line = " ".join(clean_parts) + " console=tty3 quiet loglevel=3 logo.nologo vt.global_cursor_default=0 snd_bcm2835.enable_hdmi=1"
        with open("/tmp/cmdline.txt", "w") as f: f.write(new_line + "\n")
        run_cmd(f"cp /tmp/cmdline.txt {cmdline_path}", sudo=True)

    # 6. Serviços Systemd
    print("⚙️  Configurando servicos e timers...")
    run_cmd("systemctl daemon-reload", sudo=True)
    for srv in ["daorakids-cerebro.timer", "daorakids-sync.timer", "daorakids-live.service"]:
        run_cmd(f"systemctl enable {srv}", sudo=True)
        run_cmd(f"systemctl start {srv}", sudo=True)

    # 7. Dashboard HDMI no .bashrc
    bashrc_path = "/home/stream/.bashrc"
    bashrc_addon = """
# --- DAORA KIDS DASHBOARD v2.8.17 ---
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

    print("\n✅ Setup v2.8.17 concluído! Reiniciando em 5s...")
    run_cmd("sync", sudo=True)
    time.sleep(5)
    run_cmd("reboot", sudo=True)

if __name__ == "__main__":
    setup_wizard()
