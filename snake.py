import pygame
import sys
import random as randomizer
import socket

class Client:
    def __init__(self):
        HOST = "10.35.25.109"  # <- LAN-IP des Server-PCs eintragen
        PORT = 50007
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
    
    def send_data(self, dx,dy):
        print("Sende Daten an Server:", dx, dy)
        self.sock.sendall(f"INPUT {dx} {dy}\n".encode("utf-8"))

particle = 25
snake = [[13, 13], [13, 14]]
direction = 0
feedCordrnd = []

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([1000, 1000])

# === Grafiken ===
food_img = pygame.image.load("assets/apfel2.jpg") # Futerbild
food_img = pygame.transform.scale(food_img, (particle, particle))

body_img = pygame.image.load("assets/snakebody.jpg").convert_alpha() # Schlangenkörper
body_img = pygame.transform.scale(body_img, (particle, particle))

head_img = pygame.image.load("assets/snakehead.jpg").convert_alpha() #Schlangenkopf
head_img = pygame.transform.scale(head_img, (particle, particle))

font = pygame.font.SysFont(None, 40)  # Schriftgröße 40-  wählt Standard

def draw_score():
    score_text = font.render(f"Punkte: {score}", True, (0, 0, 0))  # Schwarz
    screen.blit(score_text, (10, 10))  # Oben links 

#region restart
def restartenvironment ():
    global snake, direction, feedCordrnd, score, endgame
    snake = [[13, 13], [13, 14]]
    direction = 0
    feedCordrnd = [feedCordsRandomizer()]
    score = 0
    endgame = False

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
    
    if SINGLE is None:
        client.send_data(*Coords)  # Sende Kopfposition an Server

def feedCordsRandomizer():
    while True:
        Coord = [randomizer.randint(0, 27), randomizer.randint(0, 27)]
        if Coord not in snake and Coord not in feedCordrnd:
            return Coord


feedCordrnd.append(feedCordsRandomizer())

go = True
endgame = False
score = 0
snake_speed = 1 # mehr = langsamer
move_counter = 0
#end region

#region Game-Loop
SINGLE = None
try:
    client = Client()  # Multiplayer Client initialisieren
except Exception as e:
    print("Verbindung zum Server fehlgeschlagen, starte im Einzelspielermodus.", e)
    SINGLE = True

while go:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key in [pygame.K_UP,pygame.K_w] and direction != 2:
                direction = 0
            if event.key in [pygame.K_RIGHT,pygame.K_d] and direction != 3:
                direction = 1
            if event.key in [pygame.K_DOWN,pygame.K_s] and direction != 0:
                direction = 2
            if event.key in [pygame.K_LEFT,pygame.K_a] and direction != 1:
                direction = 3

    # nur bewegen wenn move_counter % snake_speed == 0
    if move_counter % snake_speed == 0:
        
        new_head = snake[0].copy()
        if direction == 0: new_head[1] -= 1
        if direction == 1: new_head[0] += 1
        if direction == 2: new_head[1] += 1
        if direction == 3: new_head[0] -= 1

        # wenn schlange rand berührt
        new_head[0] %= 40
        new_head[1] %= 40

        # wenn schlange schwanz berührt
        if new_head in snake:
            game_over_screen()  
            restartenvironment()

        # Körper verschieben
        if not endgame:
            snake = [new_head] + snake[:-1]

        # apfelpunkt
        for i, food in enumerate(feedCordrnd):
            if food == new_head:
                snake.append(snake[-1].copy())
                del feedCordrnd[i]
                score += 10
                break

        # Neuer Apfeldings
        if len(feedCordrnd) == 0:
            feedCordrnd.append(feedCordsRandomizer())

    # Update
    printing()
    pygame.display.update()

    move_counter += 1
    clock.tick(60)  # 60 FPS

    #region Multiplayer 