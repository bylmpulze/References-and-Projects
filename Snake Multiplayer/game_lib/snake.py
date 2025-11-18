import pygame
from game_lib.helper import resource_path
import random
from collections import deque

class SnakeDisplay:
    def __init__(self, screen):
        self.screen = screen
        self.segments = deque(self._random_snake_segments(), maxlen=None)
        self.snake_speed = 4  # mehr = langsamer
        self.snake_direction = 0  # 0: up, 1: right, 2: down, 3: left
        self.move_counter = 0
        self.body_img = self._create_snake_body_image()
        self.head_imgs = self._create_snake_head_images()

    def _create_snake_body_image(self):
        body_img = pygame.image.load(resource_path("assets/snakebody.jpg")).convert_alpha()
        body_img = pygame.transform.scale(body_img, (self.screen.particle_size, self.screen.particle_size))
        return body_img

    def _create_snake_head_images(self):
        img = pygame.image.load(resource_path("assets/Snake/Green/snake head.png")).convert_alpha()
        img = pygame.transform.scale(img, (self.screen.particle_size, self.screen.particle_size))
        return {
            2: pygame.transform.rotate(img, 0),    # down
            1: pygame.transform.rotate(img, 90),   # right
            0: pygame.transform.rotate(img, 180),  # up
            3: pygame.transform.rotate(img, 270),  # left
        }

    def snake_movement(self):
        if self.move_counter % self.snake_speed != 0:
            return None

        head = self.segments[0]
        new_head = head.copy()

        if self.snake_direction == 0:  # up
            new_head[1] -= 1
        elif self.snake_direction == 1:  # right
            new_head[0] += 1
        elif self.snake_direction == 2:  # down
            new_head[1] += 1
        elif self.snake_direction == 3:  # left
            new_head[0] -= 1

        self.segments.appendleft(new_head)
        self.segments.pop()
        return new_head

    def handle_normal_movement(self, event, direction):
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

        head = self.segments[0]
        head[0] = head[0] % max_x
        head[1] = head[1] % max_y

    def draw_snake(self):
        ps = self.screen.get_particle_size()
        top = self.screen.get_topbar_height()

        hx, hy = self.segments[0]
        self.screen.display(self.head_imgs[self.snake_direction], (hx * ps, top + hy * ps))

        for x, y in list(self.segments)[1:]:
            self.screen.display(self.body_img, (x * ps, top + y * ps))

    def get_snake_segments(self):
        """ Copy for external use """ 
        return list(self.segments)

    def add_snake_body(self):
        """ Grow by duplicating current tail """
        tail_copy = self.segments[-1].copy()
        self.segments.append(tail_copy)
        print("Snake verlängert:", list(self.segments))

    
    def _random_snake_segments(self):
        max_x = self.screen.get_screen_size_width() // self.screen.get_particle_size()
        max_y = (self.screen.get_screen_size_height() - self.screen.get_topbar_height()) // self.screen.get_particle_size()

      
        x = random.randint(0, max_x - 1)
        y = random.randint(1, max_y - 1)  # ensure y-1 >= 0

        y2 = y + 1 if (y + 1) < max_y else y - 1
        
        return [[x, y], [x, y2]]
