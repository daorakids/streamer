#!/usr/bin/env python3
import json
import datetime
import os
import subprocess
import requests
import socket
import hashlib
import time
import sys
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# --- CORES ANSI ---
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[1;31m"
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_BLUE = "\033[1;34m"
C_MAGENTA = "\033[1;35m"
C_CYAN = "\033[1;36m"

# --- CONFIGURAÇÃO DE LOGS ---
def log_debug(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    prefix = f"{C_MAGENTA}📅 [SCHEDULER]{C_RESET}"
    if "❌" in msg or "💥" in msg:
        msg = f"{C_RED}{msg}{C_RESET}"
    elif "⚠️" in msg or "⏳" in msg:
        msg = f"{C_YELLOW}{msg}{C_RESET}"
    elif "✅" in msg or "✨" in msg:
        msg = f"{C_GREEN}{msg}{C_RESET}"
    
    print(f"{prefix} [{timestamp}] {msg}", flush=True)

# --- CARREGAR CONFIGS DO .ENV ---
BASE_DIR = "/home/stream"
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# --- CAMINHOS ---
SCHEDULE_PATH = os.path.join(BASE_DIR, "schedule.json")
CURRENT_STATE_FILE = os.path.join(BASE_DIR, "estado_atual.json")
CONFIG_FILE = os.path.join(BASE_DIR, ".current_config")
VIDEO_ROOT = "/mnt/videos"

# --- CONFIGS CREDENCIAIS ---
SYNC_URL = os.getenv("SYNC_URL", "https://daorakids.com.br/util/stream/").rstrip('/')
SYNC_USER = os.getenv("SYNC_USER", "stream")
SYNC_PASS = os.getenv("SYNC_PASS", "stream")
WEB_SCHEDULE_URL = f"{SYNC_URL}/schedule.json"

def find_video_dir(lang):
    if not os.path.exists(VIDEO_ROOT): return None
    lang_search = lang.lower().strip()
    try:
        items = os.listdir(VIDEO_ROOT)
        for item in items:
            path = os.path.join(VIDEO_ROOT, item)
            if os.path.isdir(path) and item.lower().strip() == lang_search:
                return path
    except: pass
    return None

def check_all_languages_ready():
    required = ["pt", "en", "es"]
    missing = []
    for lang in required:
        if not find_video_dir(lang):
            missing.append(lang.upper())
    return missing

def update_schedule_from_web():
    log_debug(f"🌐 Sincronizando agenda...")
    try:
        response = requests.get(WEB_SCHEDULE_URL, timeout=15, auth=HTTPBasicAuth(SYNC_USER, SYNC_PASS))
        if response.status_code == 200:
            new_content = response.text
            try: json.loads(new_content)
            except: return
            with open(SCHEDULE_PATH, 'w') as f: f.write(new_content)
            log_debug("✅ Agenda atualizada.")
    except Exception as e:
        log_debug(f"⚠️ Falha ao baixar agenda (usando local): {e}")

def get_current_slot():
    try:
        if not os.path.exists(SCHEDULE_PATH): return None
        with open(SCHEDULE_PATH, 'r') as f: data = json.load(f)
    except: return None

    if data.get("emergency_stop"): return {"lang": "STOP"}

    agora = datetime.datetime.now()
    days_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    hoje_dia = days_map[agora.weekday()]
    hora_atual = agora.strftime("%H:%M")

    slot = None
    special = data.get("special_dates", {}).get(agora.strftime("%Y-%m-%d"))
    if special:
        for s in special:
            if s["start"] <= hora_atual <= s["end"]: slot = s; break
    if not slot:
        day_slots = data.get("schedule", {}).get(hoje_dia)
        if day_slots:
            for s in day_slots:
                if s["start"] <= hora_atual <= s["end"]:
                    slot = s; break
    
    if not slot:
        log_debug(f"💤 Fora do horario (Relogio: {hora_atual})")
        return {"lang": "OFF"}
    
    lang_key = slot['lang'].lower()
    web_keys = data.get("stream_keys", {})
    slot["key"] = web_keys.get(lang_key, os.getenv(f"YT_KEY_{lang_key.upper()}"))
    return slot

def main():
    log_debug(f"{C_BOLD}--- INICIANDO SCHEDULER v3.2 ---{C_RESET}")
    update_schedule_from_web()
    
    # CHECK DE HARDWARE
    is_mounted = subprocess.run("mount | grep /mnt/videos", shell=True, capture_output=True).returncode == 0
    if not is_mounted:
        log_debug("⚠️ AVISO: Pendrive nao detectado! Gravando no MicroSD (Fallback).")
    
    # VALIDACAO DE PRONTIDAO
    missing = check_all_languages_ready()
    if missing:
        log_debug(f"⏳ Aguardando sincronismo inicial. Faltam: {', '.join(missing)}")
        with open(CONFIG_FILE + ".error", 'w') as f:
            f.write(f"Aguardando download inicial das pastas: {', '.join(missing)}")
        if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
        return

    slot = get_current_slot()
    if not slot: return

    current_state = {}
    if os.path.exists(CURRENT_STATE_FILE):
        try:
            with open(CURRENT_STATE_FILE, 'r') as f: current_state = json.load(f)
        except: pass

    if slot != current_state or not os.path.exists(CONFIG_FILE):
        log_debug(f"🔄 Ajustando transmissao para {C_BOLD}{slot.get('lang').upper()}{C_RESET}...")
        target_lang = slot.get("lang", "OFF").lower()
        target_mode = slot.get("mode", "sequential")
        target_key = slot.get("key", "")
        
        with open(CURRENT_STATE_FILE, 'w') as f: json.dump(slot, f)

        if target_lang in ["stop", "off"]:
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
        else:
            video_dir = find_video_dir(target_lang)
            if not video_dir:
                with open(CONFIG_FILE + ".error", 'w') as f:
                    f.write(f"Pasta '{target_lang.upper()}' sumiu do pendrive!")
                if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
                return
            
            if os.path.exists(CONFIG_FILE + ".error"): os.remove(CONFIG_FILE + ".error")
            
            try:
                with open(CONFIG_FILE, 'w') as f:
                    f.write(f'CHAVE="{target_key}"\nPASTA_VIDEOS="{video_dir}"\nMODO="{target_mode}"\n')
                log_debug(f"✅ Transmissao liberada!")
                os.chmod(CONFIG_FILE, 0o777)
            except Exception as e:
                log_debug(f"❌ Erro ao gravar config: {e}")
        
        subprocess.run(["pkill", "-f", "ffmpeg"], stderr=subprocess.DEVNULL)
    else:
        log_debug(f"😴 Tudo em ordem. Transmitindo {C_BOLD}{slot.get('lang').upper()}{C_RESET}...")

    # Lembrete de comandos
    print(f"\n{C_CYAN}💡 Comandos:{C_RESET} {C_BOLD}'log'{C_RESET}, {C_BOLD}'daora-stop'{C_RESET}, {C_BOLD}'daora-start'{C_RESET}\n")

if __name__ == "__main__":
    try: main()
    except Exception as e: log_debug(f"💥 ERRO: {e}")
