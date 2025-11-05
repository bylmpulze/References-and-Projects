import os
import pygame
import sys
import json
import random as randomizer
from powerups import PowerUp
from client import Client, FakeClient
from snake_functions import draw_other_snakes


particle = 25
snake = [[13, 13], [13, 14]]
direction = 0
feedCordrnd = []
go = True
endgame = False
score = 0
snake_speed = 4 # mehr = langsamer
move_counter = 0

pygame.init()
SCREEN_SIZE = 800
screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])
clock = pygame.time.Clock()
powerups = PowerUp(particle_size=particle)

base_path = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(base_path, "assets")

food_img = pygame.image.load(os.path.join(asset_path, "apfel2.jpg"))  # Futterbild
food_img = pygame.transform.scale(food_img, (particle, particle))

body_img = pygame.image.load(os.path.join(asset_path, "snakebody.jpg")).convert_alpha()
body_img = pygame.transform.scale(body_img, (particle, particle))

head_img = pygame.image.load(os.path.join(asset_path, "snakehead.jpg")).convert_alpha()
head_img = pygame.transform.scale(head_img, (particle, particle))

PLAYER_COLORS = {
    "p1": (0, 200, 0),    # green
    "p2": (220, 40, 40),  # red
    "p3": (40, 120, 220), # blue
    "p4": (230, 170, 30), # yellow
}

PLAYERID = None

