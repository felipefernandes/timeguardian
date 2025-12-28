#!/usr/bin/env python3

import os
import json
import time
import subprocess
import logging
from datetime import datetime
import pwd

# ============ CONFIGURAÇÕES ==============

USER = os.getenv("TARGET_USER") or "gardenia"   # Edite aqui ou exporte ao iniciar o serviço
CONFIG_PATH = f"/etc/guardiantime/config.json"     # Arquivo com políticas
LOG_PATH = "/var/log/guardiantime.log"
STATE_PATH = "/var/lib/guardiantime/state.json"   # Para persistir tempo

# ============ LOGGING ====================
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# ============ AUXILIARES =================

def get_user_uid(user):
    try:
        return pwd.getpwnam(user).pw_uid
    except Exception:
        return 1000  # fallback, mas avisa no log

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
    uid = get_user_uid(USER)
    dbus_address = f"unix:path=/run/user/{uid}/bus"
    proc_env = os.environ.copy()
    proc_env['DISPLAY'] = ':0'
    proc_env['DBUS_SESSION_BUS_ADDRESS'] = dbus_address
    try:
        subprocess.run([
            "sudo", "-u", USER, "notify-send", "GuardianTime", message
        ], env=proc_env)
    except Exception as e:
        logging.error(f"Notify error: {e}")

# ============ MAIN =======================

def load_state():
    try:
        with open(STATE_PATH, "r") as f:
            data = json.load(f)
        if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
            return data.get('used_today', 0)
        return 0
    except Exception:
        return 0

def save_state(used_today):
    try:
        with open(STATE_PATH, "w") as f:
            json.dump({
                'used_today': used_today,
                'date': datetime.now().strftime('%Y-%m-%d')
            }, f)
    except Exception as e:
        logging.error(f"Erro ao salvar state.json: {e}")

def main():
    used_today = load_state()
    notified_5 = False
    notified_2 = False

    while True:
        now = datetime.now()
        config = load_limits()

        # Verifica janela de uso
        start, end = [datetime.strptime(t, "%H:%M").time() for t in config["allowed_window"]]
        if not (start <= now.time() <= end):
            logging.info("Fora do horário permitido. Encerrando sessão...")
            send_notify("Tempo encerrado! Fora do horário permitido.")
            subprocess.run(["loginctl", "terminate-user", USER])
            break

        idle_sec = get_idle_time()
        if idle_sec < 300:
            used_today += 1
            save_state(used_today)

        minutos_restantes = config["daily_limit_minutes"] - used_today

        if minutos_restantes <= 5 and not notified_5 and minutos_restantes > 0:
            send_notify("Restam apenas 5 minutos de uso!")
            notified_5 = True
        if minutos_restantes <= 2 and not notified_2 and minutos_restantes > 0:
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