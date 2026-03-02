# Projeto Daora Kids v2.8.35 📺🍿

**Status:** v2.8.35 - Diagnóstico de Servidor e Sincronismo Relâmpago.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.35):**
    - **Diagnóstico de Servidor:** Sincronizador agora detalha falhas de conexão, URL e autenticação com trechos de HTML.
    - **Sincronismo Relâmpago:** Disparo automático 1 min após o boot.
    - **Libs Python Garantidas:** Instalação automática de dependências (requests, dotenv).
    - **Dominação HDMI:** Boot limpo e auto-login 100% manual para máxima confiabilidade.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Comandos Globais:** `daora-start` e `daora-stop` para gestão ágil.
    - **Logs Consolidados:** `log` unificado mostra o progresso do novo sincronizador e diagnósticos do Cérebro.


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
