from __future__ import annotations
import json
import os
from pathlib import Path

class AppSettings:
    DEFAULTS = {
        "volume": 0.7,
        "fullscreen": False,
        "tickrate": 60,
        "player_color": "p1",
        "multiplayer_ip": "127.0.0.1",
        "default_name": "Spieler1",
        "avatar_path": None,
        "language": "de",
    }

    def __init__(self, vendor="YourName", app="SnakeLAN"):
        self.vendor = vendor
        self.app = app

        self._settings = self._load()


    @property
    def appdata(self) -> Path:
        return Path(os.environ.get("APPDATA") or (Path.home() / "AppData/Roaming"))

    @property
    def localappdata(self) -> Path:
        return Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData/Local"))

    @property
    def config_dir(self) -> Path:
        return self.appdata / self.vendor / self.app

    @property
    def data_dir(self) -> Path:
        return self.localappdata / self.vendor / self.app

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "Cache"

    @property
    def log_dir(self) -> Path:
        return self.data_dir / "Logs"

    @property
    def settings_file(self) -> Path:
        return self.config_dir / "settings.json"

    def ensure_dirs(self):
        for p in (self.config_dir, self.data_dir, self.cache_dir, self.log_dir):
            p.mkdir(parents=True, exist_ok=True)

    # -------------------- LOAD / SAVE --------------------

    def _load(self) -> dict:
        self.ensure_dirs()
        if self.settings_file.exists():
            try:
                data = json.loads(self.settings_file.read_text(encoding="utf-8"))
                return {**self.DEFAULTS, **data}
            except Exception:
                return self.DEFAULTS.copy()
        return self.DEFAULTS.copy()

    def save(self):
        self.ensure_dirs()
        tmp = self.settings_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._settings, indent=2), encoding="utf-8")
        tmp.replace(self.settings_file)


    def __getitem__(self, key):
        return self._settings.get(key)

    def __setitem__(self, key, value):
        self._settings[key] = value
        self.save()

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value
        self.save()
    @property
    def volume(self):
        return self._settings["volume"]

    @volume.setter
    def volume(self, value):
        self._settings["volume"] = value
        self.save()


if __name__ == "__main__":
    settings = AppSettings()
    print("Config dir:", settings.config_dir)
    print("Data dir:", settings.data_dir)
    print("Cache dir:", settings.cache_dir)
    print("Log dir:", settings.log_dir)
    print("Settings file:", settings.settings_file)

    print("Current volume:", settings.volume)
    settings.volume = 0.5
    print("Updated volume:", settings.volume)