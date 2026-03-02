# Daora Kids v2.8.16 📺🍿

Sistema de Streaming Kids 24/7 (Raspberry Pi 3) - Blindado e Totalmente Remoto.

## 🚀 Como Instalar ou Atualizar (Zero-Touch Setup)

Para instalar ou atualizar para a versão mais recente (**v2.8.16**), rode o comando abaixo no terminal do Raspberry:

```bash
sudo bash -c "$(curl -sSL https://raw.githubusercontent.com/daorakids/streamer/main/setup.sh?v=$RANDOM)"
```

### O que há de novo na v2.8.10:
*   **Wizard Bash Estável:** Configuração inicial via Bash para evitar travamentos de teclado.
*   **Montagem Blindada:** Registro seguro no `fstab` via UUID com detecção automática de portas USB.
*   **Cérebro Independente:** Agendamento via Systemd Timer e detecção de datas em Inglês (Locale-Independent).
*   **HDMI Dashboard:** O monitor de transmissão abre automaticamente no HDMI logo após o boot.

## 📺 Monitoramento em Tempo Real (HDMI Dashboard)

O sistema conta com um painel de monitoramento amigável que inicia automaticamente no terminal físico (HDMI).

- **Comando Rápido:** Digite `ver` ou `monitor` a qualquer momento para ver o status da transmissão.
- **Auto-Start HDMI:** Ao ligar o Raspberry em uma TV, o dashboard aparecerá sozinho.
- **Logs Consolidados:** Use o comando `log` para seguir o que FFmpeg e Cérebro estão fazendo.

## 🧠 Arquitetura (Cérebro + Bash)

O sistema opera com um "Cérebro" em Python (`cerebro.py`) rodando via **Systemd Timer** a cada 5 minutos, que coordena um "Braço" em Bash (`iniciar_live.sh`) responsável pelo FFmpeg.

### 🔄 Sincronização Automática
- **Agenda (`schedule.json`):** O `cerebro.py` baixa a agenda do servidor a cada 5 minutos. Se houver qualquer mudança no slot de transmissão atual (Idioma, Modo ou Chave), a live é reiniciada instantaneamente.
- **Resiliência:** O Cérebro garante a criação do arquivo de configuração mesmo em casos de reboot ou falha de rede.
- **Vídeos (`.mp4`):** O serviço `daorakids-sync.service` sincroniza os vídeos via `wget` a cada 1 hora.

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
   Este arquivo controla tudo remotamente. Você pode definir horários semanais, datas especiais e chaves.

## 🩺 Manutenção e Saúde
- **Notificações:** Alertas de troca de idioma e status da live via Telegram.
- **Hardware Watchdog:** O sistema monitora a si mesmo e reinicia o hardware se houver travamento total.
- **Log2Ram (Opcional):** Protege o cartão SD movendo logs para a memória RAM.

---
Desenvolvido por Bruno Grange.
