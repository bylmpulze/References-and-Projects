import pygame
from game_lib.helper import resource_path
import random


#region Snakedisplay
class SnakeDisplay:
    def __init__(self,screen):
        self.screen = screen
        self.snake_head = self.get_random_snake_cords()
        self.snake_body = []
        self.snake_cords = 0
        self.snake_speed = 4  # mehr = langsamer
        self.snake_direction = 0
        self.move_counter = 0
        self.body_img = self.create_snake_body_image()
        self.head_imgs = self.create_snake_head_images()

    def create_snake_body_image(self):    
        body_img = pygame.image.load(resource_path("assets/snakebody.jpg")).convert_alpha()
        body_img = pygame.transform.scale(body_img,(self.screen.particle_size, self.screen.particle_size))
        return body_img
    
    def create_snake_head_images(self):    
        
        img = pygame.image.load(resource_path("assets/Snake/Green/snake head.png")).convert_alpha()
        img = pygame.transform.scale(img, ((self.screen.particle_size, self.screen.particle_size)))
        return {
            2:   pygame.transform.rotate(img, 0),
            1:  pygame.transform.rotate(img, 90),
            0: pygame.transform.rotate(img, 180),
            3: pygame.transform.rotate(img, 270)
        }

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
        max_x = self.screen.get_screen_size_width() // self.screen.get_particle_size()
        max_y = (self.screen.get_screen_size_height() - self.screen.get_topbar_height()) // self.screen.get_particle_size()

        head = self.snake_head[0]

        # x Koordinate
        head[0] = head[0] % max_x

        # y Koordinate 
        head[1] = head[1] % max_y

    def draw_snake(self):
        # Kopf 
        head_x, head_y = self.snake_head[0]
        
        self.screen.display(self.head_imgs[self.snake_direction], (head_x * self.screen.get_particle_size(), self.screen.get_topbar_height() + head_y * self.screen.get_particle_size()))
        #körper
        for segment in self.snake_head[1:]:
            x, y = segment
            self.screen.display(self.body_img, (x * self.screen.get_particle_size(), self.screen.get_topbar_height() + y * self.screen.get_particle_size()))
    
    def get_snake_headcords(self):
        return self.snake_head

    def get_snake_bodycords(self):
        return self.snake_body
    
    def add_snake_body(self):
        self.snake_head.append(self.snake_head[-1].copy())
        print("Snake verlängert:", self.snake_head)

    def get_random_snake_cords(self):

        max_x = self.screen.get_screen_size_width() // self.screen.get_particle_size()
        max_y = (self.screen.get_screen_size_height() - self.screen.get_topbar_height()) // self.screen.get_particle_size()

        x = random.randint(0, max_x)
        y = random.randint(0, max_y)

        return [[x,y],[x,y+1]]
        


        
