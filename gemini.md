# Projeto Daora Kids v2.8.14 📺🍿

**Status:** v2.8.14 - HDMI Dominado, Boot Silencioso e Auto-login Oficial.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Wizard v2.8.14):**
    - **Auto-login Oficial:** Implementado via `raspi-config` para máxima compatibilidade com Debian 13.
    - **HDMI Dashboard:** Monitoramento automático no terminal físico (HDMI) com tela limpa.
    - **Boot Silencioso:** Kernel e mensagens de sistema ocultadas para uma experiência de "Kiosk".
    - **Cérebro v2.8.14:** Independente de locale e com logs de diagnóstico unificados.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
