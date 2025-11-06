import time
import socket
import asyncio

HOST = "127.0.0.1"
PORT = 50007

def get_local_ipv4(target=("8.8.8.8", 80)):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(target)
        return s.getsockname()[0]
    finally:
        s.close()

class BroadcastServer:
    def __init__(self, max_line=8192, handshake_timeout=5.0):
        self.clients: set[asyncio.StreamWriter] = set()
        self.snakes = []
        self.client_meta: dict[asyncio.StreamWriter, dict] = {}
        self._next_id = 1
        self.max_line = max_line
        self.handshake_timeout = handshake_timeout

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

        # Expect: HELLO <name>
        if not text.startswith("HELLO"):
            raise RuntimeError("invalid handshake verb")
        parts = text.split(maxsplit=1)
        name = parts[1].strip() if len(parts) == 2 else ""

        cid = self._next_id
        self._next_id += 1

        # Send acknowledgment
        writer.write(f"WELCOME {cid}\n".encode("utf-8"))
        await writer.drain()

        return {"id": cid, "name": name}

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")
        try:
            meta = await self._do_handshake(reader, writer)
        except Exception as e:
            # Send an error and close
            try:
                writer.write(f"ERROR {str(e)}\n".encode("utf-8"))
                await writer.drain()
            except Exception:
                pass
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            print(f"Handshake failed from {peer}: {e}")
            return

        self.clients.add(writer)
        self.client_meta[writer] = meta
        print(f"Client verbunden: {peer} as {meta}")

        try:
            while True:
                try:
                    line = await self._readline_capped(reader)  # \n-terminated messages
                except ValueError:
                    # too long, discard this client
                    print(f"Client sent oversized line: {peer}")
                    break

                if not line:
                    print(f"Client getrennt: {peer}")
                    break

                now = time.time()
                self.snakes.append((now, line))

                # Optional: prepend sender id or name
                prefix = f"{meta['id']}: ".encode("utf-8")
                outbound = prefix + line

                await self.broadcast(outbound, exclude=writer)
        finally:
            if writer in self.clients:
                self.clients.discard(writer)
            self.client_meta.pop(writer, None)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

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
    host = get_local_ipv4()
    server = await asyncio.start_server(server_logic.handle_client, host, PORT)
    addr_list = ", ".join(str(s.getsockname()) for s in server.sockets)
    print(f"Server läuft auf {addr_list} - warte auf Clients...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
