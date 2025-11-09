import os
import pygame
import sys
import json
from game.powerups import PowerUp, powerupconfig
from game.client import Client, FakeClient
from game.snake_functions import draw_other_snakes, handle_snake_collisions
from game.selector_screen import menu_screen

particle = 25
snake = [[13, 13], [13, 14]]
direction = 0
feedCordrnd = []
go = True
endgame = False
score = 0
snake_speed = 4  # mehr = langsamer
move_counter = 0

pygame.init()
SCREEN_SIZE = 800
TOPBAR_HEIGHT = 40
GAME_SIZE = SCREEN_SIZE - TOPBAR_HEIGHT
screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])
clock = pygame.time.Clock()
powerups = PowerUp(particle_size=particle)

def resource_path(rel_path: str) -> str:
    try:
        base_path = sys._MEIPASS
        base_path = os.path.join(base_path, "Snake Multiplayer")
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, rel_path)

# Assets laden
food_img = pygame.image.load(resource_path("game/assets/apfel2.jpg"))
food_img = pygame.transform.scale(food_img, (particle, particle))

body_img = pygame.image.load(resource_path("game/assets/snakebody.jpg")).convert_alpha()
body_img = pygame.transform.scale(body_img, (particle, particle))

head_img = pygame.image.load(resource_path("game/assets/snakehead.jpg")).convert_alpha()
head_img = pygame.transform.scale(head_img, (particle, particle))

PLAYERID = None
font = pygame.font.SysFont(None, 40)

