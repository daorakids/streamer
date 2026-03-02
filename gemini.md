# Projeto Daora Kids v2.8.34 📺🍿

**Status:** v2.8.34 - Sincronizador Robusto e Sincronismo Relâmpago.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.34):**
    - **Sincronizador Robusto:** Script `sincronizador.py` com detecção automática de erros (401, bibliotecas faltantes) e feedback "X de Y".
    - **Sincronismo Relâmpago:** Timer agora dispara 1 min após o boot para garantir preenchimento imediato do pendrive.
    - **Faxina do MicroSD:** Remoção automática de vídeos antigos que entupiam o cartão SD.
    - **Dominação HDMI:** Boot 100% limpo, silencioso e auto-login manual garantido.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Comandos Globais:** `daora-start` e `daora-stop` para gestão ágil.
    - **Logs Consolidados:** `log` unificado mostra o progresso do novo sincronizador.


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
