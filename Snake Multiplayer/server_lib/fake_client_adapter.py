import asyncio
import threading
from collections import deque
from typing import Optional, Dict, Any, Deque

from server_lib.net_fake import FakeServer

class Client:
    def __init__(self,power_ups) -> None:
        self.power_ups = power_ups

    def receive_now(self) -> Optional[str]:
        pass

    def process_messages(self):
        msg = self.receive_now()
        if msg is None:
            return
        if msg.startswith("POWER_UP_SPAWNED"):
            _,pw_id, x, y, pw_type = msg.split()
            self.power_ups.add(pw_id,x,y,pw_type)
    


class FakeClient(Client):
    """
    Adapter mit eigenem asyncio-Loop im Hintergrund-Thread.
    - Startet beim Erzeugen einen Event-Loop in thread.
    - Alle async-Calls werden via run_coroutine_threadsafe in diesen Loop gescheduled.
    - receive_now bleibt non-blocking für die Pygame-Loop.
    """
    def __init__(self, power_ups,version: str = "1.0", name: str = "player"):
        super().__init__(power_ups)
        self._version = version
        self._name = name
        self._server = FakeServer(version=version)
        self._inbox: Deque[str] = deque()

        # Bridge: FakeServer -> Inbox
        self._server.on_message(self._on_line)

        # Eigener Event-Loop im Hintergrund-Thread
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, name="FakeClientLoop", daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _on_line(self, line: str) -> None:
        self._inbox.append(line)

    # Öffentliche, sync-kompatible API

    def connect(self, name: Optional[str] = None, version: Optional[str] = None) -> None:
        name = name or self._name
        version = version or self._version
        asyncio.run_coroutine_threadsafe(
            self._server.connect(name=name, version=version),
            self._loop
        )

    def receive_now(self) -> Optional[str]:
        return self._inbox.popleft() if self._inbox else None

    def send_pos(self, pos: Dict[str, Any]) -> None:
        asyncio.run_coroutine_threadsafe(
            self._server.send_pos(pos),
            self._loop
        )

    def power_up_collected(self, pw_id: int) -> None:
        asyncio.run_coroutine_threadsafe(
            self._server.power_up_collected(pw_id),
            self._loop
        )

    def close(self) -> None:
        # Server-Task beenden
        fut = asyncio.run_coroutine_threadsafe(self._server.close(), self._loop)
        try:
            fut.result(timeout=1.0)
        except Exception:
            pass
        # Loop stoppen
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=1.0)
