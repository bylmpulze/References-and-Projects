import asyncio
import json
import random
import time
from typing import Dict, Any, Optional, List, Tuple

from .net_api import GameNet

GRID_W = 28
GRID_H = 28



class FakeServer(GameNet):
    """
    In-Process „Server“, der Netzwerk nur simuliert:
    - WELCOME <id>
    - POWER_UP_SPAWNED <pw_id> <x> <y> <type>
    - POWER_UP_REMOVED <pw_id>
    - Loopback: "<id>: POS {json}"
    """

    def __init__(
        self, version: str = "1.0", powerup_spawn_interval_ms: int = 1000
    ) -> None:
        super().__init__()
        self.version = version
        self._connected = False
        self._task: Optional[asyncio.Task] = None
        self._client_id = 1
        self._power_ups: Dict[int, Dict[str, Any]] = {
            1: {"x": 6, "y": 6, "pw_type": "speed_boost_x2"}
        }
        self._next_pw_id = 2
        self._last_spawn_ms = self._now_ms()
        self._powerup_spawn_interval_ms = powerup_spawn_interval_ms
        self.food_locations: List[Tuple[int, int]] = []

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    async def connect(self, name: str, version: str) -> None:
        # Version prüfen; im Fake-Fall nur simulierte Ablehnung möglich.
        if version != self.version:
            self._emit("REJECTED Client_Server_Version_Missmatch\n")
            return
        self._connected = True
        self._emit(f"WELCOME {self._client_id}\n")
        # Bereits existierende Powerups senden (Start: keine).
        for pw_id, pu in self._power_ups.items():
            self._emit(
                f"POWER_UP_SPAWNED {pw_id} {pu['x']} {pu['y']} {pu['pw_type']}\n"
            )
        self._task = asyncio.create_task(self._loop())

    async def _loop(self) -> None:
        try:
            while self._connected:
                await asyncio.sleep(0.005)
                await self._maybe_spawn_powerup()
        except asyncio.CancelledError:
            return

    async def _maybe_spawn_powerup(self) -> None:
        now = self._now_ms()
        if (
            not self._power_ups
            and now - self._last_spawn_ms >= self._powerup_spawn_interval_ms
        ):
            await self._spawn_one()

    async def _spawn_one(self) -> None:
        x = random.randint(1, GRID_W - 1)
        y = random.randint(1, GRID_H - 1)
        pw_type = random.choice(
            [
                "speed_boost_x2",
                # "speed_half",
                # "extra_life",
                # "powerup_drunk",
                # "powerup_magnet",
            ]
        )
        pw_id = self._next_pw_id
        self._next_pw_id += 1
        self._power_ups[pw_id] = {"x": x, "y": y, "pw_type": pw_type}
        self._last_spawn_ms = self._now_ms()
        self._emit(f"POWER_UP_SPAWNED {pw_id} {x} {y} {pw_type}\n")

    async def send_pos(self, pos: Dict[str, Any]) -> None:
        # Simuliere Broadcast als Loopback (als ob von anderem Spieler gesehen).
        line = f"{self._client_id}: POS {json.dumps(pos, separators=(',', ':'))}\n"
        self._emit(line)

    async def power_up_collected(self, pw_id: int) -> None:
        if pw_id in self._power_ups:
            del self._power_ups[pw_id]
            self._emit(f"POWER_UP_REMOVED {pw_id}\n")
            print("POWER_UP_REMOVED")
            # Optional direkt neues Powerup spawnen:
            await self._spawn_one()

    async def close(self) -> None:
        self._connected = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
