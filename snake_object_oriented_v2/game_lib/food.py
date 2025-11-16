import pygame
from .snake import resource_path
import random

class FoodMain:
    def __init__(self,screen):
        self.screen = screen
        self.foodcoords = []
        self.foodImage = self.create_foodImage()
        self.grid_width = 25
        self.grid_height = 25



    def create_foodImage(self):
        foodImage = pygame.image.load(resource_path("assets/apfel2.jpg"))
        foodImage = pygame.transform.scale(foodImage, (self.screen.get_particle_size(), self.screen.get_particle_size()))
        return foodImage

    def spawn_food(self, snake_coords):
        while True:
            x = random.randint(0, self.grid_width - 1)
            y =random.randint(0,self.grid_height - 1)
            if [x, y] not in snake_coords:
                self.foodcoords = [[x, y]]
                break


    def draw_food(self):
        for a in self.foodcoords:
            x = a[0] * self.screen.get_particle_size()
            y = a[1] * self.screen.get_particle_size() + self.screen.get_topbar_height()
            self.screen.display(self.foodImage, (x, y))
