import os
import pygame
import sys
import json
import random as randomizer
import game.snake_functions as snake_functions
from game.powerups import PowerUp
from game.client import Client, FakeClient
from game.snake_functions import draw_other_snakes
from game.selector_screen import menu_screen

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
flags = pygame.SCALED | pygame.DOUBLEBUF
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE), flags, vsync=1)
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
    global snake, direction, feedCordrnd, score, endgame, powerup_active, snake_speed
    snake = [[13, 13], [13, 14]]
    direction = 0
    feedCordrnd = [feedCordsRandomizer()]
    score = 0
    endgame = False
    powerup_active = -9999
    powerups.delete_powerup()
    snake_speed = 4

# --- Fester Logik-Takt + Interpolation ---
STEP_DT = 0.10  # 10 Moves/s (Gitter-Updates)
accumulator = 0.0



client = FakeClient()

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




        

# Speichere vorherigen und aktuellen Schlangenzustand für Interpolation
prev_snake = [seg.copy() for seg in snake]
curr_snake = [seg.copy() for seg in snake]

def draw_score():
    score_text = font.render(f"Punkte: {score}", True, (0, 0, 0)) # Schwarz
    screen.blit(score_text, (10, 10)) # Oben links 


def logic_step():
    global snake, prev_snake, curr_snake, score, endgame, feedCordrnd, direction, snake_speed
    # Vor Zustand sichern
    prev_snake = [seg.copy() for seg in curr_snake]

    # Kopf berechnen (Grid-Schritt)
    new_head = curr_snake[0].copy()
    if direction == 0: new_head[1] -= 1
    if direction == 1: new_head[0] += 1
    if direction == 2: new_head[1] += 1
    if direction == 3: new_head[0] -= 1

    # Wrap um das Grid
    new_head[0] %= (SCREEN_SIZE // particle)
    new_head[1] %= (SCREEN_SIZE // particle)

    # Selbstkollision -> Restart Screen + Reset
    if new_head in curr_snake:
        game_over_screen()
        restartenvironment()
        # Nach Reset auch interpolationszustände neu setzen
        reset_states()
        return

    # Körper schieben
    curr_snake = [new_head] + curr_snake[:-1]

    # Apfel essen
    for i, food in enumerate(feedCordrnd):
        if food == new_head:
            curr_snake.append(curr_snake[-1].copy())
            del feedCordrnd[i]
            score += 10
            break

    # Apfel nachspawnen
    if len(feedCordrnd) == 0:
        feedCordrnd.append(feedCordsRandomizer())

    # Power-Ups
    powerups.spawn_powerup(curr_snake)
    collected = powerups.check_collision(new_head)
    if collected:
        if collected == "speed_boost_x2":
            # An festen Takt anpassen: optional STEP_DT halbieren statt Snake-Speed
            snake_speed = max(1, snake_speed // 2)
        elif collected == "speed_half":
            snake_speed = snake_speed * 2
        elif collected == "extra_life":
            endgame = False

def reset_states():
    global prev_snake, curr_snake
    prev_snake = [seg.copy() for seg in snake]
    curr_snake = [seg.copy() for seg in snake]

reset_states()

def render_interpolated(alpha: float):
    screen.fill((255, 255, 255))

    # Apfel zeichnen
    for a in feedCordrnd:
        Coords = [a[0] * particle, a[1] * particle]
        screen.blit(food_img, (Coords[0], Coords[1]))

    # Schlange: position zwischen prev und curr interpolieren
    for i, (prev_seg, curr_seg) in enumerate(zip(prev_snake, curr_snake)):
        x = (prev_seg[0] * (1 - alpha) + curr_seg[0] * alpha) * particle
        y = (prev_seg[1] * (1 - alpha) + curr_seg[1] * alpha) * particle
        if i == 0:
            # Kopfrotation anhand Richtung (vorab vorbereitete Rotationen empfohlen)
            if direction == 0:
                rotated_head = pygame.transform.rotate(head_img, 0)
            elif direction == 1:
                rotated_head = pygame.transform.rotate(head_img, 270)
            elif direction == 2:
                rotated_head = pygame.transform.rotate(head_img, 180)
            elif direction == 3:
                rotated_head = pygame.transform.rotate(head_img, 90)
            screen.blit(rotated_head, (x, y))
        else:
            screen.blit(body_img, (x, y))

    draw_score()


    powerups.draw(screen)
    pygame.display.update()

# --- Game Loop ---
current_time_ms = pygame.time.get_ticks()
while go:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.key in [pygame.K_UP, pygame.K_w] and direction != 2:
                direction = 0
            if event.key in [pygame.K_RIGHT, pygame.K_d] and direction != 3:
                direction = 1
            if event.key in [pygame.K_DOWN, pygame.K_s] and direction != 0:
                direction = 2
            if event.key in [pygame.K_LEFT, pygame.K_a] and direction != 1:
                direction = 3
            if event.key in [pygame.K_SPACE]:
                restartenvironment()
                reset_states()

    new_time_ms = pygame.time.get_ticks()
    frame_time = (new_time_ms - current_time_ms) / 1000.0
    current_time_ms = new_time_ms

    # (Optional) Clamp, um Extremwerte zu vermeiden
    if frame_time > 0.25:
        frame_time = 0.25

    accumulator += frame_time
    while accumulator >= STEP_DT:
        logic_step()
        accumulator -= STEP_DT

    alpha = accumulator / STEP_DT
    render_interpolated(alpha)

    # Genaue Taktung (alternativ clock.tick(60))
    clock.tick_busy_loop(60)
