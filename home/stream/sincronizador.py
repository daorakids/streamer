#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import time

# --- LOG DE DIAGNÓSTICO INICIAL ---
def log(msg):
    print(f"🔄 [SYNC] {msg}", flush=True)

try:
    import requests
    from dotenv import load_dotenv
    from requests.auth import HTTPBasicAuth
except ImportError as e:
    log(f"💥 ERRO CRITICO: Faltam bibliotecas Python: {e}")
    log("Tente rodar: sudo apt-get install python3-requests python3-dotenv")
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
        
        if response.status_code == 401:
            log(f"❌ ERRO 401: Usuario '{SYNC_USER}' ou senha invalidos!")
            return []
        if response.status_code != 200:
            log(f"⚠️ Servidor respondeu com status {response.status_code}")
            return []
        
        # Procura por links .mp4 ou pastas (terminadas em /)
        links = re.findall(r'href="([^"]+)"', response.text)
        
        if not links:
            log(f"⚠️ Alerta: Nenhum link encontrado na pagina HTML de {subfolder or 'root'}")
            log(f"📝 Conteudo inicial da resposta: {response.text[:200]}...")
            return []

        for link in links:
            if link.startswith('?') or link.startswith('/') or '..' in link: continue
            if link.endswith('/'):
                files.extend(get_remote_files(url, subfolder + link))
            elif link.lower().endswith('.mp4'):
                files.append(subfolder + link)
    except Exception as e:
        log(f"⚠️ Erro de conexao em {full_url}: {e}")
    return files

def main():
    log(f"Iniciando Sincronizador v2.8.36")
    log(f"👤 Usuario: {SYNC_USER} | 🌍 Servidor: {SYNC_URL}")
    
    if not os.path.exists(VIDEO_ROOT):
        log(f"🚨 PASTA RAIZ NAO ENCONTRADA: {VIDEO_ROOT}")
        # Tenta criar a pasta caso ela tenha sido deletada
        try:
            os.makedirs(VIDEO_ROOT, exist_ok=True)
            log(f"✅ Pasta {VIDEO_ROOT} recriada.")
        except Exception as e:
            log(f"💥 Falha ao recriar pasta: {e}")
            sys.exit(1)

    log("📡 Mapeando arquivos no servidor...")
    remote_files = get_remote_files(SYNC_URL)
    total_remote = len(remote_files)
    
    if total_remote == 0:
        log("⚠️ Nenhum video encontrado. Verifique a URL ou as credenciais.")
        sys.exit(0)

    log(f"✅ Encontrados {total_remote} videos. Iniciando sincronismo...")

    for i, rel_path in enumerate(remote_files, 1):
        local_path = os.path.join(VIDEO_ROOT, rel_path)
        local_dir = os.path.dirname(local_path)
        remote_full_url = SYNC_URL + rel_path
        
        os.makedirs(local_dir, exist_ok=True)
        filename = os.path.basename(rel_path)
        log(f"📥 [{i}/{total_remote}] Sincronizando: {filename}")
        
        cmd = [
            "wget", "--user", SYNC_USER, "--password", SYNC_PASS,
            "-c", "-N", "--no-verbose", "--modify-window=2",
            "-O", local_path, remote_full_url
        ]
        subprocess.run(cmd)

    log("🧹 Verificando limpeza de arquivos obsoletos...")
    for root, dirs, files in os.walk(VIDEO_ROOT):
        for f in files:
            if not f.lower().endswith('.mp4'): continue
            full_local_path = os.path.join(root, f)
            rel_local_path = os.path.relpath(full_local_path, VIDEO_ROOT).replace('\\', '/')
            if rel_local_path not in remote_files:
                log(f"🗑️ Removendo: {rel_local_path}")
                os.remove(full_local_path)

    log("✨ Sincronizacao finalizada!")

if __name__ == "__main__":
    main()
