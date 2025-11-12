import socket
import threading
import queue
import json
import random
import pygame
from game.powerups import powerupconfig
from game.snake_functions import get_random_food_coords
import game.constants as CONSTANTS

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
        self.queue_send(f"HELLO Player {CONSTANTS.VERSION}\n".encode("utf-8"))

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
        self.queue = []
        self.snake = []
        self.power_ups = {0 : {"x":5,"y":5,"pw_type": "speed_boost_x2"}}
        self.foodCords = []
        self.foodCords.append(get_random_food_coords(self.snake,self.foodCords))
        self.queue.append(f"FOOD_SPAWNED {self.foodCords[0][0]} {self.foodCords[0][1]}")

    def receive_now(self):
        if not self.queue:
            return None
                
        return self.queue.pop(0)
    
    def handle_powerup_spawn(self):

        available_powerups = [
            "speed_boost_x2", "speed_half", "extra_life", "powerup_drunk", "powerup_magnet"
        ]
      
        if not self.power_ups.items():
            while True:
                coord = [random.randint(0, 27), random.randint(0, 27)]
                if coord not in self.snake:
                    x,y = coord
                    break
            pw_type = random.choice(available_powerups)
            self.power_ups[0] = {"x":x,"y":y,"pw_type": pw_type}

        
        self.active_powerup = random.choice(available_powerups)
        self.powerup_spawned = True
        self.powerup_spawntime = pygame.time.get_ticks()

        for pw_id, power_up in self.power_ups.items():
            self.queue.append(f"POWER_UP_SPAWNED {pw_id} {power_up['x']} {power_up['y']} {power_up['pw_type']}")

    def queue_send(self, data):

    
        line = data.decode("utf-8").strip()

        try:
            self.snake = json.loads(line)
        except json.JSONDecodeError:
            if "FOOD_EATEN" in line:
                x,y = get_random_food_coords(self.snake,self.foodCords)
                self.foodCords = [x,y]
                self.queue.append(f"FOOD_SPAWNED {x} {y}")
            elif "DEAD SNAKE" in line:
                x,y = get_random_food_coords(self.snake,self.foodCords)
                self.foodCords = [x,y]
                self.queue.append(f"FOOD_SPAWNED {x} {y}")
            elif "POWER_UP_COLLECTED" in line:
                _, pw_id = line.split()
                del self.power_ups[int(pw_id)]
    
        self.handle_powerup_spawn()