def tint_surface(src: pygame.Surface, color: tuple[int,int,int]) -> pygame.Surface:
    # Preserves per-pixel alpha and shading by multiplying RGB
    # color is (r,g,b) in 0..255
    tinted = src.copy()
    mask = pygame.Surface(src.get_size(), flags=pygame.SRCALPHA)
    # Fill with the tint color, full alpha to affect RGB channels
    mask.fill((*color, 255))
    # Multiply: darkens channels proportionally to the tint
    tinted.blit(mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    return tinted

def make_snake_skins(color):
    return (
        tint_surface(body_img, color),     # or recolor_exact(body_img, color)
        tint_surface(head_img, color),     # or recolor_exact(head_img, color)
    )

snake_skins = {sid: make_snake_skins(col) for sid, col in PLAYER_COLORS.items()}

font = pygame.font.SysFont(None, 40)

def draw_score():
    score_text = font.render(f"Punkte: {score}", True, (0, 0, 0))  # Schwarz
    screen.blit(score_text, (10, 10))  # Oben links 

#region restart
def restartenvironment ():
    global snake, direction, feedCordrnd, score, endgame, powerup_active
    snake = [[13, 13], [13, 14]]
    direction = 0
    feedCordrnd = [feedCordsRandomizer()]
    score = 0
    endgame = False
    powerup_active = -9999
    powerups.delete_powerup()



def feedCordsRandomizer():
    while True:
        Coord = [randomizer.randint(0, 27), randomizer.randint(0, 27)]
        if Coord not in snake and Coord not in feedCordrnd:
            return Coord

def game_over_screen():
    screen.fill((255, 255, 255))  # Weißer Hintergrund
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

#endregion

# region Grafiken 
def printing():
    screen.fill((255, 255, 255))  # Weißer Hintergrund

    # Apfel
    for a in feedCordrnd:
        Coords = [a[0] * particle, a[1] * particle]
        screen.blit(food_img, (Coords[0], Coords[1]))

    # Schlange 
    for i, x in enumerate(snake):
        Coords = [x[0] * particle, x[1] * particle]
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

        draw_score()
        


feedCordrnd.append(feedCordsRandomizer())

SINGLE = False
try:
    client = Client()  # Multiplayer Client initialisieren
except Exception as e:
    client = FakeClient()

other_snakes = {}


def identfy(player_id):
    font = pygame.font.SysFont(None, SCREEN_SIZE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

        screen.fill((255, 255, 255))  # Weißer Hintergrund
        id_text = font.render(f"{player_id}", True, (0, 0, 0))  # Schwarz
        width,height = id_text.get_size()
        x = SCREEN_SIZE//2 - width//2
        y = SCREEN_SIZE//2 - height//2
        screen.blit(id_text, (x, y))  # Zentriert
        pygame.display.update()

#powerup change_direction movement handler (opposite_directions -> down = up)
def handle_powerup_drunk(event,direction):
    if event.key in [pygame.K_UP,pygame.K_w] and direction != 0:
        direction = 2 
    if event.key in [pygame.K_RIGHT,pygame.K_d] and direction != 1:
        direction = 3 
    if event.key in [pygame.K_DOWN,pygame.K_s] and direction != 2:
        direction = 0 
    if event.key in [pygame.K_LEFT,pygame.K_a] and direction != 3:
        direction = 1 
    return direction

#normal movement_handler
def handle_normal_movement(event,direction):
    if event.key in [pygame.K_UP,pygame.K_w] and direction != 2:
        direction = 0 
    if event.key in [pygame.K_RIGHT,pygame.K_d] and direction != 3:
        direction = 1 
    if event.key in [pygame.K_DOWN,pygame.K_s] and direction != 0:
        direction = 2
    if event.key in [pygame.K_LEFT,pygame.K_a] and direction != 1:
        direction = 3 
    return direction


def handle_keypress(event, direction, change_direction_collected):
    powerup_active = pygame.time.get_ticks() - (change_direction_collected or 0)
    powerup_active = 0 < powerup_active < 5_000 # powerup_active time = 5 seconds
    print("Drunk Powerup aktiv = ", powerup_active)
    if event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
    if powerup_active: 
        direction = handle_powerup_drunk(event, direction) 
    else:
        direction = handle_normal_movement(event, direction) 
    if event.key in [pygame.K_SPACE]: 
        restartenvironment()
    if event.key in [pygame.K_F1]:
        identfy(PLAYERID)
    return direction


powerup_drunk_collected = -9999
immunity_collected = None
while go:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            direction = handle_keypress(event, direction,powerup_drunk_collected) 
               

    # nur bewegen wenn move_counter % snake_speed == 0
    if move_counter % snake_speed == 0:
        # Kopf bewegen
        new_head = snake[0].copy()
        if direction == 0: new_head[1] -= 1
        if direction == 1: new_head[0] += 1
        if direction == 2: new_head[1] += 1
        if direction == 3: new_head[0] -= 1
                
        # Power-Up Kollision
        powerups.spawn_powerup(snake)
        collected = powerups.check_collision(new_head)
        if collected:
            if collected == "speed_boost_x2":
                snake_speed = max(1, snake_speed // 2)
            elif collected == "speed_half":
                snake_speed = snake_speed * 2
            elif collected == "extra_life":
                immunity_collected = pygame.time.get_ticks()
                print("Unverwundbarkeit aktiviert für 5 Sekunden!")
                print(immunity_collected)
            elif collected == "powerup_drunk":
                powerup_drunk_collected = pygame.time.get_ticks() 


        # Spielfeldbegrenzung
        new_head[0] %= (SCREEN_SIZE // particle)
        new_head[1] %= (SCREEN_SIZE // particle)

        # Selbstkollision
        if new_head in snake:
            elapsed = pygame.time.get_ticks() - (immunity_collected or 0)
            if elapsed > 5000:
                game_over_screen()
                restartenvironment()
        
        for snake_id,other_snake in other_snakes.items():
            if new_head in other_snake:
                game_over_screen()

        # Körper verschieben
        if not endgame:
            snake = [new_head] + snake[:-1]

        # Apfel essen
        for i, food in enumerate(feedCordrnd):
            if food == new_head:
                snake.append(snake[-1].copy())
                del feedCordrnd[i]
                score += 10
                break

        # Neuer Apfel
        if len(feedCordrnd) == 0:
            feedCordrnd.append(feedCordsRandomizer())

    if not SINGLE and move_counter % 2 == 0:
        client.queue_send( (json.dumps(snake) + "\n").encode("utf-8")  )

    # Update
    printing()
    while data_from_server := client.receive_now():
        if "WELCOME" in data_from_server:
            print("Eingeloggt ins Spiel.",data_from_server)
            PLAYERID = data_from_server.split()[1]
        else:
            snake_id, other_snakes_data = data_from_server.split(":", 1)
            other_snakes[snake_id] = json.loads(other_snakes_data)
    draw_other_snakes(other_snakes, particle, screen, snake_skins)
        
    powerups.draw(screen)
    pygame.display.update()

    move_counter += 1
    clock.tick(60)  # 60 FPS
