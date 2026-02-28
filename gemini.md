# Projeto Daora Kids v2.2 📺🍿

**Status:** v2.2 Bootstrap na Raiz + Sincronização Web Ativada (Cérebro v2.1).

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Instalação Bootstrap (`setup.sh`):**
    - Arquivo movido para a raiz do projeto.
    - Suporta instalação limpa com comando de uma linha (`curl | bash`), baixando o repositório completo antes de invocar o Wizard Python.

2.  **Cérebro Python (`cerebro.py`):**
    - **Sincronização 5-5min:** Baixa `schedule.json` da web com validação de formato.
    - **Detecção de Mudança:** Se o slot atual (Idioma, Modo ou Chave) mudar, reinicia a live gentilmente via `pkill -f ffmpeg`.
    - **Case Insensitive:** A busca pelas pastas de vídeo no pendrive ignora maiúsculas/minúsculas.
    - **Resiliência Offline:** Se o servidor estiver fora, usa a última versão salva localmente.

3.  **Sincronização de Vídeos (`daorakids-sync.service`):**
    - Sincroniza arquivos `.mp4` a cada hora.
    - **Sync-On-Demand:** O Cérebro dispara uma sincronização imediata se o idioma da agenda for alterado.

4.  **Streaming Bash (`iniciar_live.sh`):**
    - Loop resiliente que reage às mudanças do Cérebro via `.current_config`.

5.  **Manutenção e Saúde:**
    - Notificações de Alerta e Status no Telegram (IP, Idioma e Modo).

---
**Atualizado em:** 28 de Fevereiro de 2026 por Gemini CLI.
