# Projeto Daora Kids v2.5 📺🍿

**Status:** v2.5 Auto-login 'stream' + Modo Update + Monitoramento (Cérebro v2.1).

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (`install.py`):**
    - **Apropriação do Terminal:** Configura o override do `getty@tty1` para logar o usuário `stream` automaticamente no boot, eliminando a necessidade de logar como `pi`.
    - **Modo [U]pdate:** Detecta instalações anteriores e preserva configurações do `.env`.
    - **Gerenciamento de Serviços:** Desliga live/ffmpeg antes de atualizar e faz `reboot` automático pós-instalação.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Atalhos:** Aliases `ver`, `monitor` e `log` (agora oficial) no `.bashrc`.
    - **Painel:** Inicia no login, mostrando status e logs limpos.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Corrigido: `cp -a` para ocultos e `sudo` obrigatório.

---
**Atualizado em:** 01 de Março de 2026 por Gemini CLI.
