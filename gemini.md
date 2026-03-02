# Projeto Daora Kids v2.8.38 📺🍿

**Status:** v2.8.38 - Sincronizador Ultra-Sensível e Início Forçado.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.38):**
    - **Sincronizador Ultra-Sensível:** Regex aprimorado para capturar links em qualquer formato de servidor.
    - **Início Imediato:** Setup agora força o start dos serviços e timers antes do reboot para diagnósticos rápidos.
    - **Dominação HDMI Final:** Expurgo total de cloud-init e reconstrução de boot garantidos.
    - **Auto-login Manual:** Implementado via override direto para evitar falhas de utilitários externos.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Comandos de Controle:** `daora-start` e `daora-stop` integrados ao dashboard.
    - **Logs Consolidados:** Exibe progresso do novo sincronizador e relógio do Cérebro.


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
