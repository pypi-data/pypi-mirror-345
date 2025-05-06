import threading
import time
import requests
import sys
import traceback
from urllib.parse import urlencode

class Logger:
    def __init__(self, app_id: str, api_key: str, api_url: str = "https://api.logger-simple.com/python/"):
        if not app_id or not api_key:
            raise ValueError("app_id and api_key are required.")
        self.app_id = app_id
        self.api_key = api_key
        self.api_url = api_url.rstrip("/") + "/"
        self._hb_thread = None
        self._hb_stop = threading.Event()
        self._start_heartbeat(interval=5.0)
        self._setup_crash_logging()

    def _build_url(self, params: dict) -> str:
        params.update({
            "app_id": self.app_id,
            "api_key": self.api_key
        })
        return f"{self.api_url}?{urlencode(params)}"

    def send_log(self, log_level: str, message: str) -> dict:
        url = self._build_url({
            "action": "logger",
            "request": "new_log",
            "logLevel": log_level,
            "message": message
        })
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("success"):
            return data["log"]
        else:
            err = data.get("error", f"API error: {data}")
            raise RuntimeError(err)

    def log_success(self, message: str) -> dict:
        return self.send_log("success", message)

    def log_info(self, message: str) -> dict:
        return self.send_log("info", message)

    def log_error(self, message: str) -> dict:
        return self.send_log("error", message)

    def log_critical(self, message: str) -> dict:
        return self.send_log("critical", message)

    def _heartbeat_loop(self, interval: float):
        while not self._hb_stop.wait(interval):
            try:
                self.send_heartbeat()
            except Exception:
                pass

    def _start_heartbeat(self, interval: float):
        if self._hb_thread and self._hb_thread.is_alive():
            return
        self._hb_thread = threading.Thread(
            target=self._heartbeat_loop, args=(interval,), daemon=True
        )
        self._hb_thread.start()

    def send_heartbeat(self) -> dict:
        url = self._build_url({
            "action": "logger",
            "request": "heartbeat",
        })
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("success"):
            return data
        else:
            err = data.get("error", f"API heartbeat error: {data}")
            raise RuntimeError(err)

    def stop_heartbeat(self):
        self._hb_stop.set()
        if self._hb_thread:
            self._hb_thread.join(timeout=1)

    def _setup_crash_logging(self):
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            stack = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            try:
                self.log_critical(f"CRITICAL: Uncaught exception\n{stack}")
            except Exception:
                pass
            sys.exit(1)

        sys.excepthook = handle_exception
