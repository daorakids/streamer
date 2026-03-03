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

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    log(f"⚠️ Alerta: Arquivo {ENV_PATH} nao encontrado!")

VIDEO_ROOT = "/mnt/videos"
SYNC_URL = os.getenv("SYNC_URL", "https://daorakids.com.br/util/stream/").rstrip('/') + '/'
SYNC_USER = os.getenv("SYNC_USER")
SYNC_PASS = os.getenv("SYNC_PASS")

if not SYNC_USER or not SYNC_PASS:
    log("❌ ERRO: Credenciais SYNC_USER ou SYNC_PASS nao encontradas no .env!")
    sys.exit(1)

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
    log(f"{C_BOLD}--- INICIANDO SINCRONIZADOR v3.3.1 ---{C_RESET}")

    
    if not os.path.exists(VIDEO_ROOT):
        try: os.makedirs(VIDEO_ROOT, exist_ok=True)
        except Exception as e:
            log(f"💥 Falha ao criar pasta {VIDEO_ROOT}: {e}")
            sys.exit(1)

    log("📡 Mapeando arquivos remotos...")
    remote_files = get_remote_files(SYNC_URL)
    total_remote = len(remote_files)
    
    if total_remote == 0:
        log("⚠️ Nenhum video encontrado no servidor.")
        sys.exit(0)

    log(f"✅ Encontrados {C_BOLD}{total_remote}{C_RESET} videos. Sincronizando...")

    for i, rel_path in enumerate(sorted(remote_files), 1):
        clean_rel_path = rel_path.lstrip('/')
        local_path = os.path.join(VIDEO_ROOT, clean_rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        download_url = SYNC_URL + clean_rel_path
        
        try:
            if os.path.exists(local_path):
                head = requests.head(download_url, auth=HTTPBasicAuth(SYNC_USER, SYNC_PASS), timeout=10)
                remote_size = int(head.headers.get('Content-Length', 0))
                local_size = os.path.getsize(local_path)
                if remote_size > 0 and remote_size == local_size:
                    log(f"⏩ [{i}/{total_remote}] {C_BOLD}{clean_rel_path}{C_RESET} (Ja atualizado)")
                    continue
        except: pass

        log(f"📥 [{i}/{total_remote}] {C_BOLD}{clean_rel_path}{C_RESET}")
        cmd = ["wget", "--user", SYNC_USER, "--password", SYNC_PASS, "-c", "--no-verbose", "-O", local_path, download_url]
        res = subprocess.run(cmd)
        if res.returncode != 0:
            log(f"❌ Erro ao baixar {clean_rel_path} (Wget exit: {res.returncode})")

    log("✨ Sincronizacao finalizada!")

if __name__ == "__main__":
    try: main()
    except Exception as e:
        log(f"💥 ERRO FATAL: {e}")
        sys.exit(1)
