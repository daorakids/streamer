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
        log_debug(f"🚨 PASTA RAIZ NAO EXISTE: {VIDEO_ROOT}")
        return None
    lang_search = lang.lower().strip()
    log_debug(f"📂 Procurando pasta para o idioma: '{lang_search}'...")
    try:
        items = os.listdir(VIDEO_ROOT)
        for item in items:
            path = os.path.join(VIDEO_ROOT, item)
            if os.path.isdir(path) and item.lower().strip() == lang_search:
                log_debug(f"   ✅ Pasta encontrada: '{item}'")
                return path
    except Exception as e:
        log_debug(f"❌ Erro ao listar {VIDEO_ROOT}: {e}")
    return None

def update_schedule_from_web():
    log_debug(f"🌐 Tentando baixar agenda de: {WEB_SCHEDULE_URL}")
    try:
        # Usa Autenticação Básica com os dados do .env
        response = requests.get(WEB_SCHEDULE_URL, timeout=15, auth=HTTPBasicAuth(SYNC_USER, SYNC_PASS))
        log_debug(f"📡 Resposta do servidor: {response.status_code}")
        if response.status_code == 200:
            new_content = response.text
            try:
                json.loads(new_content) # Valida se é JSON
            except ValueError:
                log_debug("❌ Erro: O conteudo baixado nao e um JSON valido!")
                return
            if os.path.exists(SCHEDULE_PATH):
                with open(SCHEDULE_PATH, 'r') as f:
                    old_content = f.read()
                if hashlib.md5(new_content.encode()).hexdigest() == hashlib.md5(old_content.encode()).hexdigest():
                    log_debug("✅ Agenda ja esta atualizada.")
                    return 
            with open(SCHEDULE_PATH, 'w') as f:
                f.write(new_content)
            log_debug("✨ Nova agenda salva!")
        else:
            log_debug(f"⚠️ Erro {response.status_code} ao buscar agenda. Verifique usuario/senha.")
    except Exception as e:
        log_debug(f"❌ Falha de rede ao buscar agenda: {e}")

def get_current_slot():
    log_debug("📅 Analisando agenda local...")
    try:
        if not os.path.exists(SCHEDULE_PATH):
            log_debug(f"⚠️ {SCHEDULE_PATH} nao existe!")
            return None
        with open(SCHEDULE_PATH, 'r') as f:
            data = json.load(f)
    except Exception as e:
        log_debug(f"❌ Erro ao ler JSON: {e}")
        return None

    if data.get("emergency_stop"):
        log_debug("🛑 EMERGENCY STOP detectado!")
        return {"lang": "STOP"}

    agora = datetime.datetime.now()
    hoje_iso = agora.strftime("%Y-%m-%d")
    days_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    hoje_dia = days_map[agora.weekday()]
    hora_atual = agora.strftime("%H:%M")
    log_debug(f"⏰ Horario do Sistema: {hoje_dia} {hora_atual}")

    slot = None
    # 1. Datas especiais
    special = data.get("special_dates", {}).get(hoje_iso)
    if special:
        for s in special:
            if s["start"] <= hora_atual <= s["end"]:
                slot = s; break
    # 2. Agenda semanal
    if not slot:
        day_slots = data.get("schedule", {}).get(hoje_dia)
        if day_slots:
            for s in day_slots:
                if s["start"] <= hora_atual <= s["end"]:
                    slot = s; break
    if not slot:
        log_debug("💤 Fora do horario programado.")
        return {"lang": "OFF"}
    
    lang_key = slot['lang'].lower()
    web_keys = data.get("stream_keys", {})
    if lang_key in web_keys:
        slot["key"] = web_keys[lang_key]
    else:
        slot["key"] = os.getenv(f"YT_KEY_{lang_key.upper()}")
    return slot

def main():
    log_debug("--- INICIANDO CEREBRO v2.8.23 ---")
    update_schedule_from_web()
    slot = get_current_slot()
    if not slot: return

    current_state = {}
    if os.path.exists(CURRENT_STATE_FILE):
        try:
            with open(CURRENT_STATE_FILE, 'r') as f:
                current_state = json.load(f)
        except: pass

    config_missing = not os.path.exists(CONFIG_FILE)
    if slot != current_state or config_missing:
        log_debug(f"🔄 Mudanca de estado (config faltando={config_missing})")
        target_lang = slot.get("lang", "OFF").lower()
        target_mode = slot.get("mode", "sequential")
        target_key = slot.get("key", "")
        with open(CURRENT_STATE_FILE, 'w') as f:
            json.dump(slot, f)

        if target_lang in ["stop", "off"]:
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            log_debug("🛑 Modo OFF.")
        else:
            video_dir = find_video_dir(target_lang)
            if not video_dir:
                log_debug(f"❌ Pasta '{target_lang}' nao encontrada em {VIDEO_ROOT}!")
                if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
                return
            try:
                with open(CONFIG_FILE, 'w') as f:
                    f.write(f'CHAVE="{target_key}"\n')
                    f.write(f'PASTA_VIDEOS="{video_dir}"\n')
                    f.write(f'MODO="{target_mode}"\n')
                log_debug(f"✅ Config gravada!")
                os.chmod(CONFIG_FILE, 0o777)
            except Exception as e:
                log_debug(f"❌ Erro ao gravar config: {e}")
        subprocess.run(["pkill", "-f", "ffmpeg"], stderr=subprocess.DEVNULL)
    else:
        log_debug("😴 Sem alteracoes.")

if __name__ == "__main__":
    try: main()
    except Exception as e:
        log_debug(f"💥 ERRO FATAL: {e}")
