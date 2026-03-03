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

# --- CONFIGURAÇÃO DE LOGS ---
def log_debug(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🧠 [CEREBRO DEBUG] [{timestamp}] {msg}", flush=True)

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
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYNC_URL = os.getenv("SYNC_URL", "https://daorakids.com.br/util/stream/").rstrip('/')
SYNC_USER = os.getenv("SYNC_USER", "stream")
SYNC_PASS = os.getenv("SYNC_PASS", "stream")
WEB_SCHEDULE_URL = f"{SYNC_URL}/schedule.json"

def find_video_dir(lang):
    if not os.path.exists(VIDEO_ROOT):
        return None
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
    log_debug(f"🌐 Sincronizando agenda com o servidor...")
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
    # 1. Datas especiais
    special = data.get("special_dates", {}).get(agora.strftime("%Y-%m-%d"))
    if special:
        for s in special:
            if s["start"] <= hora_atual <= s["end"]: slot = s; break
    # 2. Agenda semanal
    if not slot:
        day_slots = data.get("schedule", {}).get(hoje_dia)
        if day_slots:
            for s in day_slots:
                if s["start"] <= hora_atual <= s["end"]: slot = s; break
    
    if not slot:
        log_debug(f"💤 Fora do horario (Relogio: {hora_atual})")
        return {"lang": "OFF"}
    
    lang_key = slot['lang'].lower()
    web_keys = data.get("stream_keys", {})
    slot["key"] = web_keys.get(lang_key, os.getenv(f"YT_KEY_{lang_key.upper()}"))
    return slot

def main():
    log_debug("--- INICIANDO CEREBRO v2.9.7 ---")
    update_schedule_from_web()
    
    # CHECK DE HARDWARE (Aviso de Pendrive Missing)
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
        log_debug(f"🔄 Ajustando transmissao para {slot.get('lang').upper()}...")
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
        log_debug("😴 Tudo em ordem. Transmitindo...")

    # Lembrete de comandos (Dica do Usuário)
    print("\n💡 Use os comandos: 'log' para monitorar, 'daora-stop' para parar e 'daora-start' para iniciar o sistema.\n")

if __name__ == "__main__":
    try: main()
    except Exception as e: log_debug(f"💥 ERRO: {e}")
