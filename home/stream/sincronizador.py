#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import time
from urllib.parse import urlparse

# --- CORES ANSI ---
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[1;31m"
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_CYAN = "\033[1;36m"

# --- LOG DE DIAGNÓSTICO ---
def log(msg):
    prefix = f"{C_CYAN}🔄 [SYNC]{C_RESET}"
    if "❌" in msg or "💥" in msg:
        msg = f"{C_RED}{msg}{C_RESET}"
    elif "⚠️" in msg or "⏳" in msg:
        msg = f"{C_YELLOW}{msg}{C_RESET}"
    elif "✅" in msg or "✨" in msg:
        msg = f"{C_GREEN}{msg}{C_RESET}"
    print(f"{prefix} {msg}", flush=True)

try:
    import requests
    from dotenv import load_dotenv
    from requests.auth import HTTPBasicAuth
except ImportError as e:
    log(f"💥 ERRO CRITICO: Faltam bibliotecas Python: {e}")
    sys.exit(1)

# --- CONFIGURAÇÃO ---
BASE_DIR = "/home/stream"
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

VIDEO_ROOT = "/mnt/videos"
SYNC_URL = os.getenv("SYNC_URL", "https://daorakids.com.br/util/stream/").rstrip('/') + '/'
SYNC_USER = os.getenv("SYNC_USER", "stream")
SYNC_PASS = os.getenv("SYNC_PASS", "stream")

# Extrai o path da URL para validar caminhos absolutos
BASE_PATH = urlparse(SYNC_URL).path.rstrip('/')

def get_remote_files(url, subfolder=""):
    files = []
    current_full_url = url + subfolder
    try:
        log(f"🔗 Listando: {C_BOLD}{current_full_url}{C_RESET}")
        response = requests.get(current_full_url, auth=HTTPBasicAuth(SYNC_USER, SYNC_PASS), timeout=20)
        if response.status_code != 200:
            log(f"⚠️ Servidor respondeu status {response.status_code}")
            return []
        
        links_brutos = re.findall(r'href=["\']?([^"\'> ]+)', response.text, re.I)
        for link in links_brutos:
            if link.startswith('?') or '..' in link: continue
            if link.startswith('/'):
                if link.startswith(BASE_PATH): link = link[len(BASE_PATH):].lstrip('/')
                else: continue
            
            full_rel_path = link if (subfolder and link.startswith(subfolder)) else subfolder + link

            if link.endswith('/'):
                if link.strip('/') == subfolder.strip('/'): continue
                files.extend(get_remote_files(url, full_rel_path))
            elif link.lower().endswith('.mp4'):
                files.append(full_rel_path)
    except Exception as e:
        log(f"⚠️ Erro ao listar: {e}")
    return list(set(files))

def main():
    log(f"{C_BOLD}--- INICIANDO SINCRONIZADOR v3.2 ---{C_RESET}")
    log(f"🌍 Servidor: {SYNC_URL}")
    
    # 1. VERIFICAÇÃO E MONTAGEM
    is_mounted = subprocess.run("mount | grep /mnt/videos", shell=True, capture_output=True).returncode == 0
    if not is_mounted:
        log("⚠️ ALERTA: Pendrive nao detectado. Tentando montar 'DAORAKIDS'...")
        res = subprocess.run("sudo mount -L DAORAKIDS /mnt/videos", shell=True, capture_output=True)
        if res.returncode == 0:
            log("   ✅ SUCESSO: Pendrive montado!")
            is_mounted = True
        else:
            log("   ❌ ERRO: Usando MicroSD (Fallback).")

    if not os.path.exists(VIDEO_ROOT): os.makedirs(VIDEO_ROOT, exist_ok=True)

    log("📡 Mapeando arquivos remotos...")
    remote_files = get_remote_files(SYNC_URL)
    total_remote = len(remote_files)
    
    if total_remote == 0:
        log("⚠️ Nenhum video encontrado.")
        sys.exit(0)

    log(f"✅ Encontrados {C_BOLD}{total_remote}{C_RESET} videos. Sincronizando...")

    for i, rel_path in enumerate(sorted(remote_files), 1):
        clean_rel_path = rel_path.lstrip('/')
        local_path = os.path.join(VIDEO_ROOT, clean_rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        download_url = SYNC_URL + clean_rel_path
        
        filename = os.path.basename(clean_rel_path)
        log(f"📥 [{i}/{total_remote}] {C_BOLD}{clean_rel_path}{C_RESET}")
        
        cmd = ["wget", "--user", SYNC_USER, "--password", SYNC_PASS, "-c", "--no-verbose", "-O", local_path, download_url]
        subprocess.run(cmd)

    log("✨ Sincronizacao finalizada!")

if __name__ == "__main__":
    main()
