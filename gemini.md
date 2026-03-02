# Projeto Daora Kids v2.8.33 📺🍿

**Status:** v2.8.33 - Libs Python Garantidas e Sincronismo Relâmpago (1min).

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.33):**
    - **Libs Garantidas:** Instalação automática de `python3-requests` e `python3-dotenv` para evitar falhas no sincronizador.
    - **Sincronismo Relâmpago:** Timer de sincronização agora dispara apenas 1 min após o boot (antes 5 min).
    - **Sincronizador Pro:** Script `sincronizador.py` com feedback "Arquivo X de Y" e mirroring real.
    - **HDMI Dashboard:** Boot silencioso e monitoramento automático via `.bashrc`.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Gestão de Serviços:** Comandos `daora-start` e `daora-stop` oficiais.
    - **Manual Integrado:** Lembrete de comandos exibido no log a cada 5 minutos.


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
