import pygame
import random as randomizer
import os
import sys


class PowerUp:
    def __init__(self, particle_size=25):
        self.particle_size = particle_size
        self.position = None
        self.active_powerup = None
        self.powerup_spawned = True
        self.powerup_spawntime = 0
        self.powerup_despawntime = 0
        self.spawn_powerup_delay = 0
        self.spawn_duration = 2000  # Frames oder Sekunden, je nach Spieltempo
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
            img = pygame.transform.scale(self.resource_path(img), (self.particle_size, self.particle_size))
            self.images[key] = img
        
    def resource_path(self, rel_path: str) -> str:
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, rel_path)


    def spawn_powerup(self, snake): # powerup spawn randomizer
        current_frametime = pygame.time.get_ticks()
        print ("current frametime = ", current_frametime)
        if self.position is None and (current_frametime - self.powerup_despawntime) > self.spawn_duration: 
            while True:
                coord = [randomizer.randint(0, 27), randomizer.randint(0, 27)]
                if coord not in snake:
                    self.position = coord
                    self.active_powerup = randomizer.choice(self.types)
                    self.powerup_spawned = True
                    print("powerup activ")
                    print("status of powerup_spawned",  self.powerup_spawned)
                    self.powerup_spawntime = pygame.time.get_ticks() 
                    return True
                  
    def draw(self, screen): # Show powerup
        if self.position and self.active_powerup:
            pos_px = [self.position[0] * self.particle_size, self.position[1] * self.particle_size]
            screen.blit(self.images[self.active_powerup], pos_px)

    def check_collision(self, snake_head): #checks if the powerup got picked up
        if self.position and snake_head == self.position:
            collected = self.active_powerup
            self.delete_powerup()
            return collected
        return None
    
    def delete_powerup(self):
        if self.powerup_spawned is True:
            self.position = None
            self.active_powerup = None
            self.timer = 0
            self.powerup_despawntime = pygame.time.get_ticks()
            self.powerup_spawned = False
            print("powerup despawntime: " , self.powerup_despawntime)

    
 