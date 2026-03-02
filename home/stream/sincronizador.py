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
            
            # Trata links absolutos (Ex: /util/stream/en/)
            if link.startswith('/'):
                if link.startswith(BASE_PATH):
                    # Transforma em relativo ao SYNC_URL
                    link = link[len(BASE_PATH):].lstrip('/')
                else: continue
            
            if not link: continue
            valid_links.append(link)

        for link in list(set(valid_links)):
            if link.endswith('/'):
                # Na recursão, não passamos subfolder se o link já for o caminho completo
                # Mas para manter a estrutura, limpamos o link e enviamos
                clean_link = link.strip('/') + '/'
                # Evita duplicar se o link já contiver o subfolder atual
                if subfolder and clean_link.startswith(subfolder):
                    files.extend(get_remote_files(url, clean_link))
                else:
                    files.extend(get_remote_files(url, subfolder + clean_link))
            elif link.lower().endswith('.mp4'):
                # Garante que o arquivo final seja relativo à raiz do sync
                if subfolder and link.startswith(subfolder):
                    files.append(link)
                else:
                    files.append(subfolder + link)
                
    except Exception as e:
        log(f"⚠️ Erro de conexao: {e}")
    return list(set(files))

def main():
    log(f"Iniciando Sincronizador v2.9.1")
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
        # Limpeza final do path para evitar // ou en/en/
        clean_rel_path = rel_path.replace('//', '/').lstrip('/')
        local_path = os.path.join(VIDEO_ROOT, clean_rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        filename = os.path.basename(clean_rel_path)
        log(f"📥 [{i}/{total_remote}] {filename}")
        
        # Wget sem -N para evitar conflito com -O, mas com -c para resume
        cmd = ["wget", "--user", SYNC_USER, "--password", SYNC_PASS, "-c", "--no-verbose", "-O", local_path, SYNC_URL + clean_rel_path]
        subprocess.run(cmd)

    log("✨ Sincronizacao finalizada!")

if __name__ == "__main__":
    main()
