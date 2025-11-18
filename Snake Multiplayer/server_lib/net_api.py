from typing import Callable, Optional, Dict, Any
import abc

MessageCallback = Callable[[str], None]

class GameNet(abc.ABC):
    """Abstrakte Netz-API für Snake-Game-Clients."""
    def __init__(self) -> None:
        self._cb: Optional[MessageCallback] = None

    def on_message(self, cb: MessageCallback) -> None:
        """Registriert einen Callback, der komplette Zeilen (inkl. \n) erhält."""
        self._cb = cb

    def _emit(self, line: str) -> None:
        if self._cb:
            self._cb(line)

    @abc.abstractmethod
    async def connect(self, name: str, version: str) -> None:
        ...

    @abc.abstractmethod
    async def send_pos(self, pos: Dict[str, Any]) -> None:
        ...

    @abc.abstractmethod
    async def power_up_collected(self, pw_id: int) -> None:
        ...

    @abc.abstractmethod
    async def close(self) -> None:
        ...


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
    
