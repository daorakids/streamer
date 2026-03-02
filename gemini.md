# Projeto Daora Kids v2.8.17 📺🍿

**Status:** v2.8.17 - Opção Nuclear HDMI v2: Purge total e reconstrução de boot.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Wizard v2.8.17):**
    - **Opção Nuclear HDMI:** Purge completo dos pacotes `cloud-init` e `rpi-cloud-init-mods` para limpar o console.
    - **Rebuild Cirúrgico do Boot:** Reconstrução dinâmica do `cmdline.txt` para remover o bug `enable_hdmi=0` e forçar `quiet`.
    - **Auto-login Inabalável:** Implementado via `raspi-config` oficial com troca cirúrgica de usuário para `stream`.
    - **Cérebro v2.8.17:** Diagnóstico total e persistência de configuração.


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
