import os
import pygame
import sys
import json
import game.constants as CONSTANTS
from game.powerups import PowerUp, powerupconfig
from game.client import Client
from game.fake_client_adapter import FakeClient  # <— hinzufügen
from game.snake_functions import draw_other_snakes, handle_snake_collisions
from game.selector_screen import menu_screen
from game.scenes.reject_screen import draw_rejected
from game.scenes.settings_menu import settings_menu
from game.snake import Snake
from game.food import Food


direction = 0
feedCordrnd = []
endgame = False
score = 0
move_counter = 0
POWER_UPS: dict[int, PowerUp] = {}

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode([CONSTANTS.SCREEN_SIZE, CONSTANTS.SCREEN_SIZE])
clock = pygame.time.Clock()
powerups = PowerUp(particle_size=CONSTANTS.PARTICLE_SIZE)

SNAKE = Snake()
foods = [Food(CONSTANTS.PARTICLE_SIZE)]

PLAYERID = None
font = pygame.font.SysFont(None, 40)


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
    global foods
    screen.fill((255, 255, 255))
    to_delete = []
    for food in foods:
        food.draw(screen)   

        if food.collides_with_rect(SNAKE.get_head_rect()):
            SNAKE.grow()
            food.on_eaten()
            to_delete.append(food)

    foods = [f for f in foods if f not in to_delete]
            
    SNAKE.draw(screen)
    
# Multiplayer Setup

ip_addr = menu_screen(screen, CONSTANTS.SCREEN_SIZE)
if not ip_addr:
    client = FakeClient(version=CONSTANTS.VERSION, name="player")
    client.connect()
else:
    try:
        client = Client(ip_addr)           # echter Socket-Client
        client.connect(name="player", version=CONSTANTS.VERSION)
    except Exception:
        client = FakeClient(version=CONSTANTS.VERSION, name="player")
        client.connect()

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
        print(msg)
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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            direction = handle_keypress(event, direction, powerup_drunk_collected)

    if direction == 0: 
        SNAKE.move_up()
    if direction == 1:
        SNAKE.move_right()
    if direction == 2:
        SNAKE.move_down()
    if direction == 3:
        SNAKE.move_left()

    #if move_counter % 25 == 0:
    #    SNAKE.grow()
    
    SNAKE.update()
    process_server_messages()

    draw_game_elements()
    pygame.display.update()

    move_counter += 1
    clock.tick(60)
