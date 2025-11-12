import socket
import asyncio
from typing import Dict, Tuple, List
from server_main import BroadcastServer, PORT

def get_local_ipv4(target=("8.8.8.8", 80)):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(target)
        return s.getsockname()[0]
    finally:
        s.close()