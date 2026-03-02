# Projeto Daora Kids v2.8.32 📺🍿

**Status:** v2.8.32 - Sincronizador Pro (X de Y) e Faxina Automática.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.32):**
    - **Sincronizador Pro:** Novo script `sincronizador.py` que mapeia o servidor e fornece feedback em tempo real ("Arquivo X de Y").
    - **Faxina Automática:** Remoção de arquivos locais que não existem mais no servidor (Mirroring real).
    - **Sincronismo Duplo:** Boot + Hourly para garantir pendrive sempre em dia.
    - **Dominação HDMI:** Boot 100% limpo e dashboard automático.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Comandos Globais:** `daora-start` e `daora-stop`.
    - **Feedback Visual:** Log unificado agora mostra o progresso detalhado do download.


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
