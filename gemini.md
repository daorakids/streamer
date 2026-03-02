# Projeto Daora Kids v2.8.22 📺🍿

**Status:** v2.8.22 - Pastas Case-Insensitive e Sincronização Inteligente.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.22):**
    - **Bootstrap Único:** Toda a lógica de instalação e dominação HDMI consolidada no `setup.sh`.
    - **Pastas Robustas:** Busca de pastas de vídeo ignorando maiúsculas/minúsculas no pendrive.
    - **Wget Otimizado:** Sincronização de vídeos mais rápida e com logs limpos.
    - **Auto-login & HDMI:** Expurgo de cloud-init e override manual de Getty garantidos.

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
