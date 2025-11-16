import asyncio
from collections import deque
from typing import Optional, Dict, Any, Deque, Callable

# Importiere deine FakeServer-Implementierung
# Falls deine Datei net_fake.py in game/net_fake.py liegt:
from game.server.net_fake import FakeServer


class FakeClient:
    """
    Adapter, der FakeServer so kapselt, dass er dieselbe API wie dein echter Client hat:
    - connect(name, version)
    - receive_now() -> Optional[str]
    - send_pos(pos_dict)
    - power_up_collected(pw_id)
    - close()
    Intern nutzt er eine Inbox-Queue, die der FakeServer über on_message füllt.
    """
    def __init__(self, version: str = "1.0", name: str = "player"):
        self._version = version
        self._name = name
        self._server = FakeServer(version=version)
        self._inbox: Deque[str] = deque()
        # Bridge: Server liefert Zeilen, die in die Inbox gepusht werden
        self._server.on_message(self._on_line)

    def _on_line(self, line: str) -> None:
        # line enthält bereits das '\n' aus dem Server
        self._inbox.append(line)

    # Öffentliche API – synchron aufrufbar aus der Pygame-Loop

    def connect(self, name: Optional[str] = None, version: Optional[str] = None) -> None:
        """
        Startet den FakeServer-Connect asynchron, ohne die Pygame-Loop zu blockieren.
        """
        name = name or self._name
        version = version or self._version
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._server.connect(name=name, version=version))
        except RuntimeError:
            # Kein laufender Loop: kurzzeitig einen Event-Loop für den Connect ausführen
            asyncio.run(self._server.connect(name=name, version=version))

    def receive_now(self) -> Optional[str]:
        """
        Nicht-blockierend: Gibt sofort die nächste volle Zeile zurück oder None.
        """
        return self._inbox.popleft() if self._inbox else None

    def send_pos(self, pos: Dict[str, Any]) -> None:
        """
        Schickt Positions-Update in den FakeServer (asynchron).
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._server.send_pos(pos))
        except RuntimeError:
            asyncio.run(self._server.send_pos(pos))

    def power_up_collected(self, pw_id: int) -> None:
        """
        Meldet eingesammeltes Power-Up an den FakeServer (asynchron).
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._server.power_up_collected(pw_id))
        except RuntimeError:
            asyncio.run(self._server.power_up_collected(pw_id))

    def close(self) -> None:
        """
        Schließt den FakeServer (asynchron).
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._server.close())
        except RuntimeError:
            asyncio.run(self._server.close())
