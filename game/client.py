import socket
import threading
import queue

class Client:
    """
    TCP client with a reader thread (incoming queue) and a sender thread (outgoing queue).
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 50007) -> None:
        self.server_host = host
        self.server_port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

        # Thread coordination
        self._stop_event = threading.Event()

        # Queues
        self.incoming_messages: "queue.Queue[str | None]" = queue.Queue()
        self.outgoing_messages: "queue.Queue[bytes]" = queue.Queue()

        # Threads
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._sender_thread = threading.Thread(target=self._send_loop, daemon=True)
        self._reader_thread.start()
        self._sender_thread.start()
        self.queue_send(b"HELLO Player\n")

    def queue_send(self, data) -> None:
        """
        Enqueue a message to be sent by the sender thread.
        """
        self.outgoing_messages.put(data)

    def send_immediate(self, delta_x: int, delta_y: int, part_index: int) -> None:
        """
        Bypass the queue and send immediately on the calling thread.
        Useful for urgent control messages.
        """
        line = f"INPUT {delta_x} {delta_y} {part_index}\n".encode("utf-8")
        self.socket.sendall(line)

    def _read_loop(self) -> None:
        """
        Reads lines and pushes them to incoming_messages; pushes None on EOF.
        """
        f_in = self.socket.makefile("r", encoding="utf-8", newline="\n")
        try:
            while not self._stop_event.is_set():
                line = f_in.readline()
                if not line:
                    self.incoming_messages.put(None)
                    break
                self.incoming_messages.put(line.rstrip("\n"))
        finally:
            try: 
                f_in.close()
            except Exception: 
                pass

    def _send_loop(self) -> None:
        """
        Pulls bytes from outgoing_messages and writes to the socket.
        """
        try:
            while not self._stop_event.is_set():
                try:
                    data = self.outgoing_messages.get(timeout=0.2)  # wake periodically
                except queue.Empty:
                    continue
                if data is None:
                    break
                # Handle partial sends by looping until buffer is empty [web:41]
                view = memoryview(data)
                while view:
                    sent = self.socket.send(view)  # may send fewer bytes [web:41]
                    view = view[sent:]
                self.outgoing_messages.task_done()
        except OSError:
            pass  # socket closed during shutdown

    def receive_now(self):
        try:
            return self.incoming_messages.get_nowait()
        except queue.Empty:
            return None

    def receive_wait(self, timeout: float | None = None):
        try:
            return self.incoming_messages.get(timeout=timeout)
        except queue.Empty:
            return None

    def close(self) -> None:
        """
        Signal threads to stop, drain sender, and close the socket.
        """
        self._stop_event.set()
        # Stop sender loop gracefully
        try:
            self.outgoing_messages.put_nowait(None)
        except Exception:
            pass
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.socket.close()
        except OSError:
            pass


class FakeClient:
    def __init__(self):
        pass

    def receive_now(self):
        return None

    def queue_send(self, data):
        pass