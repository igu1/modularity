                                                      

import os, json
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional

@dataclass
class DbConfig:
    url: str = "sqlite:///system.db"
    echo: bool = False

@dataclass
class LogConfig:
    level: str = "INFO"
    dir: str = "logs"

@dataclass
class SvrConfig:
    host: str = "localhost"
    port: int = 8080
    debug: bool = False

@dataclass
class AuthConfig:
    jwt_secret: str = "your-secret-key"
    access_token_expiry: int = 3600  # seconds (1 hour)
    refresh_token_expiry: int = 604800  # seconds (7 days)

@dataclass
class Config:
    db: DbConfig = field(default_factory=DbConfig)
    log: LogConfig = field(default_factory=LogConfig)
    svr: SvrConfig = field(default_factory=SvrConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)

class ConfigManager:
    def __init__(self, path: str = "config.json"):
        self.path, self.cfg = path, Config()
        self.load()

    def _update(self, target, data):
        for k, v in data.items():
            if hasattr(target, k):
                t = getattr(target, k)
                if hasattr(t, '__dataclass_fields__') and isinstance(v, dict): self._update(t, v)
                else: setattr(target, k, v)

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f: self._update(self.cfg, json.load(f))
            except: pass
        self.cfg.db.url = os.getenv("DB_URL", self.cfg.db.url)
        self.cfg.svr.port = int(os.getenv("PORT", self.cfg.svr.port))

    def save(self):
        with open(self.path, 'w') as f: json.dump(asdict(self.cfg), f, indent=2)

_mgr = ConfigManager()
def get_config() -> Config: return _mgr.cfg
def get_config_manager() -> ConfigManager: return _mgr
