# windows_paths.py
from __future__ import annotations
import json
import os
from pathlib import Path

VENDOR = "YourName"
APP    = "SnakeLAN"

DEFAULT_SETTINGS = {
    "volume": 0.7,
    "fullscreen": False,
    "tickrate": 60,
    "player_color": "p1",
}


def win_appdata() -> Path:
    appdata = os.environ.get("APPDATA")  # e.g. C:\Users\<User>\AppData\Roaming
    if not appdata:
        # Fallback: HOME + Roaming path (sehr selten nötig, z. B. bei Spezialumgebungen)
        home = Path.home()
        appdata = str(home / "AppData" / "Roaming")
    return Path(appdata)

def win_localappdata() -> Path:
    local = os.environ.get("LOCALAPPDATA")  # e.g. C:\Users\<User>\AppData\Local
    if not local:
        home = Path.home()
        local = str(home / "AppData" / "Local")
    return Path(local)

def config_dir() -> Path:
    return win_appdata() / VENDOR / APP

def data_dir() -> Path:
    return win_localappdata() / VENDOR / APP

def cache_dir() -> Path:
    return data_dir() / "Cache"

def log_dir() -> Path:
    return data_dir() / "Logs"

def ensure_dirs() -> None:
    for p in (config_dir(), data_dir(), cache_dir(), log_dir()):
        p.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = config_dir() / "settings.json"

def load_settings() -> dict:
    ensure_dirs()
    if SETTINGS_FILE.exists():
        try:
            return {**DEFAULT_SETTINGS, **json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))}
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict) -> None:
    ensure_dirs()
    tmp: Path = SETTINGS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    tmp.replace(SETTINGS_FILE)  # atomarer Austausch minimiert Korruption
