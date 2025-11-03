# client.py
import socket
import pygame

HOST = "10.35.25.109"  # <- LAN-IP des Server-PCs eintragen
PORT = 50007

def run():
    sock = socket.create_connection((HOST, PORT))
    f_in = sock.makefile("r", encoding="utf-8", newline="\n")

    pygame.init()
    W, H = 640, 480
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Pygame Client (Pfeiltasten bewegen Rechteck)")
    clock = pygame.time.Clock()

    x, y = 320, 240
    speed = 5
    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * speed
            dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * speed

            sock.sendall(f"INPUT {dx} {dy}\n".encode("utf-8"))
            line = f_in.readline()
            if not line:
                print("Verbindung zum Server verloren.")
                break
            parts = line.strip().split()
            if len(parts) == 3 and parts[0] == "STATE":
                try:
                    x = int(parts[1]); y = int(parts[2])
                except ValueError:
                    pass

            screen.fill((30, 30, 30))
            pygame.draw.rect(screen, (0, 200, 120), pygame.Rect(x, y, 40, 40))
            pygame.display.flip()
            clock.tick(60)
    finally:
        sock.close()
        pygame.quit()

if __name__ == "__main__":
    run()
