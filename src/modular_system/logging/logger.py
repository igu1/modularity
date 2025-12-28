import logging, os, sys
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler

class CoreLogger:
    def __init__(self, log_dir: str = 'logs', level: str = 'INFO'):
        self.log_dir, self.level = log_dir, getattr(logging, level.upper(), logging.INFO)
        self._loggers, self._handlers = {}, {}
        os.makedirs(self.log_dir, exist_ok=True)
        self._setup_defaults()

    def _setup_defaults(self):
        fmt = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        fh = RotatingFileHandler(os.path.join(self.log_dir, 'app.log'), maxBytes=10*1024*1024, backupCount=5)
        fh.setFormatter(fmt)
        self._handlers.update({'console': ch, 'file': fh})

    def get_logger(self, name: str, cls: str = None) -> logging.Logger:
        ln = f"mod.{name}" + (f".{cls}" if cls else "")
        if ln not in self._loggers:
            l = logging.getLogger(ln)
            l.setLevel(self.level)
            if not l.handlers:
                h = RotatingFileHandler(os.path.join(self.log_dir, f'{name}.log'), maxBytes=5*1024*1024, backupCount=3)
                h.setFormatter(logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s'))
                l.addHandler(h)
                l.addHandler(self._handlers['console'])
                l.addHandler(self._handlers['file'])
                l.propagate = False
            self._loggers[ln] = l
        return self._loggers[ln]

    def log(self, mod: str, msg: str, lvl: str = 'info', cls: str = None, extra: Dict = None):
        l = self.get_logger(mod, cls)
        l.log(getattr(logging, lvl.upper(), logging.INFO), msg, extra=extra or {})
        if lvl.lower() in ['error', 'critical', 'warning'] or self.level <= logging.INFO:
            print(f"[{mod.upper()}] {lvl.upper()}: {msg}", file=sys.stderr if lvl.lower() in ['error', 'critical'] else sys.stdout)

    def log_event(self, data: Dict):
        self.log(data.get('src', 'sys'), f"EVT: {data.get('name')} | {data.get('data', {})}")

    def log_error(self, mod: str, msg: str, ex: Exception = None):
        if ex: msg += f" - {type(ex).__name__}: {ex}"
        self.log(mod, msg, 'error')

core_logger = CoreLogger()
def get_logger(name: str, cls: str = None): return core_logger.get_logger(name, cls)
def log_event(data: Dict): core_logger.log_event(data)
def log_error(mod: str, msg: str, ex: Exception = None): core_logger.log_error(mod, msg, ex)
