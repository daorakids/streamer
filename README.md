# Daora Kids v2.2 📺🍿

Sistema de Streaming Kids 24/7 (Raspberry Pi 3) - Blindado e Totalmente Remoto.

## 🚀 Como Instalar (Zero-Touch Setup)

1. Instale o **Raspberry Pi OS Legacy 64-Bit** (Lite).
2. Conecte o Pi na rede, acesse via SSH e rode (certifique-se de que o repositório é público):
   ```bash
   curl -sSL https://raw.githubusercontent.com/daorakids/streamer/main/setup.sh | bash
   ```
3. O Bootstrap baixará o código e iniciará o Wizard (`install.py`). Siga as instruções na tela (Chaves, Telegram, Servidor).

## 🧠 Arquitetura (Cérebro + Bash)

O sistema opera com um "Cérebro" em Python (`cerebro.py`) rodando via Cron a cada 5 minutos, que coordena um "Braço" em Bash (`iniciar_live.sh`) responsável pelo FFmpeg.

### 🔄 Sincronização Automática
- **Agenda (`schedule.json`):** O `cerebro.py` baixa a agenda do servidor a cada 5 minutos. Se houver qualquer mudança no slot de transmissão atual (Idioma, Modo ou Chave), a live é reiniciada instantaneamente com a nova configuração (`sync-on-demand` incluso para vídeos).
- **Vídeos (`.mp4`):** O serviço `daorakids-sync.service` sincroniza os vídeos via `wget` a cada 1 hora, mantendo o Pendrive atualizado.

## 📂 Configuração do Servidor

Para o Raspberry sincronizar, seu servidor (Apache/Nginx) deve permitir a listagem de arquivos e proteger a pasta.

1. **Estrutura no Servidor (`/util/stream/`):**
   ```text
   /util/stream/
   ├── schedule.json (Agenda de horários e chaves)
   ├── pt/ (vídeos em português)
   ├── en/ (vídeos em inglês)
   └── es/ (vídeos em espanhol)
   ```

2. **O arquivo `schedule.json`:**
   Este arquivo controla tudo remotamente. Você pode definir horários semanais, datas especiais e chaves. A busca das pastas de vídeo no pendrive é *case-insensitive* (ex: `EN`, `en`, `En`).

## 🩺 Manutenção e Saúde
- **Notificações:** Alertas de erro no Pendrive, troca de idioma e status da live via Telegram.
- **Resiliência:** O loop Bash garante que o FFmpeg reinicie automaticamente em caso de falha de conexão.

---
Desenvolvido por Bruno Grange.
