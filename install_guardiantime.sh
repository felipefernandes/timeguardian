#!/usr/bin/env bash
set -e

# =============== CONFIGURÁVEIS ==================
SRC_DIR="$(pwd)"  # Diretório atual com os arquivos
TARGET_USER="${TARGET_USER:-usuarioalvo}" # Você pode definir export TARGET_USER=meuuser antes
# ===============================================

echo "Instalando dependências do Ubuntu (será solicitado sudo)..."
sudo apt update
sudo apt install -y python3 python3-pip xprintidle libnotify-bin

echo "Preparando diretórios e arquivos de configuração..."
sudo mkdir -p /etc/guardiantime

echo "Copiando arquivos do GuardianTime..."
sudo cp "$SRC_DIR/guardiantime.py" /usr/local/bin/
sudo chmod +x /usr/local/bin/guardiantime.py
sudo cp "$SRC_DIR/config.json" /etc/guardiantime/
sudo cp "$SRC_DIR/guardiantime.service" /etc/systemd/system/

echo "Configurando usuário alvo: $TARGET_USER..."
sudo sed -i "s|^Environment=TARGET_USER=.*|Environment=TARGET_USER=${TARGET_USER}|" /etc/systemd/system/guardiantime.service

echo "Ajustando permissões do log..."
sudo touch /var/log/guardiantime.log
sudo chown root:root /var/log/guardiantime.log

echo "Habilitando e iniciando serviço..."
sudo systemctl daemon-reload
sudo systemctl enable guardiantime
sudo systemctl restart guardiantime

echo ""
echo "GuardianTime instalado com sucesso!"
echo "Verifique logs com: sudo tail -f /var/log/guardiantime.log"
echo ""
echo "Caso precise mudar o usuário alvo, edite Environment=TARGET_USER=XXXX em /etc/systemd/system/guardiantime.service e rode 'sudo systemctl daemon-reload && sudo systemctl restart guardiantime'"