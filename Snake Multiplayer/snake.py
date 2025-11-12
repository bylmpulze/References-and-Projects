import os
import pygame
import sys
import json
import game.constants as CONSTANTS
from game.powerups import PowerUp, powerupconfig
from game.client import Client, FakeClient
from game.snake_functions import draw_other_snakes, handle_snake_collisions
from game.selector_screen import menu_screen
from game.scenes.reject_screen import draw_rejected

snake = [[13, 13], [13, 14]]
direction = 0
feedCordrnd = []
endgame = False
score = 0
snake_speed = 4  # mehr = langsamer
move_counter = 0
POWER_UPS: dict[int, PowerUp] = {}

pygame.init()
screen = pygame.display.set_mode([CONSTANTS.SCREEN_SIZE, CONSTANTS.SCREEN_SIZE])
clock = pygame.time.Clock()
powerups = PowerUp(particle_size=CONSTANTS.PARTICLE_SIZE)

def resource_path(rel_path: str) -> str:
    try:
        base_path = sys._MEIPASS
        base_path = os.path.join(base_path, "Snake Multiplayer")
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, rel_path)

# Assets
food_img = pygame.image.load(resource_path("game/assets/apfel2.jpg"))
food_img = pygame.transform.scale(food_img, (CONSTANTS.PARTICLE_SIZE, CONSTANTS.PARTICLE_SIZE))

body_img = pygame.image.load(resource_path("game/assets/snakebody.jpg")).convert_alpha()
body_img = pygame.transform.scale(body_img, (CONSTANTS.PARTICLE_SIZE, CONSTANTS.PARTICLE_SIZE))

head_img = pygame.image.load(resource_path("game/assets/snakehead.jpg")).convert_alpha()
head_img = pygame.transform.scale(head_img, (CONSTANTS.PARTICLE_SIZE, CONSTANTS.PARTICLE_SIZE))

PLAYERID = None
font = pygame.font.SysFont(None, 40)

