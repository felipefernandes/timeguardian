# TimeGuardian

TimeGuardian (GuardianTime) é um sistema de controle de tempo de uso para Ubuntu desenvolvido para ambientes de alta segurança, mesmo onde o usuário-alvo é administrador (sudoer). Seu objetivo é garantir limites de uso diário, mesmo que o usuário tenha privilégios elevados, encerrando a sessão quando o tempo acabar.

## Como funciona

- **Execução como serviço:** Roda como systemd (root), conferindo resiliência e integridade.
- **Monitoramento de tempo real:** A cada 60 segundos, checa:
  - Se está dentro da janela de horários permitida (`allowed_window`).
  - Se o usuário está ativo (idle < 5 min usando `xprintidle`).
  - Registra tempo usado no dia e avisa com `notify-send` ao restar 5 ou 2 minutos.
  - Encerra a sessão com `loginctl terminate-user` ao atingir o limite.
- **Configuração e logs:**
  - Configurações em `/etc/guardiantime/config.json` (exemplo abaixo).
  - Logs em `/var/log/guardiantime.log`.

## Arquivo de configuração (`/etc/guardiantime/config.json`)

Sugestão para permitir uso **todos os dias entre 09:00 e 19:00**, até 10 horas diárias:

```json
{
  "allowed_window": ["09:00", "19:00"],
  "daily_limit_minutes": 600
}
```

## Dica: Qual nome de usuário utilizar?

Use exatamente o nome do usuário conforme usado no login (e retornado pelo comando `whoami` ou na coluna da esquerda do comando `who`). Exemplo de modificação da variável `TARGET_USER`:

```ini
# No arquivo guardiantime.service
Environment=TARGET_USER=meunome
```

## Instalação

Prefira o instalador automático. Necessário rodar como root (ou com sudo):

```bash
chmod +x install_guardiantime.sh
sudo ./install_guardiantime.sh
```

**Opcional**: Para instalar já usando o login correto:
```bash
export TARGET_USER=meunome
sudo ./install_guardiantime.sh
```

Isso realiza:
- Instalação de dependências (`python3`, `xprintidle`, etc).
- Cópia do script, config e .service para os diretórios adequados.
- Ajuste automático de permissões.
- Configuração do serviço systemd.

## Gerenciamento

- Ativar Manualmente:
  ```
  sudo systemctl daemon-reload
  sudo systemctl enable guardiantime
  sudo systemctl restart guardiantime
  ```
- Ver logs em tempo real:
  ```
  sudo tail -f /var/log/guardiantime.log
  ```
- Para mudar o usuário alvo, edite o `Environment=TARGET_USER=...` em `/etc/systemd/system/guardiantime.service`, depois:
  ```
  sudo systemctl daemon-reload
  sudo systemctl restart guardiantime
  ```

---

Dúvidas, ajustes de configuração por dia da semana ou integração com webhooks? Fale comigo!
