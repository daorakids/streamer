# Projeto Daora Kids v2.8.15 📺🍿

**Status:** v2.8.15 - Dominio Total do HDMI e Auto-login Forçado.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Wizard v2.8.15):**
    - **Auto-login Forçado:** Override manual do Getty (TTY1) para garantir o login automático do usuário `stream`.
    - **Cloud-init Desativado:** Remoção total das mensagens técnicas de boot que sujavam o HDMI.
    - **HDMI Dashboard:** Atraso de segurança no `.bashrc` para garantir uma tela limpa no Dashboard.
    - **Cérebro v2.8.15:** Super Logs de diagnóstico e independência de locale.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Logs Unificados:** Agora mostra Live, Cérebro e Sincronizador em uma única tela.
    - **Limpeza de Tela:** Comando `ver` limpa o terminal de forma absoluta antes de exibir o status.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
