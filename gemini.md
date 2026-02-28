# Projeto Daora Kids v2.0 📺🍿

**Status:** v2.0 Sincronização Web Ativada (Cérebro v2.1).

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Cérebro Python (`cerebro.py`):**
    - **Sincronização 5-5min:** Baixa `schedule.json` da web a cada 5 minutos.
    - **Detecção de Mudança:** Se o slot atual (Idioma, Modo ou Chave) mudar após o download, reinicia a live imediatamente via `pkill ffmpeg`.
    - **Resiliência Offline:** Se o servidor de agenda estiver fora do ar, usa a última versão salva localmente (`schedule.json`).

2.  **Sincronização de Vídeos (`daorakids-sync.service`):**
    - Sincroniza arquivos `.mp4` a cada hora do servidor para o Pendrive (`/mnt/videos`).

3.  **Streaming Bash (`iniciar_live.sh`):**
    - Loop resiliente (Sequential/Random) que reage às mudanças do Cérebro via `.current_config`.

4.  **Configuração de Servidor:**
    - Padronizado para `schedule.json` em todos os diretórios.
    - Chaves do YouTube agora podem ser atualizadas remotamente no `schedule.json`.

5.  **Manutenção e Saúde:**
    - Notificações de Alerta e Status no Telegram (IP, Idioma e Modo).

---
**Atualizado em:** 28 de Fevereiro de 2026 por Gemini CLI.
