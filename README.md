# Daora Kids v3.2 📺🍿

Sistema de Streaming Kids 24/7 (Raspberry Pi 3 ou superior) - Blindado e Totalmente Remoto.

> **SO Recomendado:** Raspberry Pi OS Lite (64-bit) - Baseado em Debian 13 (Trixie/Bookworm).

## 🚀 Como Instalar ou Atualizar (Zero-Touch Setup)

Para instalar ou atualizar para a versão mais recente (**v3.2**), rode o comando abaixo no terminal do Raspberry:

```bash
sudo bash -c "$(curl -sSL https://raw.githubusercontent.com/daorakids/streamer/main/setup.sh?v=$RANDOM)"
```

### O que há de novo na v3.2:
*   **Padronização Técnica:** O componente "Cérebro" agora se chama oficialmente **Scheduler**, com nomes de arquivos e serviços atualizados.
*   **Pastas Case-Insensitive:** O sistema agora encontra as pastas de vídeo independente de maiúsculas ou minúsculas.
*   **Dominação HDMI:** Boot 100% silencioso e dashboard automático em tela cheia.

## 📺 Monitoramento em Tempo Real (HDMI Dashboard)

O sistema conta com um painel de monitoramento amigável que inicia automaticamente no terminal físico (HDMI).

- **Comando Rápido:** Digite `ver` ou `monitor` a qualquer momento para ver o status da transmissão.
- **Logs Consolidados:** Use o comando `log` para seguir Live, Scheduler e Sincronizador simultaneamente.

## 🧠 Arquitetura (Scheduler + Bash)

O sistema opera com um **Scheduler** em Python (`scheduler.py`) rodando via **Systemd Timer** a cada 5 minutos, que coordena um "Braço" em Bash (`iniciar_live.sh`) responsável pelo FFmpeg.

### 🔄 Sincronização Automática
- **Agenda (`schedule.json`):** O Scheduler baixa a agenda do servidor a cada 5 minutos. Se houver qualquer mudança no slot, a live é atualizada instantaneamente.
- **Vídeos (`.mp4`):** O serviço `daorakids-sync.service` sincroniza os vídeos via `wget` de forma inteligente.

## 🩺 Manutenção e Saúde
- **Notificações:** Alertas via Telegram para troca de idioma e status.
- **Hardware Watchdog:** O Raspberry reinicia automaticamente em caso de travamento total do sistema.
- **Log2Ram (Opcional):** Prolonga a vida útil do cartão SD.

---
Desenvolvido por Bruno Grange.
