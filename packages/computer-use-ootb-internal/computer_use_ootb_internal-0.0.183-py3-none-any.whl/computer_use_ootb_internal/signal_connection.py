# Helper script to signal guard service about user connection
# Save as e.g., ootb_lite_pypi/ootb_lite_pypi/src/computer_use_ootb_internal/signal_connection.py
import sys
import requests
import logging
import os
import pathlib

# Basic logging for the script itself
LOG_DIR = pathlib.Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / "OOTBGuardService" / "SignalLogs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "signal_connection.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

GUARD_SERVICE_URL = "http://localhost:14000/internal/user_connected"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Username argument missing.")
        sys.exit(1)

    username = sys.argv[1]
    logging.info(f"Signaling connection for user: {username}")

    payload = {"username": username}

    try:
        response = requests.post(GUARD_SERVICE_URL, json=payload, timeout=10)
        response.raise_for_status()
        logging.info(f"Successfully signaled connection for user {username}. Status: {response.status_code}")
        sys.exit(0)
    except requests.exceptions.ConnectionError:
        logging.error(f"Connection refused when trying to signal for user {username}. Guard service might not be running or accessible.")
        sys.exit(2)
    except requests.exceptions.Timeout:
        logging.error(f"Timeout when trying to signal for user {username}.")
        sys.exit(3)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error signaling connection for user {username}: {e}")
        sys.exit(4)
    except Exception as e:
        logging.error(f"Unexpected error for user {username}: {e}")
        sys.exit(5) 