# Daora Kids v2.0 📺🍿

Sistema de Streaming Kids 24/7 (Raspberry Pi 3).

## 🚀 Arquitetura (Cérebro + Bash)

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
   Este arquivo controla tudo remotamente. Você pode definir horários semanais, datas especiais (como Dia das Crianças) e as chaves de transmissão do YouTube.

## 🩺 Manutenção e Saúde
- **Notificações:** Alertas de erro no Pendrive, troca de idioma e status da live via Telegram.
- **Resiliência:** O loop Bash garante que, se o FFmpeg cair por queda de conexão, ele reinicie em 5 segundos.

---
Desenvolvido por Bruno Grange.
