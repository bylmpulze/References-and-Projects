import pygame
import random as randomizer
import os

base_path = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(base_path, "assets")

class PowerUp:
    def __init__(self, particle_size=25):
        self.particle_size = particle_size
        self.active_powerup = None
        self.timer = 0
        self.position = None
        self.duration = 300  # Frames oder Sekunden, je nach Spieltempo
        self.types = ["speed_boost_x2", "speed_half", "extra_life", "powerup_drunk"]
        self.image_files = {
            "speed_boost_x2": "assets/powerup_speed2.png",
            "speed_half": "assets/powerup_speedhalf.png",
            "extra_life": "assets/powerup_extra_life.png",
            "powerup_drunk": "assets/powerup_drunk.jpg"
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
    
    def delete_powerup(self):
            self.position = None
            self.active_powerup = None
            self.timer = 0
            return 
    
 