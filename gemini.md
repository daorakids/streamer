# Projeto Daora Kids v2.8.25 📺🍿

**Status:** v2.8.25 - Prontidão Total e Wget Inteligente (Fim dos re-downloads).

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.25):**
    - **Prontidão Total:** Cérebro agora aguarda o download de todas as pastas (PT, EN, ES) antes de iniciar a primeira transmissão.
    - **Wget Inteligente:** Fim dos downloads repetitivos e falsos positivos no pendrive (FAT32/exFAT).
    - **Credenciais de Sync:** Registro automático de usuário/senha no `.env`.
    - **Diagnóstico Honesto:** Mensagens claras para "Pasta Faltando" vs "Fora de Horário".

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Dashboard HDMI:** Inicia sozinho no boot físico com tela limpa.
    - **Logs Consolidados:** Comando `log` unificado (Live + Cerebro + Sync).


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
