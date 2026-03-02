#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import time
from urllib.parse import urlparse

# --- LOG DE DIAGNÓSTICO ---
def log(msg):
    print(f"🔄 [SYNC] {msg}", flush=True)

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
BASE_PATH = urlparse(SYNC_URL).path

def get_remote_files(url, subfolder=""):
    files = []
    full_url = url + subfolder
    try:
        log(f"🔗 Acessando: {full_url}")
        response = requests.get(full_url, auth=HTTPBasicAuth(SYNC_USER, SYNC_PASS), timeout=20)
        
        if response.status_code != 200:
            log(f"⚠️ Servidor respondeu status {response.status_code}")
            return []
        
        links_brutos = re.findall(r'href=["\']?([^"\'> ]+)', response.text, re.I)
        
        valid_links = []
        for link in links_brutos:
            if link.startswith('?') or '..' in link: continue
            if link.startswith('/'):
                if link.startswith(BASE_PATH):
                    link = link[len(BASE_PATH):].lstrip('/')
                else: continue
            if not link: continue
            valid_links.append(link)

        if not valid_links:
            return []

        for link in list(set(valid_links)):
            if link.endswith('/'):
                files.extend(get_remote_files(url, subfolder + link))
            elif link.lower().endswith('.mp4'):
                files.append(subfolder + link)
                
    except Exception as e:
        log(f"⚠️ Erro de conexao: {e}")
    return list(set(files))

def main():
    log(f"Iniciando Sincronizador v2.9")
    log(f"🌍 Servidor: {SYNC_URL} | Usuario: {SYNC_USER}")
    
    if not os.path.exists(VIDEO_ROOT):
        os.makedirs(VIDEO_ROOT, exist_ok=True)

    log("📡 Mapeando arquivos no servidor...")
    remote_files = get_remote_files(SYNC_URL)
    total_remote = len(remote_files)
    
    if total_remote == 0:
        log("⚠️ Nenhum video encontrado.")
        sys.exit(0)

    log(f"✅ Encontrados {total_remote} videos. Iniciando...")

    for i, rel_path in enumerate(sorted(remote_files), 1):
        local_path = os.path.join(VIDEO_ROOT, rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        filename = os.path.basename(rel_path)
        log(f"📥 [{i}/{total_remote}] {filename}")
        
        # REMOVIDO --modify-window para compatibilidade
        cmd = ["wget", "--user", SYNC_USER, "--password", SYNC_PASS, "-c", "-N", "--no-verbose", "-O", local_path, SYNC_URL + rel_path]
        subprocess.run(cmd)

    log("✨ Sincronizacao finalizada!")

if __name__ == "__main__":
    main()
