#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import time

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

def get_remote_files(url, subfolder=""):
    files = []
    full_url = url + subfolder
    try:
        log(f"🔗 Acessando: {full_url}")
        response = requests.get(full_url, auth=HTTPBasicAuth(SYNC_USER, SYNC_PASS), timeout=20)
        
        if response.status_code != 200:
            log(f"⚠️ Servidor respondeu status {response.status_code}")
            return []
        
        # Regex Ultra-Sensivel (ignora case, aceita aspas simples/duplas ou sem aspas)
        links = re.findall(r'href=["\']?([^"\'> ]+)', response.text, re.I)
        
        if not links:
            log(f"📝 HTML RECEBIDO (Snippet): {response.text[:500]}")
            return []

        for link in links:
            # Ignora links de navegacao do servidor
            if link.startswith('?') or link.startswith('/') or '..' in link: continue
            if link.endswith('/'):
                files.extend(get_remote_files(url, subfolder + link))
            elif link.lower().endswith('.mp4'):
                files.append(subfolder + link)
    except Exception as e:
        log(f"⚠️ Erro de conexao: {e}")
    return list(set(files)) # Remove duplicatas

def main():
    log(f"Iniciando Sincronizador v2.8.38")
    log(f"🌍 Servidor: {SYNC_URL} | Usuario: {SYNC_USER}")
    
    if not os.path.exists(VIDEO_ROOT):
        os.makedirs(VIDEO_ROOT, exist_ok=True)

    log("📡 Mapeando arquivos no servidor...")
    remote_files = get_remote_files(SYNC_URL)
    total_remote = len(remote_files)
    
    if total_remote == 0:
        log("⚠️ Nenhum video encontrado. Verifique a listagem de diretorios no servidor.")
        sys.exit(0)

    log(f"✅ Encontrados {total_remote} videos. Sincronizando...")

    for i, rel_path in enumerate(sorted(remote_files), 1):
        local_path = os.path.join(VIDEO_ROOT, rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        filename = os.path.basename(rel_path)
        log(f"📥 [{i}/{total_remote}] {filename}")
        
        cmd = ["wget", "--user", SYNC_USER, "--password", SYNC_PASS, "-c", "-N", "--no-verbose", "--modify-window=2", "-O", local_path, SYNC_URL + rel_path]
        subprocess.run(cmd)

    log("✨ Sincronizacao finalizada!")

if __name__ == "__main__":
    main()
