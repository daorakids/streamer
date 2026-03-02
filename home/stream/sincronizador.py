#!/usr/bin/env python3
import os
import sys
import requests
import subprocess
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin, urlparse
import re

# --- CONFIGURAÇÃO ---
BASE_DIR = "/home/stream"
load_dotenv(os.path.join(BASE_DIR, ".env"))

VIDEO_ROOT = "/mnt/videos"
SYNC_URL = os.getenv("SYNC_URL", "https://daorakids.com.br/util/stream/").rstrip('/') + '/'
SYNC_USER = os.getenv("SYNC_USER", "stream")
SYNC_PASS = os.getenv("SYNC_PASS", "stream")

def log(msg):
    print(f"🔄 [SYNC] {msg}", flush=True)

def get_remote_files(url, subfolder=""):
    """Busca recursivamente arquivos .mp4 no servidor via directory listing."""
    files = []
    try:
        response = requests.get(url + subfolder, auth=HTTPBasicAuth(SYNC_USER, SYNC_PASS), timeout=20)
        if response.status_code != 200:
            return []
        
        # Regex para encontrar links de arquivos e pastas
        links = re.findall(r'href="([^"]+)"', response.text)
        
        for link in links:
            # Ignora links de sistema e navegação superior
            if link.startswith('?') or link.startswith('/') or '..' in link:
                continue
            
            if link.endswith('/'):
                # É uma pasta, busca dentro dela
                files.extend(get_remote_files(url, subfolder + link))
            elif link.lower().endswith('.mp4'):
                # É um vídeo
                files.append(subfolder + link)
    except Exception as e:
        log(f"⚠️ Erro ao listar servidor ({subfolder}): {e}")
    
    return files

def main():
    log("Iniciando Sincronizacao Inteligente v2.8.32...")
    
    if not os.path.exists(VIDEO_ROOT):
        log(f"🚨 ERRO: Pendrive nao montado em {VIDEO_ROOT}")
        sys.exit(1)

    # 1. Obter lista de arquivos remotos
    log("📡 Mapeando arquivos no servidor...")
    remote_files = get_remote_files(SYNC_URL)
    total_remote = len(remote_files)
    
    if total_remote == 0:
        log("⚠️ Nenhum video encontrado no servidor ou erro de autenticacao.")
        sys.exit(0)

    log(f"✅ Encontrados {total_remote} arquivos no servidor.")

    # 2. Sincronizar (Download)
    for i, rel_path in enumerate(remote_files, 1):
        local_path = os.path.join(VIDEO_ROOT, rel_path)
        local_dir = os.path.dirname(local_path)
        remote_full_url = SYNC_URL + rel_path
        
        # Cria subpastas locais (pt, en, es...)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        filename = os.path.basename(rel_path)
        log(f"📥 [{i}/{total_remote}] Sincronizando: {filename}")
        
        # Usa o wget para o download real (melhor suporte a resume e progresso)
        # -c (resume), -N (apenas se for mais novo), -q (quiet para nao poluir o nosso log customizado)
        cmd = [
            "wget",
            "--user", SYNC_USER,
            "--password", SYNC_PASS,
            "-c", "-N",
            "--no-verbose",
            "--modify-window=2",
            "-O", local_path,
            remote_full_url
        ]
        
        subprocess.run(cmd)

    # 3. Limpeza (Remover arquivos locais que nao existem no servidor)
    log("🧹 Verificando arquivos antigos para limpeza...")
    for root, dirs, files in os.walk(VIDEO_ROOT):
        for f in files:
            if not f.lower().endswith('.mp4'):
                continue
                
            full_local_path = os.path.join(root, f)
            rel_local_path = os.path.relpath(full_local_path, VIDEO_ROOT).replace('', '/')
            
            if rel_local_path not in remote_files:
                log(f"🗑️ Removendo arquivo obsoleto: {rel_local_path}")
                os.remove(full_local_path)

    log("✨ Sincronizacao concluida com sucesso!")

if __name__ == "__main__":
    main()
