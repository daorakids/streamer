# Projeto Daora Kids v2.8.36 📺🍿

**Status:** v2.8.36 - Sincronização Flexível e Alinhamento de Versões.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.36):**
    - **Wizard Flexível:** Pergunta da `SYNC_URL` restaurada para permitir mudança de servidores.
    - **Sincronizador Robusto:** Script `sincronizador.py` agora inclui diagnósticos detalhados e autenticação.
    - **Dominação HDMI:** Boot 100% silencioso e auto-login manual no usuário `stream`.
    - **Cérebro v2.8.36:** Alinhado com a agenda e independente de locale.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Comandos Globais:** `daora-start` e `daora-stop` para gestão ágil.
    - **Feedback Visual:** Log unificado mostra o progresso do sincronizador e lembretes de comandos.


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
