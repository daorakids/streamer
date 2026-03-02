# Projeto Daora Kids v2.8.10 📺🍿

**Status:** v2.8.10 - Independência de Locale, Systemd Timers e HDMI Dashboard.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Wizard v2.8.10):**
    - **Wizard em Bash:** Estabilidade total no terminal.
    - **Blindagem do fstab:** Registro via UUID com detecção dinâmica.
    - **Systemd Timers:** Cérebro e Sincronizador agendados via timers do sistema (substituindo o Cron).
    - **Locale-Independent:** Cérebro usa datas em Inglês para casar com o servidor, ignorando o idioma do Raspberry.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **HDMI Dashboard:** Auto-monitor no TTY1 (HDMI) via `.bashrc`.
    - **Atalhos:** Aliases `ver`, `monitor` e `log`.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Criacao robusta de `/mnt/videos` e isolamento de erros de hardware.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
