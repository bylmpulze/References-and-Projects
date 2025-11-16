import asyncio
import json
from typing import Optional, Dict, Any

from .net_api import GameNet

class SocketClient(GameNet):
    """TCP-Client, der das gleiche Protokoll spricht und dieselbe API wie FakeServer bietet."""
    def __init__(self, host: str, port: int, version: str = "1.0") -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.version = version
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._task: Optional[asyncio.Task] = None

    async def connect(self, name: str, version: str) -> None:
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self.writer.write(f"HELLO {name} {version}\n".encode("utf-8"))
        await self.writer.drain()
        self._task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        assert self.reader is not None
        try:
            while True:
                line = await self.reader.readline()
                if not line:
                    break
                self._emit(line.decode("utf-8", errors="replace"))
        except asyncio.CancelledError:
            return

    async def send_pos(self, pos: Dict[str, Any]) -> None:
        if not self.writer:
            return
        self.writer.write(f"POS {json.dumps(pos, separators=(',', ':'))}\n".encode("utf-8"))
        await self.writer.drain()

    async def power_up_collected(self, pw_id: int) -> None:
        if not self.writer:
            return
        self.writer.write(f"POWER_UP_COLLECTED {pw_id}\n".encode("utf-8"))
        await self.writer.drain()

    async def close(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
            self.writer = None
            self.reader = None
