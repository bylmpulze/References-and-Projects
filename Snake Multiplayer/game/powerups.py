import pygame
import random as randomizer
import os
import sys
import game.constants as constants



def resource_path(rel_path: str) -> str:
    try:
        base_path = sys._MEIPASS
        base_path = os.path.join(base_path, "Snake Multiplayer/game")
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, rel_path)

class PowerUpConfig:
    def __init__(self):
        self.speed_boost_x2 = False
        self.speed_half = False
        self.extra_life = False  
        self.powerup_magnet = False
        self.powerup_drunk = True
        self.powerup_drunk_duration = 0 # Dauer - umgekehrte steuerung (nicht fertig)
        self.powerup_magnet_duration = 1500 #Dauer Apfel heranziehen (nicht fertig)
        self.speed_boost_x2_duration = 5000 # Dauer - doppelte Geschwindigkeit  (1000 = 1 sec) (nicht fertig)
        self.extra_life_duration = 1500 #1.5 sekunden Unverwundbarkeit ( 1000 = 1 sec) (fertig)
        self.power_up_activ_time = 5000 #löscht powerup  (1000 = 1 sec) (fertig)
        self.spawn_duration = 1000 # spawnzeit nach letztem Powerup ( 1000 = 1 sec) (fertig)
        
        


powerupconfig = PowerUpConfig ()

class PowerUp:
    def __init__(self, particle_size=25):
        self.particle_size = particle_size
        self.position = None
        self.active_powerup = None
        self.powerup_spawned = True
        self.powerup_spawntime = 0
        self.powerup_despawntime = 0
        self.spawn_powerup_delay = 0
        self.config = powerupconfig
        self.types = ["speed_boost_x2", "speed_half", "extra_life", "powerup_drunk", "powerup_magnet"]
        self.image_files = {
            "speed_boost_x2": "assets/powerup_speed2.png",
            "speed_half": "assets/powerup_speedhalf.png",
            "extra_life": "assets/powerup_extra_life.png",
            "powerup_drunk": "assets/powerup_drunk.jpg",
            "powerup_magnet": "assets/powerup_magnet.webp"
        }

        # Laden MIT resource_path und korrekt skalieren
        self.images = {}
        for key, rel_file in self.image_files.items():
            img_path = resource_path(rel_file)  # absoluter Pfad (MEIPASS-fähig)
            img = pygame.image.load(img_path).convert_alpha()  # Surface laden
            img = pygame.transform.scale(img, (self.particle_size, self.particle_size))  # Surface skalieren
            self.images[key] = img
        

    def spawn_powerup(self, snake): # powerup spawn randomizer
        global powerupconfig
        current_frametime = pygame.time.get_ticks()
        if self.position is None and (current_frametime - self.powerup_despawntime) > powerupconfig.spawn_duration:  #prüft ob kein Powerup derzeit aktiv ist und wann das letzte respawnt wurde
            available_powerups = [
                l for l in self.types if getattr(self.config, l)
            ]
            if not available_powerups:
                print(" Keine Power-ups Aktiviert!")
                return False
            
            while True:
                coord = [randomizer.randint(0, 27), randomizer.randint(0, 27)]
                if coord not in snake:
                    self.position = coord
                    break

            self.active_powerup = randomizer.choice(available_powerups)
            self.powerup_spawned = True
            self.powerup_spawntime = pygame.time.get_ticks()
                  
    def draw(self, screen): # Show powerup
        if self.position and self.active_powerup:
            pos_px = [self.position[0] * self.particle_size, self.position[1] * self.particle_size + constants.TOPBAR_HEIGHT]
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


    
 