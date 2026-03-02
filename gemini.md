# Projeto Daora Kids v2.8.31 📺🍿

**Status:** v2.8.31 - Sincronismo Duplo (Boot + Hora Cheia) e Arquivos Físicos Garantidos.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.8.31):**
    - **Sincronismo Inteligente:** O Pi agora sincroniza 2 min após o boot e repete exatamente no início de cada hora cheia.
    - **Arquivos Físicos:** Serviços e timers agora possuem arquivos físicos no repositório para garantir instalação sem erros de recursos.
    - **Dominação HDMI:** Expurgo total de cloud-init e mensagens de boot limpas.
    - **Prontidão Total:** Live aguarda download de todas as pastas (PT, EN, ES) antes de iniciar.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Comandos Globais:** `daora-start` e `daora-stop` para gestão fácil dos serviços.
    - **HDMI Dashboard:** Tela preta limpa que inicia o monitor automaticamente.
    - **Logs Consolidados:** `log` unificado (Live + Cerebro + Sync).


2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
