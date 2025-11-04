import asyncio
import socket

HOST = "0.0.0.0"
PORT = 50007  # ein Port genügt; mehrere Ports sind möglich, aber meist unnötig

def get_local_ipv4(target=("192.0.2.1", 80)):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(target)  # sendet nichts; wählt Route/Interface
        return s.getsockname()[0]
    finally:
        s.close()

class BroadcastServer:
    def __init__(self):
        # Speichere nur Writer; Peername kann bei Bedarf separat gemappt werden
        self.clients: set[asyncio.StreamWriter] = set()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")
        self.clients.add(writer)
        print(f"Client verbunden: {peer}")
        try:
            while True:
                line = await reader.readline()  # erwartet \n-terminierte Nachrichten
                if not line:
                    print(f"Client getrennt: {peer}")
                    break
                # Optional: Validierung/Begrenzung
                if len(line) > 8192:
                    continue  # zu lange Zeile verwerfen

                # Broadcast an alle anderen
                await self.broadcast(line, exclude=writer)
        finally:
            # Client entfernen und sauber schließen
            if writer in self.clients:
                self.clients.discard(writer)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def broadcast(self, data: bytes, exclude: asyncio.StreamWriter | None = None):
        dead: list[asyncio.StreamWriter] = []
        # Zuerst write() an alle (nicht blockierend), dann drain() gesammelt
        for w in list(self.clients):
            if exclude is not None and w is exclude:
                continue
            try:
                w.write(data)
            except Exception:
                dead.append(w)
        # Flusskontrolle berücksichtigen
        await asyncio.gather(*(w.drain() for w in list(self.clients)
                               if (exclude is None or w is not exclude) and w not in dead),
                             return_exceptions=True)
        # Tote Verbindungen aufräumen
        for w in dead:
            if w in self.clients:
                self.clients.discard(w)
            try:
                w.close()
                await w.wait_closed()
            except Exception:
                pass

async def main():
    server_logic = BroadcastServer()
    # host = get_local_ipv4()  # falls du explizit auf der aktiven LAN-IP lauschen willst
    host = HOST
    server = await asyncio.start_server(server_logic.handle_client, host, PORT)
    addr_list = ", ".join(str(s.getsockname()) for s in server.sockets)
    print(f"Server läuft auf {addr_list} – warte auf Clients...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
