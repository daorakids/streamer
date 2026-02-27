# Projeto Daora Kids v2.0 📺🍿

**Status:** v2.0 Implementada com Sucesso (Estrutura de "Cérebro" Python + "Braço" Bash).

## 🚀 Arquitetura Atual (Python-Based)

1.  **Cérebro Python (`cerebro.py`):**
    - Roda via Cron a cada 5 minutos.
    - Valida o Pendrive USB e a montagem automática.
    - Monitora IP Interno/Externo e gerencia trocas de idioma.

2.  **Streaming Bash (`iniciar_live.sh`):**
    - Loop resiliente (Sequential/Random).
    - Lê chaves do YouTube e pastas de vídeos do `.current_config`.

3.  **Setup Automatizado (`setup.sh` + `install.py`):**
    - Wizard inteligente para YouTube, Telegram e Sync Server.
    - Configura Auto-login no HDMI (TTY1).
    - Suporte Universal a Pendrives (FAT32, NTFS, exFAT).

4.  **Sync Server Configuration (Apache):**
    - Habilita `Options +Indexes` para permitir navegação do `wget`.
    - Proteção por `Auth Basic` (.htaccess e .htpasswd).

5.  **Manutenção e Saúde (Resumo):**
    - **01:00 às 05:00:** Descanso e limpeza.
    - Notificações de Alerta (apenas problemas) no Telegram.

---
**Atualizado em:** 26 de Fevereiro de 2026 por Gemini CLI.
