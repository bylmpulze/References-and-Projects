import asyncio
import random
import time
from typing import Dict, Optional

GRID_W = 28
GRID_H = 28


class SocketBroadcastServer:
    """
    Asyncio-Streams-basierter Server:
    - Handshake: HELLO <name> <version>  -> WELCOME <id>
    - Client sendet: POS {json}, POWER_UP_COLLECTED <id>
    - Server broadcastet:
        "<id>: POS {json}"
        "POWER_UP_SPAWNED <pw_id> <x> <y> <type>"
        "POWER_UP_REMOVED <pw_id>"
    """

    def __init__(
        self,
        version: str = "1.0",
        powerup_spawn_interval_ms: int = 8000,
        max_line: int = 8192,
        handshake_timeout: float = 5.0,
    ) -> None:
        self.version = version
        self.max_line = max_line
        self.handshake_timeout = handshake_timeout

        self.clients: set[asyncio.StreamWriter] = set()
        self.client_meta: dict[asyncio.StreamWriter, dict] = {}
        self._next_id = 1

        self.available_powerups = [
            "speed_boost_x2",
            "speed_half",
            "extra_life",
            "powerup_drunk",
            "powerup_magnet",
        ]
        self.powerup_spawn_interval_ms = powerup_spawn_interval_ms
        self._last_powerup_spawn_ms = self._now_ms()
        self._next_powerup_id = 1
        self.power_ups: Dict[int, Dict] = {}

        self._periodic_task: Optional[asyncio.Task] = None

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    async def _readline_capped(self, reader: asyncio.StreamReader) -> bytes:
        line = await reader.readline()
        if not line:
            return line
        if len(line) > self.max_line:
            raise ValueError("line too long")
        return line

    async def _do_handshake(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> dict:
        try:
            line = await asyncio.wait_for(
                self._readline_capped(reader), timeout=self.handshake_timeout
            )
        except asyncio.TimeoutError:
            raise RuntimeError("handshake timeout")
        if not line:
            raise RuntimeError("client closed before handshake")

        text = line.decode("utf-8", errors="strict").strip()
        parts = text.split()
        if len(parts) != 3 or parts[0] != "HELLO":
            raise RuntimeError("invalid handshake verb")
        _, name, client_version = parts

        if client_version != self.version:
            writer.write(b"REJECTED Client_Server_Version_Missmatch\n")
            await writer.drain()
            raise ValueError("Client Server Version Missmatch")

        cid = self._next_id
        self._next_id += 1

        writer.write(f"WELCOME {cid}\n".encode("utf-8"))
        await writer.drain()
        print(f"WELCOME {cid}")
        return {"id": cid, "name": name}

    async def _periodic_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(0.25)
                await self._maybe_spawn_powerup()
        except asyncio.CancelledError:
            return

    async def start_periodic(self) -> None:
        if self._periodic_task is None or self._periodic_task.done():
            self._periodic_task = asyncio.create_task(self._periodic_loop())

    async def stop_periodic(self) -> None:
        if self._periodic_task and not self._periodic_task.done():
            self._periodic_task.cancel()
            try:
                await self._periodic_task
            except asyncio.CancelledError:
                pass
        self._periodic_task = None

    async def _maybe_spawn_powerup(self) -> None:
        now = self._now_ms()
        if not self.power_ups and (
            now - self._last_powerup_spawn_ms >= self.powerup_spawn_interval_ms
        ):
            await self._spawn_one_powerup_if_none()

    async def _spawn_one_powerup_if_none(self) -> None:
        if self.power_ups:
            return
        x = random.randint(0, GRID_W - 1)
        y = random.randint(0, GRID_H - 1)
        pw_type = random.choice(self.available_powerups)
        pw_id = self._next_powerup_id
        self._next_powerup_id += 1

        self.power_ups[pw_id] = {"x": x, "y": y, "pw_type": pw_type}
        self._last_powerup_spawn_ms = self._now_ms()

        await self.broadcast(
            f"POWER_UP_SPAWNED {pw_id} {x} {y} {pw_type}\n".encode("utf-8")
        )

    async def broadcast(
        self, data: bytes, exclude: Optional[asyncio.StreamWriter] = None
    ) -> None:
        dead: list[asyncio.StreamWriter] = []
        for w in list(self.clients):
            if exclude is not None and w is exclude:
                continue
            try:
                w.write(data)
            except Exception:
                dead.append(w)
        await asyncio.gather(
            *(
                w.drain()
                for w in list(self.clients)
                if (exclude is None or w is not exclude) and w not in dead
            ),
            return_exceptions=True,
        )
        for w in dead:
            if w in self.clients:
                self.clients.discard(w)
            self.client_meta.pop(w, None)
            try:
                w.close()
                await w.wait_closed()
            except Exception:
                pass

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            meta = await self._do_handshake(reader, writer)
        except Exception:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            return

        self.clients.add(writer)
        self.client_meta[writer] = meta
        await self.start_periodic()

        # Sync bestehende Powerups
        for pw_id, pu in self.power_ups.items():
            writer.write(
                f"POWER_UP_SPAWNED {pw_id} {pu['x']} {pu['y']} {pu['pw_type']}\n".encode(
                    "utf-8"
                )
            )
        await writer.drain()

        try:
            while True:
                await self._maybe_spawn_powerup()

                try:
                    line = await self._readline_capped(reader)
                except ValueError:
                    break

                if not line:
                    break

                text = line.decode("utf-8", errors="strict").strip()

                if text.startswith("POWER_UP_COLLECTED"):
                    parts = text.split()
                    try:
                        pw_id = int(parts[1])
                    except Exception:
                        pw_id = None
                    if pw_id is not None and pw_id in self.power_ups:
                        del self.power_ups[pw_id]
                        await self.broadcast(
                            f"POWER_UP_REMOVED {pw_id}\n".encode("utf-8")
                        )
                        await self._spawn_one_powerup_if_none()
                    continue

                if text.startswith("POS"):
                    outbound = f"{meta['id']}: {text}\n".encode("utf-8")
                    await self.broadcast(outbound, exclude=writer)
                    continue

        except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
            pass
        finally:
            if writer in self.clients:
                self.clients.discard(writer)
            self.client_meta.pop(writer, None)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

            if not self.clients:
                await self.stop_periodic()


async def run_server(
    host: str = "127.0.0.1", port: int = 50007, version: str = "1.0"
) -> None:
    print(f"Server running at {host} {port}")
    logic = SocketBroadcastServer(version=version)
    server = await asyncio.start_server(logic.handle_client, host, port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(run_server())
