import pygame
import sys
import random as randomizer
import socket
import Snake_Functions
import Powerups
import os

#class Client:
    #def __init__(self):
        #HOST = "10.35.25.109"  # <- LAN-IP des Server-PCs eintragen
        #PORT = 50007
        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.connect((HOST, PORT))
    
    #def send_data(self, dx,dy):
        #print("Sende Daten an Server:", dx, dy)
        #self.sock.sendall(f"INPUT {dx} {dy}/n".encode("utf-8"))

#powerUps
class PowerUps:
    def __init__(self, particle_size=25):
        self.particle_size = particle_size
        self.active_powerup = None
        self.timer = 0
        self.position = None
        self.duration = 300  # Frames oder Sekunden, je nach Spieltempo
        self.types = ["speed_boost_x2", "speed_half", "extra_life"]

        base_path = os.path.dirname(os.path.abspath(__file__))
        asset_path = os.path.join(base_path, "assets")

        self.image_files = {
            "speed_boost_x2": os.path.join(asset_path, "powerup_speed2.png"),
            "speed_half": os.path.join(asset_path, "powerup_speedhalf.png"),
            "extra_life": os.path.join(asset_path, "powerup_extra_life.png")
        }


        self.images = {}
        for key, file in self.image_files.items():
            img = pygame.image.load(file).convert_alpha()
            img = pygame.transform.scale(img, (self.particle_size, self.particle_size))
            self.images[key] = img

    def spawn_powerup(self, snake): # powerup spawn randomizer
        if self.position is None and randomizer.random() < 0.01:  # ~1% Chance pro Frame
            while True:
                coord = [randomizer.randint(0, 27), randomizer.randint(0, 27)]
                if coord not in snake:
                    self.position = coord
                    self.active_powerup = randomizer.choice(self.types)
                    break

    def draw(self, screen): # Show powerup
        if self.position and self.active_powerup:
            pos_px = [self.position[0] * self.particle_size, self.position[1] * self.particle_size]
            screen.blit(self.images[self.active_powerup], pos_px)

    def check_collision(self, snake_head): #checks if the powerup got picked up
        if self.position and snake_head == self.position:
            collected = self.active_powerup
            self.position = None
            self.active_powerup = None
            self.timer = 0
            return collected
        return None


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
screen = pygame.display.set_mode([1000, 1000])
clock = pygame.time.Clock()
powerups = PowerUps(particle_size=particle)

base_path = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(base_path, "assets")

food_img = pygame.image.load(os.path.join(asset_path, "apfel2.jpg"))  # Futterbild
food_img = pygame.transform.scale(food_img, (particle, particle))

body_img = pygame.image.load(os.path.join(asset_path, "snakebody.jpg")).convert_alpha()
body_img = pygame.transform.scale(body_img, (particle, particle))

head_img = pygame.image.load(os.path.join(asset_path, "snakehead.jpg")).convert_alpha()
head_img = pygame.transform.scale(head_img, (particle, particle))

font = pygame.font.SysFont(None, 40)

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
    
    #if SINGLE is None:
        #client.send_data(*Coords)  # Sende Kopfposition an Server

def feedCordsRandomizer():
    while True:
        Coord = [randomizer.randint(0, 27), randomizer.randint(0, 27)]
        if Coord not in snake and Coord not in feedCordrnd:
            return Coord


feedCordrnd.append(feedCordsRandomizer())

#end region

#region Game-Loop
#SINGLE = None
#try:
    #client = Client()  # Multiplayer Client initialisieren
#except Exception as e:
    #print("Verbindung zum Server fehlgeschlagen, starte im Einzelspielermodus.", e)
    #SINGLE = True

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
            if event.key in [pygame.K_SPACE]: 
                restartenvironment()

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
                endgame = False

        # Spielfeldbegrenzung
        new_head[0] %= 40
        new_head[1] %= 40

        # Selbstkollision
        if new_head in snake:
            game_over_screen()
            restartenvironment()

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

    # Update
    printing()
    powerups.draw(screen)
    pygame.display.update()

    move_counter += 1
    clock.tick(60)  # 60 FPS

    #region Multiplayer 