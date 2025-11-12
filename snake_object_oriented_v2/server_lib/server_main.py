import time
import socket
import asyncio
import json
import random
import server_functions
from typing import Dict, Tuple, List


HOST = "127.0.0.1"
PORT = 50007

GRID_W = 28
GRID_H = 28

class BroadcastServer:
    def __init__(self, max_line=8192, handshake_timeout=5.0, powerup_spawn_interval_ms=8000):
        self.clients: set[asyncio.StreamWriter] = set()
        self.client_meta: dict[asyncio.StreamWriter, dict] = {}
        self.snakes: List[Tuple[float, bytes]] = []
        self._next_id = 1
        self.max_line = max_line
        self.handshake_timeout = handshake_timeout

        # Food
        self.food_locations: list[Tuple[int, int]] = []
        self.food_locations.append(get_random_food_coords([], self.food_locations))

        # Powerups
        self.power_ups: Dict[int, Dict] = {}  # id -> {"x","y","pw_type"}
        self._next_powerup_id = 1
        self.available_powerups = [
            "speed_boost_x2", "speed_half", "extra_life", "powerup_drunk", "powerup_magnet"
        ]
        self.powerup_spawn_interval_ms = powerup_spawn_interval_ms
        self._last_powerup_spawn_ms = self._now_ms()

        self._periodic_task: asyncio.Task | None = None

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    async def start_periodic(self):
        if self._periodic_task is None or self._periodic_task.done():
            self._periodic_task = asyncio.create_task(self._periodic_powerup_spawner())

    async def stop_periodic(self):
        if self._periodic_task and not self._periodic_task.done():
            self._periodic_task.cancel()
            try:
                await self._periodic_task
            except Exception:
                pass
        self._periodic_task = None

    async def _readline_capped(self, reader: asyncio.StreamReader) -> bytes:
        line = await reader.readline()
        if not line:
            return line
        if len(line) > self.max_line:
            raise ValueError("line too long")
        return line

    async def _do_handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> dict:
        try:
            line = await asyncio.wait_for(self._readline_capped(reader), timeout=self.handshake_timeout)
        except asyncio.TimeoutError:
            raise RuntimeError("handshake timeout")
        if not line:
            raise RuntimeError("client closed before handshake")

        try:
            text = line.decode("utf-8", errors="strict").strip()
        except UnicodeDecodeError:
            raise RuntimeError("handshake not utf-8")

        if not text.startswith("HELLO"):
            raise RuntimeError("invalid handshake verb")
        _,name,client_version = text.split()
        if client_version != CONSTANTS.VERSION:
            writer.write("REJECTED Client_Server_Version_Missmatch\n".encode("utf-8"))
            await writer.drain()
            raise ValueError("Client Server Version Missmatch")
        

        cid = self._next_id
        self._next_id += 1

        writer.write(f"WELCOME {cid}\n".encode("utf-8"))
        await writer.drain()

        return {"id": cid, "name": name}

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")
        try:
            meta = await self._do_handshake(reader, writer)
        except Exception as e:
            try:
                writer.write(f"ERROR {str(e)}\n".encode("utf-8"))
                await writer.drain()
            except Exception as E:
                print(E)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as E:
                print(E)
            print(f"Handshake failed from {peer}: {e}")
            return

        self.clients.add(writer)
        self.client_meta[writer] = meta
        print(f"Client verbunden: {peer} as {meta}")

        await self.start_periodic()

        # Sync Food
        for x, y in self.food_locations:
            try:
                writer.write(f"FOOD_SPAWNED {x} {y}\n".encode("utf-8"))
            except Exception:
                pass
        await writer.drain()

        # Sync Powerups
        for pw_id, pu in self.power_ups.items():
            try:
                writer.write(
                    f"POWER_UP_SPAWNED {pw_id} {pu['x']} {pu['y']} {pu['pw_type']}\n".encode("utf-8")
                )
            except Exception:
                pass
        await writer.drain()

        try:
            while True:
                await self._maybe_spawn_powerup()

                try:
                    line = await self._readline_capped(reader)
                except ValueError:
                    print(f"Client sent oversized line: {peer}")
                    break

                if not line:
                    print(f"Client getrennt: {peer}")
                    break

                text = line.decode("utf-8", errors="strict").strip()

                if text.startswith("POWER_UP_COLLECTED"):
                    await self._handle_powerup_collected(text)
                    continue

                if text.startswith("DEAD SNAKE"):
                    await self.broadcast((text + "\n").encode("utf-8"), exclude=writer)
                    x, y = get_random_food_coords([], self.food_locations)
                    self.food_locations.append((x, y))
                    await self.broadcast(f"FOOD_SPAWNED {x} {y}\n".encode("utf-8"))
                    await self._spawn_one_powerup_if_none()
                    continue

                if text.startswith("FOOD_EATEN"):
                    x, y = get_random_food_coords([], self.food_locations)
                    self.food_locations.append((x, y))
                    await self.broadcast(f"FOOD_SPAWNED {x} {y}\n".encode("utf-8"))
                    await self._spawn_one_powerup_if_none()
                    continue

                now = time.time()
                self.snakes.append((now, line))
                prefix = f"{meta['id']}: ".encode("utf-8")
                outbound = prefix + line
                await self.broadcast(outbound, exclude=writer)
        except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
            print(f"[DISCONNECT] {meta['name']} (ID={meta['id']}) - connection lost")
            await self.broadcast(
                f"PLAYER_LEFT {meta['id']} {meta['name']}\n".encode("utf-8"),
                exclude=writer
            )
        except Exception as e:
            print(f"[ERROR] {meta['name']} (ID={meta['id']}): {type(e).__name__}: {e}")
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

    async def _handle_powerup_collected(self, text: str):
        parts = text.split()
        pw_id = None
        if len(parts) >= 2:
            try:
                pw_id = int(parts[1])
            except ValueError:
                pw_id = None

        if pw_id is not None and pw_id in self.power_ups:
            del self.power_ups[pw_id]
            await self.broadcast(f"POWER_UP_REMOVED {pw_id}\n".encode("utf-8"))
            # Sofort neu spawnen
            await self._spawn_one_powerup_if_none()
        else:
            print(f"[WARN] POWER_UP_COLLECTED unknown id: {parts[1] if len(parts)>=2 else '?'}")

    async def _periodic_powerup_spawner(self):
        try:
            while True:
                await asyncio.sleep(0.25)
                await self._maybe_spawn_powerup()
        except asyncio.CancelledError:
            return

    async def _maybe_spawn_powerup(self):
        now = self._now_ms()
        if not self.power_ups and (now - self._last_powerup_spawn_ms >= self.powerup_spawn_interval_ms):
            await self._spawn_one_powerup_if_none()

    async def _spawn_one_powerup_if_none(self):
        if self.power_ups:
            return
        # Position nicht auf Food
        while True:
            x = random.randint(0, GRID_W - 1)
            y = random.randint(0, GRID_H - 1)
            if (x, y) not in self.food_locations:
                break

        pw_type = random.choice(self.available_powerups)
        pw_id = self._next_powerup_id
        self._next_powerup_id += 1

        self.power_ups[pw_id] = {"x": x, "y": y, "pw_type": pw_type}
        self._last_powerup_spawn_ms = self._now_ms()

        await self.broadcast(f"POWER_UP_SPAWNED {pw_id} {x} {y} {pw_type}\n".encode("utf-8"))
        print(f"[SERVER] Spawned powerup id={pw_id} type={pw_type} at {x},{y}")

    async def broadcast(self, data: bytes, exclude: asyncio.StreamWriter | None = None):
        dead: list[asyncio.StreamWriter] = []
        for w in list(self.clients):
            if exclude is not None and w is exclude:
                continue
            try:
                w.write(data)
            except Exception:
                dead.append(w)
        await asyncio.gather(
            *(w.drain() for w in list(self.clients)
              if (exclude is None or w is not exclude) and w not in dead),
            return_exceptions=True
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

async def main():
    server_logic = BroadcastServer()
    host = server_functions.get_local_ipv4()
    server = await asyncio.start_server(server_logic.handle_client, host, PORT)
    addr_list = ", ".join(str(s.getsockname()) for s in server.sockets)
    print(f"Server läuft auf {addr_list} - warte auf Clients...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