# -----------------------------
# Topbar
# -----------------------------
def draw_topbar():
    # Hintergrund
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, SCREEN_SIZE, TOPBAR_HEIGHT))
    
    # Score
    score_text = font.render(f"Punkte: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    
    # Einstellungen-Button
    settings_text = font.render("Einstellungen", True, (0, 0, 0))
    settings_rect = settings_text.get_rect(topright=(SCREEN_SIZE - 10, 10))
    screen.blit(settings_text, settings_rect)
    
    return settings_rect

# -----------------------------
# Restart / Game Over
# -----------------------------
def restart_environment():
    global snake, direction, feedCordrnd, score, endgame, powerup_active, snake_speed
    snake = [[13, 13], [13, 14]]
    direction = 0
    feedCordrnd = []
    score = 0
    endgame = False
    powerup_active = -9999
    powerups.delete_powerup()
    snake_speed = 4

def game_over_screen():
    screen.fill((255, 255, 255))
    game_over_text = font.render(f"Spiel zuende! Deine Punktzahl: {score}", True, (255, 0, 0))
    restart_text = font.render("Klicke um neu zu starten", True, (0, 0, 0))
    screen.blit(game_over_text, (50, 300))
    screen.blit(restart_text, (50, 350))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
                restart_environment()

# -----------------------------
# Spielfeld zeichnen
# -----------------------------
def printing():
    screen.fill((255, 255, 255))
    
    # Topbar
    settings_rect = draw_topbar()
    
    # Apfel
    for a in feedCordrnd:
        Coords = [a[0] * particle, a[1] * particle + TOPBAR_HEIGHT]
        screen.blit(food_img, (Coords[0], Coords[1]))

    # Schlange
    for i, x in enumerate(snake):
        Coords = [x[0] * particle, x[1] * particle + TOPBAR_HEIGHT]
        if i == 0:
            if direction == 0:   
                rotated_head = pygame.transform.rotate(head_img, 0)
            elif direction == 1: 
                rotated_head = pygame.transform.rotate(head_img, 270)
            elif direction == 2: 
                rotated_head = pygame.transform.rotate(head_img, 180)
            elif direction == 3: 
                rotated_head = pygame.transform.rotate(head_img, 90)
            screen.blit(rotated_head, (Coords[0], Coords[1]))
        else:
            screen.blit(body_img, (Coords[0], Coords[1]))
    
    return settings_rect

# -----------------------------
# Multiplayer Setup
# -----------------------------
ip_addr = menu_screen(screen, SCREEN_SIZE)
if ip_addr is None:
    client = FakeClient()
else:
    try:
        client = Client(ip_addr)
    except Exception as _:
        client = FakeClient()

other_snakes = {}

# -----------------------------
# Input Handler
# -----------------------------
def handle_powerup_drunk(event, direction):
    if event.key in [pygame.K_UP, pygame.K_w] and direction != 0:
        direction = 2 
    if event.key in [pygame.K_RIGHT, pygame.K_d] and direction != 1:
        direction = 3 
    if event.key in [pygame.K_DOWN, pygame.K_s] and direction != 2:
        direction = 0 
    if event.key in [pygame.K_LEFT, pygame.K_a] and direction != 3:
        direction = 1 
    return direction

def handle_normal_movement(event, direction):
    if event.key in [pygame.K_UP, pygame.K_w] and direction != 2:
        direction = 0 
    if event.key in [pygame.K_RIGHT, pygame.K_d] and direction != 3:
        direction = 1 
    if event.key in [pygame.K_DOWN, pygame.K_s] and direction != 0:
        direction = 2
    if event.key in [pygame.K_LEFT, pygame.K_a] and direction != 1:
        direction = 3 
    return direction

def handle_keypress(event, direction, change_direction_collected):
    powerup_active = pygame.time.get_ticks() - (change_direction_collected or 0)
    powerup_active = 0 < powerup_active < 5_000
    if event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
    if powerup_active: 
        direction = handle_powerup_drunk(event, direction) 
    else:
        direction = handle_normal_movement(event, direction) 
    if event.key in [pygame.K_SPACE]: 
        restart_environment()
    return direction

powerup_drunk_collected = -9999
immunity_collected_time = None
power_up_not_collected_time = None

# -----------------------------
# Main Loop
# -----------------------------
while go:
    settings_rect = draw_topbar()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            direction = handle_keypress(event, direction, powerup_drunk_collected)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if settings_rect.collidepoint(event.pos):
                print("Einstellungen öffnen!")  # Hier kann dein Einstellungsfenster kommen

    if move_counter % snake_speed == 0:
        new_head = snake[0].copy()
        if direction == 0: new_head[1] -= 1
        if direction == 1: new_head[0] += 1
        if direction == 2: new_head[1] += 1
        if direction == 3: new_head[0] -= 1

        powerups.spawn_powerup(snake)
        collected = powerups.check_collision(new_head)
        if collected:
            if collected == "speed_boost_x2":
                snake_speed = max(1, snake_speed // 2)
            elif collected == "speed_half":
                snake_speed = snake_speed * 2
            elif collected == "extra_life":
                immunity_collected_time = pygame.time.get_ticks()
            elif collected == "powerup_drunk":
                powerup_drunk_collected = pygame.time.get_ticks()
        else:
            power_up_not_collected_time = pygame.time.get_ticks() - (powerups.powerup_spawntime or 0) 
            if power_up_not_collected_time > powerupconfig.power_up_activ_time:
                powerups.delete_powerup()

        new_head[0] %= (SCREEN_SIZE // particle)
        new_head[1] %= (GAME_SIZE // particle)  # Spielfeld begrenzt nur auf Game_Size

        if handle_snake_collisions(new_head, snake, other_snakes, immunity_collected_time):
            client.queue_send(f"DEAD SNAKE {PLAYERID}\n".encode("utf-8"))
            game_over_screen()

        if not endgame:
            snake = [new_head] + snake[:-1]

        for i, food in enumerate(feedCordrnd):
            if food == new_head:
                snake.append(snake[-1].copy())
                del feedCordrnd[i]
                score += 10
                client.queue_send("FOOD_EATEN\n".encode("utf-8"))
                break

    if move_counter % 2 == 0:
        client.queue_send((json.dumps(snake) + "\n").encode("utf-8"))

    printing()
    draw_other_snakes(other_snakes, particle, screen, body_img, head_img)
    powerups.draw(screen)
    pygame.display.update()

    while data_from_server := client.receive_now():
        if "WELCOME" in data_from_server:
            PLAYERID = data_from_server.split()[1]
        elif "DEAD SNAKE" in data_from_server:
            dead_snake_id = data_from_server.split()[2]
            if dead_snake_id in other_snakes:
                del other_snakes[dead_snake_id]
        elif "FOOD_SPAWNED" in data_from_server:
            _, x, y = data_from_server.split()
            feedCordrnd = [[int(x), int(y)]]
        else:
            snake_id, other_snakes_data = data_from_server.split(":", 1)
            other_snakes[snake_id] = json.loads(other_snakes_data)

    move_counter += 1
    clock.tick(60)
