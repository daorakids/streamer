#!/usr/bin/env python3
import json
import datetime
import os
import subprocess
import requests
import socket
import hashlib
from dotenv import load_dotenv

# --- CARREGAR CONFIGS DO .ENV ---
BASE_DIR = "/home/stream"
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# --- CAMINHOS ---
SCHEDULE_PATH = os.path.join(BASE_DIR, "schedule.json")
CURRENT_STATE_FILE = os.path.join(BASE_DIR, "estado_atual.json")
CONFIG_FILE = os.path.join(BASE_DIR, ".current_config")
VIDEO_ROOT = "/mnt/videos"

# --- CONFIGS TELEGRAM ---
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEB_SCHEDULE_URL = os.getenv("SYNC_URL", "https://daorakids.com.br/util/stream/").rstrip('/') + "/schedule.json"

def get_ips():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal = s.getsockname()[0]
        s.close()
        external = requests.get('https://api.ipify.org', timeout=5).text
    except:
        internal, external = "N/A", "N/A"
    return internal, external

def send_telegram(message):
    if not TG_TOKEN or not TG_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        data = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
    except: pass

def find_video_dir(lang):
    """Encontra a pasta de vídeos de forma case-insensitive (ex: EN, en, En)."""
    if not os.path.exists(VIDEO_ROOT): return None
    lang_lower = lang.lower()
    for item in os.listdir(VIDEO_ROOT):
        if item.lower() == lang_lower and os.path.isdir(os.path.join(VIDEO_ROOT, item)):
            return os.path.join(VIDEO_ROOT, item)
    return None

def update_schedule_from_web():
    try:
        response = requests.get(WEB_SCHEDULE_URL, timeout=15)
        if response.status_code == 200:
            new_content = response.text
            try:
                json.loads(new_content) # Valida se é JSON
            except ValueError: return

            if os.path.exists(SCHEDULE_PATH):
                with open(SCHEDULE_PATH, 'r') as f:
                    old_content = f.read()
                if hashlib.md5(new_content.encode()).hexdigest() == hashlib.md5(old_content.encode()).hexdigest():
                    return 
            
            with open(SCHEDULE_PATH, 'w') as f:
                f.write(new_content)
            print(f"[{datetime.datetime.now()}] Agenda atualizada via Web.")
    except: pass

def get_current_slot():
    try:
        if not os.path.exists(SCHEDULE_PATH): return None
        with open(SCHEDULE_PATH, 'r') as f:
            data = json.load(f)
    except: return None

    if data.get("emergency_stop"): return {"lang": "STOP"}

    agora = datetime.datetime.now()
    hoje_iso = agora.strftime("%Y-%m-%d")
    hoje_dia = agora.strftime("%a").lower()
    hora_atual = agora.strftime("%H:%M")

    slot = None
    special = data.get("special_dates", {}).get(hoje_iso)
    if special:
        for s in special:
            if s["start"] <= hora_atual <= s["end"]: slot = s; break

    if not slot:
        day_slots = data.get("schedule", {}).get(hoje_dia)
        if day_slots:
            for s in day_slots:
                if s["start"] <= hora_atual <= s["end"]: slot = s; break

    if not slot: return {"lang": "OFF"}
    
    # Normaliza o idioma para busca de chave e pasta
    lang_key = slot['lang'].lower()
    web_keys = data.get("stream_keys", {})
    
    # Busca a chave (prioridade para o que está no JSON)
    if lang_key in web_keys:
        slot["key"] = web_keys[lang_key]
    else:
        # Tenta buscar as chaves do .env se não estiver no JSON
        slot["key"] = os.getenv(f"YT_KEY_{lang_key.upper()}")
        
    return slot

def main():
    update_schedule_from_web()
    slot = get_current_slot()
    if not slot: return

    current_state = {}
    if os.path.exists(CURRENT_STATE_FILE):
        try:
            with open(CURRENT_STATE_FILE, 'r') as f:
                current_state = json.load(f)
        except: pass

    # Se mudar qualquer coisa no slot (horário, modo, chave ou idioma), reinicia.
    if slot != current_state:
        target_lang = slot.get("lang", "OFF").lower()
        target_mode = slot.get("mode", "sequential")
        target_key = slot.get("key", "")
        
        with open(CURRENT_STATE_FILE, 'w') as f:
            json.dump(slot, f)

        if target_lang in ["stop", "off"]:
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            send_telegram(f"🛑 <b>Daora Kids</b>\nStatus: {target_lang.upper()}\nLive finalizada.")
        else:
            # Sincronização de vídeos on-demand se o idioma mudou
            if target_lang != current_state.get("lang", "").lower():
                subprocess.Popen(["sudo", "systemctl", "start", "daorakids-sync.service"])

            # Busca a pasta de vídeos (Independente de ser EN, en ou En)
            video_dir = find_video_dir(target_lang)
            
            if not video_dir or not os.listdir(video_dir):
                ip_int, _ = get_ips()
                send_telegram(f"🚨 <b>ERRO: Pasta '{target_lang.upper()}' não encontrada.</b>\nIP: {ip_int}\nAguardando sincronização...")
                # O loop do iniciar_live.sh cuidará de tentar novamente.
                if not video_dir: video_dir = os.path.join(VIDEO_ROOT, target_lang)

            with open(CONFIG_FILE, 'w') as f:
                f.write(f'CHAVE="{target_key}"\n')
                f.write(f'PASTA_VIDEOS="{video_dir}"\n')
                f.write(f'MODO="{target_mode}"\n')
            
            ip_int, _ = get_ips()
            send_telegram(f"🚀 <b>Daora Kids AO VIVO!</b>\nIdioma: {target_lang.upper()}\nModo: {target_mode}\nIP: {ip_int}")

        subprocess.run(["pkill", "-f", "ffmpeg"], stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
