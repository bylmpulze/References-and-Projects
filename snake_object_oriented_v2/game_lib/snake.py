import pygame
import os
import sys


#region Snakedisplay
class SnakeDisplay:
    def __init__(self,screen):
        self.snake_head = [[13, 13], [13, 14]]
        self.snake_body = 0
        self.snake_cords = 0
        self.snake_speed = 4  # mehr = langsamer
        self.snake_direction = 0
        self.move_counter = 0
        self.body_img = ""
        self.head_img = ""
        self.screen = screen


    def get_SnakeImages(self):    
        self.body_img = pygame.image.load(resource_path("assets/snakebody.jpg")).convert_alpha()
        self.body_img = pygame.transform.scale(self.body_img, (self.screen.particle_size, self.screen.particle_size))
        self.head_img = pygame.image.load(resource_path("assets/snakehead.jpg")).convert_alpha()
        self.head_img = pygame.transform.scale(self.head_img, (self.screen.particle_size, self.screen.particle_size))



    def snake_movement(self):
        if self.move_counter % self.snake_speed == 0:
            new_head = self.snake_head[0].copy()

            if self.snake_direction == 0: new_head[1] -= 1
            if self.snake_direction == 1: new_head[0] += 1
            if self.snake_direction == 2: new_head[1] += 1
            if self.snake_direction == 3: new_head[0] -= 1

            self.snake_head.insert(0, new_head)
            self.snake_head.pop()

            return new_head
        
    def handle_normal_movement(self,event, direction):
        if event.key in [pygame.K_UP, pygame.K_w] and direction != 2:
            direction = 0 
        if event.key in [pygame.K_RIGHT, pygame.K_d] and direction != 3:
            direction = 1 
        if event.key in [pygame.K_DOWN, pygame.K_s] and direction != 0:
            direction = 2
        if event.key in [pygame.K_LEFT, pygame.K_a] and direction != 1:
            direction = 3 
        return direction
    
    def wrap_around(self):
        max_x = self.screen.screen_size_width // self.screen.particle_size
        max_y = (self.screen.screen_size_height - self.screen.topbar_height) // self.screen.particle_size

        head = self.snake_head[0]

        # x Koordinate
        head[0] = head[0] % max_x

        # y Koordinate 
        head[1] = head[1] % max_y

    def draw_snake(self):
        # Kopf 
        head_x, head_y = self.snake_head[0]
        self.screen.show_gameWindow.blit(self.head_img, (head_x * self.screen.particle_size, self.screen.topbar_height + head_y * self.screen.particle_size))
        #körper
        for segment in self.snake_head[1:]:
            x, y = segment
            self.screen.show_gameWindow.blit(self.body_img, (x * self.screen.particle_size, self.screen.topbar_height + y * self.screen.particle_size))
        
def resource_path(rel_path: str) -> str:
    try:
        base_path = sys._MEIPASS
        base_path = os.path.join(base_path, "snake_object_oriented_v2")
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, rel_path)
        
