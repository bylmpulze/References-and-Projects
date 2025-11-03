# server.py
import threading
import socket

HOST = "10.35.25.109"  # auf allen Interfaces lauschen
PORT = [50007, 50008, 50009]  # Liste der Ports für mehrere Clients

def run(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, port))
        srv.listen(1)
        print(f"Server läuft auf {HOST}:{port} – warte auf Client...")
        conn, addr = srv.accept()
        print(f"Client verbunden: {addr}")
        with conn:
            f_in = conn.makefile("r", encoding="utf-8", newline="\n")
            x, y = 320, 240
            w, h = 640, 480
            speed_limit = 10
            while True:
                line = f_in.readline()
                print(f"Empfangene Daten vom Client {port}:", line.strip())
                if not line:
                    print("Client getrennt.")
                    break
                parts = line.strip().split()
                if len(parts) == 3 and parts[0] == "INPUT":
                    try:
                        dx = int(parts[1]); dy = int(parts[2])
                    except ValueError:
                        dx = dy = 0
                    dx = max(-speed_limit, min(speed_limit, dx))
                    dy = max(-speed_limit, min(speed_limit, dy))
                    x = max(0, min(w - 40, x + dx))
                    y = max(0, min(h - 40, y + dy))
                    conn.sendall(f"STATE {x} {y}\n".encode("utf-8"))
                else:
                    conn.sendall(f"STATE {x} {y}\n".encode("utf-8"))


def start_server(port):
    while 1:
        try:
            run(port)
        except Exception as e:
            print("Fehler im Server:", e)
   


if __name__ == "__main__":
    workers = []
    for port in PORT:
        server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
        server_thread.start()
        workers.append(server_thread)
    
    for worker in workers:
        worker.join()





