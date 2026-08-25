import signal
import sys
import logging
import pyperclip
import threading
from exceptions import InvalidKiller
from vault import logout

logger = logging.getLogger(__name__)

class GracefulKiller:
    kill_now = False
    def __init__(self, session_key):
        self.session_key = session_key
        try:
            signal.signal(signal.SIGINT, self.exit_gracefully)
            signal.signal(signal.SIGTERM, self.exit_gracefully)
        except InvalidKiller as e:
            print(f"Error: {e}")
            print(f"Archivo: {e.file_name}")
            print(f"Función: {e.func_name}")
            print(f"Línea: {e.line}")
            print(f"Código fuente: {e.source_line}")
            print(f"Info: {e.info}")
            logger.error("Falló el proceso de cancelación.")

    def exit_gracefully(self, signum, frame):
        logout(self.session_key)
        self.kill_now = True
        pyperclip.copy("")
        sys.exit(0)

class VaultLockTimer:
    def __init__(self, timeout_minutes: int, on_lock):
        self.timeout = timeout_minutes * 60
        self.on_lock = on_lock
        self._timer = None
        self._lock = threading.Lock()

    def touch(self):
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.timeout, self.on_lock)
            self._timer.daemon = True
            self._timer.start()
