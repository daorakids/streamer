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

# --- CONFIGS TELEGRAM ---
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYNC_URL = os.getenv("SYNC_URL", "https://daorakids.com.br/util/stream/").rstrip('/')
WEB_SCHEDULE_URL = f"{SYNC_URL}/schedule.json"

def get_ips():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal = s.getsockname()[0]
        s.close()
        external = requests.get('https://api.ipify.org', timeout=5).text
    except Exception as e:
        log_debug(f"⚠️ Erro ao obter IPs: {e}")
        internal, external = "N/A", "N/A"
    return internal, external

def find_video_dir(lang):
    if not os.path.exists(VIDEO_ROOT):
        log_debug(f"🚨 PASTA RAIZ NAO EXISTE: {VIDEO_ROOT}")
        return None
    lang_lower = lang.lower()
    for item in os.listdir(VIDEO_ROOT):
        if item.lower() == lang_lower and os.path.isdir(os.path.join(VIDEO_ROOT, item)):
            return os.path.join(VIDEO_ROOT, item)
    return None

def update_schedule_from_web():
    log_debug(f"🌐 Tentando baixar agenda de: {WEB_SCHEDULE_URL}")
    try:
        response = requests.get(WEB_SCHEDULE_URL, timeout=15)
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
                    log_debug("✅ Agenda ja esta atualizada (MD5 bate).")
                    return 
            
            with open(SCHEDULE_PATH, 'w') as f:
                f.write(new_content)
            log_debug("✨ Nova agenda salva com sucesso!")
        else:
            log_debug(f"⚠️ Servidor retornou erro {response.status_code}")
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
        log_debug(f"❌ Erro ao ler JSON local: {e}")
        return None

    if data.get("emergency_stop"):
        log_debug("🛑 EMERGENCY STOP detectado no JSON!")
        return {"lang": "STOP"}

    agora = datetime.datetime.now()
    hoje_iso = agora.strftime("%Y-%m-%d")
    days_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    hoje_dia = days_map[agora.weekday()]
    hora_atual = agora.strftime("%H:%M")

    log_debug(f"⏰ Horario do Sistema: {hoje_dia} {hora_atual}")

    slot = None
    # 1. Checa datas especiais
    special = data.get("special_dates", {}).get(hoje_iso)
    if special:
        log_debug(f"📅 Data especial detectada: {hoje_iso}")
        for s in special:
            if s["start"] <= hora_atual <= s["end"]:
                slot = s
                log_debug(f"🎯 Slot especial encontrado: {slot}")
                break

    # 2. Checa agenda semanal
    if not slot:
        day_slots = data.get("schedule", {}).get(hoje_dia)
        if day_slots:
            for s in day_slots:
                if s["start"] <= hora_atual <= s["end"]:
                    slot = s
                    log_debug(f"🎯 Slot semanal encontrado: {slot}")
                    break

    if not slot:
        log_debug("💤 Nenhum slot programado para este horario na agenda.")
        # Tenta encontrar o próximo slot do dia para informar no log
        next_slot = None
        day_slots = data.get("schedule", {}).get(hoje_dia, [])
        for s in day_slots:
            if s["start"] > hora_atual:
                next_slot = s["start"]
                break
        if next_slot:
            log_debug(f"⏰ Proxima transmissao programada para as {next_slot}")
        else:
            log_debug("⏰ Nao ha mais transmissoes programadas para hoje.")
            
        return {"lang": "OFF"}
    
    lang_key = slot['lang'].lower()
    web_keys = data.get("stream_keys", {})
    
    if lang_key in web_keys:
        slot["key"] = web_keys[lang_key]
    else:
        slot["key"] = os.getenv(f"YT_KEY_{lang_key.upper()}")
        log_debug(f"🔑 Chave obtida via .env para {lang_key}")
        
    return slot

def main():
    log_debug("--- INICIANDO EXECUCAO DO CEREBRO ---")
    
    # Check Uptime
    try:
        with open("/proc/uptime", "r") as f:
            uptime = float(f.readline().split()[0])
            if uptime < 60:
                log_debug(f"⏳ Sistema ligou ha pouco ({uptime:.1f}s), aguardando rede...")
                time.sleep(15)
    except: pass

    update_schedule_from_web()
    slot = get_current_slot()
    
    if not slot:
        log_debug("🚨 Falha critica: Nao foi possivel determinar o slot.")
        return

    current_state = {}
    if os.path.exists(CURRENT_STATE_FILE):
        try:
            with open(CURRENT_STATE_FILE, 'r') as f:
                current_state = json.load(f)
        except: pass

    # Forçar criação se o arquivo sumiu
    config_missing = not os.path.exists(CONFIG_FILE)
    
    if slot != current_state or config_missing:
        log_debug(f"🔄 Mudanca de estado detectada (ou config faltando={config_missing})")
        target_lang = slot.get("lang", "OFF").lower()
        target_mode = slot.get("mode", "sequential")
        target_key = slot.get("key", "")
        
        with open(CURRENT_STATE_FILE, 'w') as f:
            json.dump(slot, f)

        if target_lang in ["stop", "off"]:
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            log_debug("🛑 Modo OFF/STOP. Removendo arquivo de configuracao.")
        else:
            video_dir = find_video_dir(target_lang)
            if not video_dir:
                video_dir = os.path.join(VIDEO_ROOT, target_lang)
                log_debug(f"❌ ERRO CRITICO: Pasta de videos '{video_dir}' nao foi encontrada no pendrive!")
                log_debug(f"   (Conteudo de {VIDEO_ROOT}: {os.listdir(VIDEO_ROOT) if os.path.exists(VIDEO_ROOT) else 'RAIZ NAO EXISTE'})")
                # Remove config antiga para nao rodar video errado
                if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
                return

            try:
                with open(CONFIG_FILE, 'w') as f:
                    f.write(f'CHAVE="{target_key}"\n')
                    f.write(f'PASTA_VIDEOS="{video_dir}"\n')
                    f.write(f'MODO="{target_mode}"\n')
                log_debug(f"✅ Arquivo {CONFIG_FILE} gravado com sucesso!")
                os.chmod(CONFIG_FILE, 0o777)
            except Exception as e:
                log_debug(f"❌ ERRO AO GRAVAR {CONFIG_FILE}: {e}")

        # Reinicia o FFmpeg se a live estiver ativa
        log_debug("♻️ Reiniciando processos de transmissao...")
        subprocess.run(["pkill", "-f", "ffmpeg"], stderr=subprocess.DEVNULL)
    else:
        log_debug("😴 Estado inalterado. Nada a fazer.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_debug(f"💥 ERRO FATAL NO PYTHON: {e}")
        import traceback
        log_debug(traceback.format_exc())
