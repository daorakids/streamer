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

# Extrai o path da URL para validar caminhos absolutos (Ex: /util/stream/)
BASE_PATH = urlparse(SYNC_URL).path.rstrip('/')

def get_remote_files(url, subfolder=""):
    """
    url: Base URL (https://.../stream/)
    subfolder: Caminho relativo (en/, es/...)
    """
    files = []
    current_full_url = url + subfolder
    try:
        log(f"🔗 Listando: {current_full_url}")
        response = requests.get(current_full_url, auth=HTTPBasicAuth(SYNC_USER, SYNC_PASS), timeout=20)
        
        if response.status_code != 200:
            log(f"⚠️ Servidor respondeu status {response.status_code}")
            return []
        
        # Captura todos os links href
        links_brutos = re.findall(r'href=["\']?([^"\'> ]+)', response.text, re.I)
        
        for link in links_brutos:
            # 1. Limpeza e Filtros basicos
            if link.startswith('?') or '..' in link: continue
            
            # 2. Normaliza links absolutos (Ex: /util/stream/en/v.mp4 -> en/v.mp4)
            if link.startswith('/'):
                if link.startswith(BASE_PATH):
                    link = link[len(BASE_PATH):].lstrip('/')
                else: continue # Link de fora do projeto
            
            # 3. Limpeza de duplicidade (Ex: se o link ja contiver o subfolder)
            # Se subfolder="en/" e link="en/video.mp4", queremos apenas "en/video.mp4"
            # Se subfolder="en/" e link="video.mp4", queremos "en/video.mp4"
            if subfolder and link.startswith(subfolder):
                full_rel_path = link
            else:
                full_rel_path = subfolder + link

            if link.endswith('/'):
                # Recursão: Evita processar a própria pasta atual
                if link.strip('/') == subfolder.strip('/'): continue
                files.extend(get_remote_files(url, full_rel_path))
            elif link.lower().endswith('.mp4'):
                files.append(full_rel_path)
                
    except Exception as e:
        log(f"⚠️ Erro ao listar: {e}")
    return list(set(files))

def main():
    log(f"Iniciando Sincronizador v2.9.4")
    log(f"🌍 Servidor: {SYNC_URL}")
    
    if not os.path.exists(VIDEO_ROOT):
        os.makedirs(VIDEO_ROOT, exist_ok=True)

    log("📡 Mapeando arquivos remotos...")
    remote_files = get_remote_files(SYNC_URL)
    total_remote = len(remote_files)
    
    if total_remote == 0:
        log("⚠️ Nenhum video encontrado.")
        sys.exit(0)

    log(f"✅ Encontrados {total_remote} videos. Iniciando sincronismo...")

    for i, rel_path in enumerate(sorted(remote_files), 1):
        # Garante path limpo
        clean_rel_path = rel_path.lstrip('/')
        local_path = os.path.join(VIDEO_ROOT, clean_rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # URL de download FINAL (Sempre BASE + RELATIVO)
        download_url = SYNC_URL + clean_rel_path
        
        filename = os.path.basename(clean_rel_path)
        log(f"📥 [{i}/{total_remote}] {clean_rel_path}")
        
        # Wget Robusto: -c (resume), --no-verbose (limpo), -O (saida exata)
        cmd = [
            "wget",
            "--user", SYNC_USER, "--password", SYNC_PASS,
            "-c", "--no-verbose",
            "-O", local_path,
            download_url
        ]
        subprocess.run(cmd)

    log("✨ Sincronizacao finalizada!")

if __name__ == "__main__":
    main()
