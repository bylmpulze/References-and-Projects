import pygame
from .snake import resource_path
import random

class Food:
    def __init__(self,screen,scene_manager):
        self.screen = screen
        self.foodcoords = []
        self.foodImage = self.create_foodImage()
        self.grid_width = 25
        self.grid_height = 25
        self.settings = scene_manager.settings
        self.sound_file = pygame.mixer.Sound(resource_path('assets/sounds/food.mp3'))
        self.sound_file.set_volume(self.settings.volume)    


    def create_foodImage(self):
        foodImage = pygame.image.load(resource_path("assets/Items/apple.png"))
        foodImage = pygame.transform.scale(
            foodImage,
            (self.screen.get_particle_size(), self.screen.get_particle_size())
        )
        foodImage.convert_alpha()

        return foodImage

    def spawn_food(self, snake_coords):
        while True:
            x = random.randint(0, self.grid_width - 1)
            y =random.randint(0,self.grid_height - 1)
            if [x, y] not in snake_coords:
                self.foodcoords = [[x, y]]
                break
    
    def get_foodcords(self):
        return self.foodcoords
    
    def check_collision(self, snake): 
        foodcords = self.get_foodcords()[0]
        snake_coords = snake.get_snake_segments()
        if foodcords in snake_coords:
            self.on_eaten(snake,snake_coords)
        

    def draw_food(self):
        for a in self.foodcoords:
            x = a[0] * self.screen.get_particle_size()
            y = a[1] * self.screen.get_particle_size() + self.screen.get_topbar_height()
            self.screen.display(self.foodImage, (x, y))

    def on_eaten(self,snake,snake_coords) -> None:
        """
        Sound etc.
        """
        self.sound_file.play()
        self.screen.get_score()
        self.screen.add_score(10)
        print("Kollision, neues Food spawnen!")
        self.spawn_food(snake_coords)
        snake.add_snake_body()
        
