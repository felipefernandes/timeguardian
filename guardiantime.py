#!/usr/bin/env python3

import os
import json
import time
import subprocess
import logging
from datetime import datetime

# ============ CONFIGURAÇÕES ==============

USER = os.getenv("TARGET_USER") or "gardenia"   # Edite aqui ou exporte ao iniciar o serviço
CONFIG_PATH = f"/etc/guardiantime/config.json"     # Arquivo com políticas
LOG_PATH = "/var/log/guardiantime.log"

# ============ LOGGING ====================
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# ============ AUXILIARES =================

def get_idle_time():
    try:
        ms = int(subprocess.check_output(['xprintidle']))
        return ms // 1000
    except Exception as e:
        logging.error(f"xprintidle error: {e}")
        return 0

def load_limits():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Config error: {e}")
        return {
            "allowed_window": ["08:00", "22:00"],
            "daily_limit_minutes": 120
        }

def send_notify(message):
    subprocess.run([
        "sudo", "-u", USER, "DISPLAY=:0", "DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus",
        "notify-send", "GuardianTime", message
    ])

# ============ MAIN =======================

def main():
    used_today = 0  # minutos usados hoje (use arquivo se quiser persistência)
    notified_5 = False
    notified_2 = False

    while True:
        now = datetime.now()
        config = load_limits()

        # Verifica janela de uso
        start, end = [datetime.strptime(t, "%H:%M").time() for t in config["allowed_window"]]
        if not (start <= now.time() <= end):
            logging.info("Fora do horário permitido.")
            time.sleep(60)
            continue

        idle_sec = get_idle_time()
        if idle_sec < 300:
            used_today += 1

        minutos_restantes = config["daily_limit_minutes"] - used_today

        if minutos_restantes <= 5 and not notified_5:
            send_notify("Restam apenas 5 minutos de uso!")
            notified_5 = True
        if minutos_restantes <= 2 and not notified_2:
            send_notify("Restam apenas 2 minutos de uso!")
            notified_2 = True

        if minutos_restantes <= 0:
            logging.info("Tempo esgotado! Encerrando sessão...")
            subprocess.run(["loginctl", "terminate-user", USER])
            break

        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Erro não tratado no GuardianTime.")