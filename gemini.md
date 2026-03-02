# Projeto Daora Kids v2.8.16 📺🍿

**Status:** v2.8.16 - Opção Nuclear HDMI: Purge cloud-init e reconstrução de cmdline.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Wizard v2.8.16):**
    - **Opção Nuclear HDMI:** Purgagem completa do pacote `cloud-init` para limpar o console.
    - **Rebuild cmdline.txt:** Reconstrução cirúrgica do arquivo de boot para remover o bug `enable_hdmi=0` e forçar `quiet`.
    - **Auto-login Manual:** Override do Getty (TTY1) criado com comando único para evitar falhas de diretório.
    - **Cérebro v2.8.16:** Diagnóstico avançado e detecção de slot inteligente.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
