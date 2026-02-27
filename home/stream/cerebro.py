#!/usr/bin/env python3
import json
import datetime
import os
import subprocess
import requests
import socket
from dotenv import load_dotenv

# --- CARREGAR CONFIGS DO .ENV ---
BASE_DIR = "/home/stream"
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# --- CAMINHOS ---
SCHEDULE_PATH = os.path.join(BASE_DIR, "schedule.json")
CURRENT_STATE_FILE = os.path.join(BASE_DIR, "idioma_atual.txt")
CONFIG_FILE = os.path.join(BASE_DIR, ".current_config")
VIDEO_ROOT = "/mnt/videos"

# --- CONFIGS TELEGRAM ---
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_ips():
    """Retorna IP interno e externo."""
    try:
        # Interno
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal = s.getsockname()[0]
        s.close()
        # Externo
        external = requests.get('https://api.ipify.org', timeout=5).text
    except:
        internal, external = "N/A", "N/A"
    return internal, external

def send_telegram(message):
    """Envia mensagem para o Telegram."""
    if not TG_TOKEN or not TG_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        data = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Erro Telegram: {e}")

def get_current_slot():
    """Busca o idioma e modo na agenda."""
    try:
        with open(SCHEDULE_PATH, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erro ao ler agenda: {e}")
        return None

    if data.get("emergency_stop"): return {"lang": "STOP"}

    agora = datetime.datetime.now()
    hoje_iso = agora.strftime("%Y-%m-%d")
    hoje_dia = agora.strftime("%a").lower()
    hora_atual = agora.strftime("%H:%M")

    # 1. Datas Especiais
    slot = None
    special = data.get("special_dates", {}).get(hoje_iso)
    if special:
        for s in special:
            if s["start"] <= hora_atual <= s["end"]: slot = s; break

    # 2. Grade Semanal (se não houver especial)
    if not slot:
        day_slots = data.get("schedule", {}).get(hoje_dia)
        if day_slots:
            for s in day_slots:
                if s["start"] <= hora_atual <= s["end"]: slot = s; break

    if not slot: return {"lang": "OFF"}
    
    # Busca a chave correspondente no .env
    key_env_name = f"YT_KEY_{slot['lang'].upper()}"
    slot["key"] = os.getenv(key_env_name)
    return slot

def main():
    slot = get_current_slot()
    if not slot: return

    target_lang = slot["lang"]
    target_mode = slot.get("mode", "sequential")
    target_key = slot.get("key", "")

    # Lê o que está rolando agora
    current_state = ""
    if os.path.exists(CURRENT_STATE_FILE):
        with open(CURRENT_STATE_FILE, 'r') as f:
            current_state = f.read().strip()

    # Só atua se houver mudança de idioma ou estado
    if target_lang != current_state:
        print(f"[{datetime.datetime.now()}] Mudança: {current_state} -> {target_lang}")
        
        with open(CURRENT_STATE_FILE, 'w') as f:
            f.write(target_lang)

        if target_lang in ["STOP", "OFF"]:
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            send_telegram(f"🛑 <b>Daora Kids</b>\nStatus: {target_lang}\nLive finalizada.")
        else:
            # Verifica o Pen Drive
            video_dir = os.path.join(VIDEO_ROOT, target_lang)
            if not os.path.exists(video_dir) or not os.listdir(video_dir):
                ip_int, ip_ext = get_ips()
                send_telegram(f"🚨 <b>ERRO NO PENDRIVE</b>\nIdioma: {target_lang}\nCaminho: {video_dir}\nIP Int: {ip_int}\nIP Ext: {ip_ext}")
                return

            # Gera config para o Bash
            with open(CONFIG_FILE, 'w') as f:
                f.write(f'CHAVE="{target_key}"\n')
                f.write(f'PASTA_VIDEOS="{video_dir}"\n')
                f.write(f'MODO="{target_mode}"\n')
            
            ip_int, ip_ext = get_ips()
            msg = (f"🚀 <b>Daora Kids AO VIVO!</b>\n"
                   f"Idioma: {target_lang.upper()}\n"
                   f"Modo: {target_mode}\n"
                   f"-------------------\n"
                   f"IP Interno: <code>{ip_int}</code>\n"
                   f"IP Externo: <code>{ip_ext}</code>")
            send_telegram(msg)

        # Força o reinício do FFmpeg
        subprocess.run(["pkill", "-9", "-f", "ffmpeg"], stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
