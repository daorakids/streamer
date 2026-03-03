# Projeto Daora Kids v3.1 📺🍿

**Status:** v3.1 - Padronização Dashboard e Nomenclaturas.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v3.1):**
    - **Nomenclatura Limpa:** O arquivo motor do dashboard agora se chama `dashboard.sh` (substituindo `ver_live.sh`).
    - **Logs Coloridos (ANSI):** Identificação visual rápida por cores em todos os scripts Python e Bash.
    - **Transfusão Inteligente:** Sincronizador v3.1 pronto para gerir transições MicroSD -> Pendrive.
    - **Dominação HDMI Total:** Boot silencioso e auto-login garantidos.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Comandos de Controle:** `daora-start` e `daora-stop` integrados ao dashboard.
    - **Logs Consolidados:** Exibe progresso do novo sincronizador e relógio do Cérebro.


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

## 📋 Protocolo de Versão (Obrigatório em todo Commit)

Para cada nova versão, os seguintes locais **DEVEM** ser atualizados simultaneamente:

1.  **Manifestos:**
    - `README.md`: Título e comando de instalação.
    - `gemini.md`: Título e linha de status.
2.  **Scripts de Instalação:**
    - `setup.sh`: Cabeçalho, print de início, versão do Dashboard e print de sucesso.
    - `home/stream/install.py`: Print do Wizard, versão do Dashboard e print de sucesso.
3.  **Scripts de Execução:**
    - `home/stream/cerebro.py`: Log de início (main).
    - `home/stream/sincronizador.py`: Log de início (main).
4.  **Serviços:**
    - `home/stream/daorakids-sync.service`: Descrição (Unit).

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