def draw_topbar(just_rect = False):
    settings_text = font.render("Einstellungen", True, (0, 0, 0))
    settings_rect = settings_text.get_rect(topright=(CONSTANTS.SCREEN_SIZE - 10, 10))
    if just_rect:
        return settings_rect
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, CONSTANTS.SCREEN_SIZE, CONSTANTS.TOPBAR_HEIGHT))
    score_text = font.render(f"Punkte: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(settings_text, settings_rect)

def restart_environment():
    global snake, direction, feedCordrnd, score, endgame, powerup_active, snake_speed, powerup_magnet_activ
    snake = [[13, 13], [13, 14]]
    direction = 0
    feedCordrnd = []
    score = 0
    endgame = False
    powerup_magnet_activ = False
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

def draw_game_elements():
    screen.fill((255, 255, 255))
    draw_topbar()
    for a in feedCordrnd:
        Coords = [a[0] * CONSTANTS.PARTICLE_SIZE, a[1] * CONSTANTS.PARTICLE_SIZE + CONSTANTS.TOPBAR_HEIGHT]
        screen.blit(food_img, (Coords[0], Coords[1]))
    for i, x in enumerate(snake):
        Coords = [x[0] * CONSTANTS.PARTICLE_SIZE, x[1] * CONSTANTS.PARTICLE_SIZE + CONSTANTS.TOPBAR_HEIGHT]
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

# Multiplayer Setup
ip_addr = menu_screen(screen, CONSTANTS.SCREEN_SIZE)
if ip_addr is None:
    client = FakeClient()
else:
    try:
        client = Client(ip_addr)
    except Exception:
        client = FakeClient()

other_snakes: dict[str, list[list[int]]] = {}

# Input Handler
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


powerup_magnet_collected_time = 0
powerup_drunk_collected = -9999
immunity_collected_time = None
power_up_not_collected_time = None
powerup_magnet_activ = False

def process_server_messages():
    global PLAYERID, feedCordrnd, POWER_UPS, other_snakes
    while (msg := client.receive_now()) is not None:
        if "WELCOME" in msg:
            PLAYERID = msg.split()[1]
        elif "DEAD SNAKE" in msg:
            dead_snake_id = msg.split()[2]
            if dead_snake_id in other_snakes:
                del other_snakes[dead_snake_id]
        elif "PLAYER_LEFT" in msg:
            dead_snake_id = msg.split()[1]
            if dead_snake_id in other_snakes:
                del other_snakes[dead_snake_id]
        elif "FOOD_SPAWNED" in msg:
            _, x, y = msg.split()
            feedCordrnd = [[int(x), int(y)]]
        elif "POWER_UP_SPAWNED" in msg:
            parts = msg.split()
            _, pw_id_str, x, y, pw_type = parts[:5]
            pw_id = int(pw_id_str)
            po = PowerUp(CONSTANTS.PARTICLE_SIZE)
            po.add_powerup(snake, pw_id, int(x), int(y), pw_type)
            POWER_UPS[pw_id] = po
        elif "POWER_UP_REMOVED" in msg:
            parts = msg.split()
            if len(parts) >= 2:
                try:
                    pw_id = int(parts[1])
                except ValueError:
                    continue
                if pw_id in POWER_UPS:
                    del POWER_UPS[pw_id]
        elif "REJECTED" in msg:
            _, msg_str = msg.split()
            draw_rejected(screen,msg_str)
                        
        else:
            if ":" in msg:
                snake_id, other_snakes_data = msg.split(":", 1)
                other_snakes[snake_id] = json.loads(other_snakes_data)


# Main Loop
while True:
    settings_rect = draw_topbar(True)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            direction = handle_keypress(event, direction, powerup_drunk_collected)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if settings_rect.collidepoint(event.pos):
                print("Einstellungen öffnen!")

    if move_counter % snake_speed == 0:
        new_head = snake[0].copy()
        if direction == 0: new_head[1] -= 1
        if direction == 1: new_head[0] += 1
        if direction == 2: new_head[1] += 1
        if direction == 3: new_head[0] -= 1

        # Powerup-Kollisionen
        to_keep: dict[int, PowerUp] = {}
        for pw_id, power_up in list(POWER_UPS.items()):
            collected = power_up.check_collision(new_head)
            if collected:
                # sofort an Server melden
                client.queue_send(f"POWER_UP_COLLECTED {pw_id}\n".encode("utf-8"))
                if collected == "speed_boost_x2":
                    snake_speed = max(1, snake_speed // 2)
                elif collected == "speed_half":
                    snake_speed = snake_speed * 2
                elif collected == "extra_life":
                    immunity_collected_time = pygame.time.get_ticks()
                elif collected == "powerup_drunk":
                    powerup_drunk_collected = pygame.time.get_ticks()
                elif collected == "powerup_magnet":
                    powerup_magnet_collected_time = pygame.time.get_ticks()
                    powerup_magnet_activ = True
            else:
                to_keep[pw_id] = power_up
                power_up_not_collected_time = pygame.time.get_ticks() - (powerups.powerup_spawntime or 0)
                if power_up_not_collected_time > powerupconfig.power_up_activ_time:
                    pass
        POWER_UPS = to_keep

        # Magnet-Effekt
        if 0 < pygame.time.get_ticks() - powerup_magnet_collected_time < powerupconfig.powerup_magnet_duration and powerup_magnet_activ:
            for i, food in enumerate(list(feedCordrnd)):
                if food[0] < snake[0][0]:
                    food[0] += 1
                elif food[0] > snake[0][0]:
                    food[0] -= 1
                if food[1] < snake[0][1]:
                    food[1] += 1
                elif food[1] > snake[0][1]:
                    food[1] -= 1
                if food == snake[0]:
                    del feedCordrnd[i]
                    snake.append(snake[-1].copy())
                    score += 10
                    client.queue_send(b"FOOD_EATEN\n")

        new_head[0] %= (CONSTANTS.SCREEN_SIZE // CONSTANTS.PARTICLE_SIZE)
        new_head[1] %= (CONSTANTS.GAME_SIZE // CONSTANTS.PARTICLE_SIZE)

        if handle_snake_collisions(new_head, snake, other_snakes, immunity_collected_time):
            client.queue_send(f"DEAD SNAKE {PLAYERID}\n".encode("utf-8"))
            game_over_screen()

        if not endgame:
            snake = [new_head] + snake[:-1]

        for i, food in enumerate(list(feedCordrnd)):
            if food == new_head:
                snake.append(snake[-1].copy())
                del feedCordrnd[i]
                score += 10
                client.queue_send(b"FOOD_EATEN\n")
                break

    if move_counter % 2 == 0:
        client.queue_send((json.dumps(snake) + "\n").encode("utf-8"))

    draw_game_elements()
    draw_other_snakes(other_snakes, CONSTANTS.PARTICLE_SIZE, screen, body_img, head_img)

    for pw_id, powerup in POWER_UPS.items():
        powerup.draw(screen)

    pygame.display.update()

    process_server_messages()

    move_counter += 1
    clock.tick(60)
