# Projeto Daora Kids v2.8.5 📺🍿

**Status:** v2.8.5 - Blindagem Total, Wizard Bash e Super Detecção de Pendrive.

## 🚀 Arquitetura Atual (Sincronização Remota)

1.  **Auto-login & Sistema (Wizard v2.8.5):**
    - **Wizard em Bash:** O questionário inicial foi movido para o `setup.sh` (Bash) para garantir 100% de estabilidade no terminal via `curl`.
    - **Blindagem do fstab:** O instalador não sobrescreve mais o `fstab`; ele apenas anexa o pendrive de forma segura (Safe Append).
    - **Super Detecção de Pendrive:** O sistema procura automaticamente por pendrives em `/dev/sda1`, `sdb1` ou `sdc1` e configura o UUID dinamicamente.

2.  **Monitor de Transmissão (`ver_live.sh`):**
    - **Atalhos:** Aliases `ver`, `monitor` e `log` (oficiais) no `.bashrc`.
    - **Painel:** Inicia no login, mostrando status e logs limpos.

3.  **Instalação Bootstrap (`setup.sh`):**
    - Corrigido: `cp -a` para ocultos e instalação limpa de serviços systemd.

---
**Atualizado em:** 02 de Março de 2026 por Gemini CLI.
