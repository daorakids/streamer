# Projeto Daora Kids v2.8.24 📺🍿

**Status:** v2.8.24 - Diagnóstico Honesto e Credenciais de Sync.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.24):**
    - **Bootstrap Único:** Instalação blindada e independente de cache.
    - **Credenciais de Sync:** Registro automático de usuário/senha no `.env` para wget e agenda.
    - **Diagnóstico Honesto:** Diferenciação clara entre "Fora de Horário" e "Pasta Faltando" nos logs.
    - **Pastas Case-Insensitive:** Busca robusta no pendrive ignorando maiúsculas/minúsculas.

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
