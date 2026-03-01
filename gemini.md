# Projeto Daora Kids v2.4 📺🍿

**Status:** v2.4 Modo Update Inteligente + Monitoramento Real-Time (Cérebro v2.1).

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Wizard de Instalação e Update (`install.py`):**
    - **Modo [U]pdate:** Detecta instalações anteriores via `.env` e oferece atualização rápida de scripts sem perder chaves de API.
    - **Gerenciamento de Serviços:** Para automaticamente a live e o sincronizador antes de atualizar, garantindo uma transição limpa.
    - **Pós-Instalação:** Habilita serviços, agenda tarefas no Cron e executa `reboot` automático após 10 segundos.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Atalhos:** Aliases `ver` e `monitor` adicionados ao `.bashrc`.
    - **Painel:** Abre automaticamente ao logar, mostrando Idioma, Modo e Logs consolidados (Live + Sync).
    - **Filtro:** Esconde logs repetitivos do FFmpeg para focar em erros e trocas de vídeo.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Corrigido: Agora usa `cp -a` para incluir arquivos ocultos (ex: `.bashrc`, `.env`).
    - Exige privilégios de `sudo` para instalação completa de dependências e usuários.

4.  **Cérebro Python (`cerebro.py`):**
    - **Sincronização 5-5min:** Baixa `schedule.json` da web com validação de formato.
    - **Detecção de Mudança:** Se o slot mudar, reinicia a live gentilmente via `pkill -f ffmpeg`.

---
**Atualizado em:** 01 de Março de 2026 por Gemini CLI.
