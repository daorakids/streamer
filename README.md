# Daora Kids v2.0 📺🍿

Sistema de Streaming Kids 24/7 (Raspberry Pi 3).

## 🚀 Como Instalar (Zero-Touch Setup)

1. Instale o **Raspberry Pi OS Legacy 64-Bit** (Lite).
2. Conecte o Pi na rede, acesse via SSH e rode:
   ```bash
   curl -sSL https://raw.githubusercontent.com/SEU_USUARIO/daorakids/main/setup.sh | bash
   ```
3. Siga o Wizard Python (YouTube Keys, Telegram e URL do servidor).

## 📂 Configuração do Servidor de Vídeos (Apache)

Para o Raspberry sincronizar os vídeos, seu servidor Apache deve permitir a listagem.

1. **Estrutura no Servidor:**
   ```text
   /util/stream/
   ├── .htaccess
   ├── .htpasswd
   ├── pt/ (vídeos aqui)
   ├── en/ (vídeos aqui)
   └── es/ (vídeos aqui)
   ```

2. **Crie o `.htaccess` na raiz da pasta de vídeos:**
   ```apache
   Options +Indexes
   AuthType Basic
   AuthName "Acesso Restrito"
   AuthUserFile /caminho/absoluto/para/.htpasswd
   Require valid-user
   ```

3. **Gere o `.htpasswd` (via SSH no servidor):**
   `htpasswd -c .htpasswd stream` (Cria o usuário 'stream' e pede a senha).

## 🩺 Manutenção Automática
- **01:00 às 05:00:** Período de resfriamento.
- **Check-up:** Notifica no Telegram apenas se houver problemas (Temp > 70°C, Disco Cheio ou Erro de HW).

---
Desenvolvido por Bruno Grange.
