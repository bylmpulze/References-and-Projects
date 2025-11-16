import os
import sys
import pygame

def resource_path(rel_path: str) -> str:
    try:
        base_path = sys._MEIPASS
        base_path = os.path.join(base_path, "Snake Multiplayer")
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, rel_path)

def quit_game():
    pygame.quit()
    sys.exit()
