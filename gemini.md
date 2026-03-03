# Projeto Daora Kids v2.9.7 📺🍿

**Status:** v2.9.7 - Alertas de Hardware e Fallback de Armazenamento.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Mega Bootstrap v2.9.7):**
    - **Alertas de Hardware:** O sistema agora detecta e loga explicitamente se o pendrive `DAORAKIDS` não foi encontrado.
    - **Fallback Inteligente:** Se o pendrive falhar, o sistema usa o MicroSD e avisa no log: `⚠️ Usando MicroSD (Fallback)`.
    - **Sincronizador v2.9.7:** Busca agressiva por Label e correção de caminhos aninhados.
    - **Dominação HDMI Total:** Expurgo garantido de cloud-init e boot 100% limpo.

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
