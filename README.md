# Daora Kids v2.9.8 📺🍿

Sistema de Streaming Kids 24/7 (Raspberry Pi 3) - Blindado e Totalmente Remoto.

## 🚀 Como Instalar ou Atualizar (Zero-Touch Setup)

Para instalar ou atualizar para a versão mais recente (**v2.9.8**), rode o comando abaixo no terminal do Raspberry:

```bash
sudo bash -c "$(curl -sSL https://raw.githubusercontent.com/daorakids/streamer/main/setup.sh?v=$RANDOM)"
```

### O que há de novo na v2.9.8:
*   **Pastas Case-Insensitive:** O sistema agora encontra as pastas de vídeo independente de maiúsculas ou minúsculas (ex: `EN`, `En`, `en`).
*   **Sincronização Otimizada:** O `wget` foi configurado para evitar re-downloads desnecessários e reduzir o ruído nos logs.
*   **Dominação HDMI:** Expurgo total do `cloud-init` e reconstrução cirúrgica do boot para uma experiência limpa.
*   **Auto-login Forçado:** Login automático no usuário `stream` garantido por override manual do systemd.

## 📺 Monitoramento em Tempo Real (HDMI Dashboard)

O sistema conta com um painel de monitoramento amigável que inicia automaticamente no terminal físico (HDMI).

- **Comando Rápido:** Digite `ver` ou `monitor` a qualquer momento para ver o status da transmissão.
- **Auto-Start HDMI:** Ao ligar o Raspberry em uma TV, o dashboard aparecerá sozinho após o boot silencioso.
- **Logs Consolidados:** Use o comando `log` para seguir Live, Cérebro e Sincronizador simultaneamente.

## 🧠 Arquitetura (Cérebro + Bash)

O sistema opera com um "Cérebro" em Python (`cerebro.py`) rodando via **Systemd Timer** a cada 5 minutos, que coordena um "Braço" em Bash (`iniciar_live.sh`) responsável pelo FFmpeg.

### 🔄 Sincronização Automática
- **Agenda (`schedule.json`):** O `cerebro.py` baixa a agenda do servidor a cada 5 minutos. Se houver qualquer mudança no slot, a live é atualizada instantaneamente.
- **Resiliência:** O Cérebro detecta o dia da semana em Inglês, ignorando o idioma local do sistema para evitar conflitos de agenda.
- **Vídeos (`.mp4`):** O serviço `daorakids-sync.service` sincroniza os vídeos via `wget` de forma inteligente.

## 🩺 Manutenção e Saúde
- **Notificações:** Alertas via Telegram para troca de idioma e status.
- **Hardware Watchdog:** O Raspberry reinicia automaticamente em caso de travamento total do sistema.
- **Log2Ram (Opcional):** Prolonga a vida útil do cartão SD.

---
Desenvolvido por Bruno Grange.
