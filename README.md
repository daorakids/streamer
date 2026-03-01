# Daora Kids v2.2 📺🍿

Sistema de Streaming Kids 24/7 (Raspberry Pi 3) - Blindado e Totalmente Remoto.

## 🚀 Como Instalar ou Atualizar (Zero-Touch Setup)

1. **Nova Instalação:** Instale o **Raspberry Pi OS Legacy 64-Bit** (Lite), conecte via SSH e rode o comando de "Autocura" (que ignora o cache e tenta destravar o disco):
   ```bash
   sudo mount -o remount,rw / && curl -sSL "https://raw.githubusercontent.com/daorakids/streamer/main/setup.sh?$(date +%s)" | sudo bash
   ```
2. **Atualização:** Rode o mesmo comando acima. O instalador detectará a versão anterior e oferecerá o **Modo [U]pdate**, que atualiza os scripts e serviços preservando suas chaves de API (`.env`).
3. O Bootstrap baixará o código e iniciará o Wizard (`install.py`). Siga as instruções na tela.

## 📺 Monitoramento em Tempo Real

O sistema agora conta com um painel de monitoramento amigável que inicia automaticamente ao fazer login no terminal (SSH ou HDMI).

- **Comando Rápido:** Digite `ver` ou `monitor` a qualquer momento para ver o status da transmissão.
- **O que ele mostra:** 
  - Idioma atual e Modo de exibição.
  - Logs da Live (FFmpeg), Cérebro (Agenda) e Sincronizador (Download de vídeos).
  - Filtro inteligente que remove o ruído do FFmpeg para focar em eventos importantes.

## 🧠 Arquitetura (Cérebro + Bash)

O sistema opera com um "Cérebro" em Python (`cerebro.py`) rodando via Cron a cada 5 minutos, que coordena um "Braço" em Bash (`iniciar_live.sh`) responsável pelo FFmpeg.

### 🔄 Sincronização Automática
- **Agenda (`schedule.json`):** O `cerebro.py` baixa a agenda do servidor a cada 5 minutos. Se houver qualquer mudança no slot de transmissão atual (Idioma, Modo ou Chave), a live é reiniciada instantaneamente com a nova configuração.
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
   Este arquivo controla tudo remotamente. Você pode definir horários semanais, datas especiais e chaves. A busca das pastas de vídeo no pendrive é *case-insensitive*.

## 🩺 Manutenção e Saúde
- **Notificações:** Alertas de erro no Pendrive, troca de idioma e status da live via Telegram.
- **Resiliência:** O loop Bash garante o FFmpeg reinicie automaticamente em caso de falha de conexão.

---
Desenvolvido por Bruno Grange.
