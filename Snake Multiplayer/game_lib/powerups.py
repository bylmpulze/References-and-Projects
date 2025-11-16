import pygame
from game_lib.helper import resource_path

#region Config
class PowerUpConfig:
    def __init__(self):
        self.powerup_speed_boost_x2 = True
        self.powerup_speed_half = False
        self.powerup_immunity = False  
        self.powerup_magnet = False
        self.powerup_change_direction = False

        self.powerup_change_direction_duration = 1000 #Dauer - umgekehrte steuerung  (1000 = 1 sec) 
        self.powerup_magnet_duration = 1000 #Dauer Apfel heranziehen  (1000 = 1 sec) 
        self.powerup_speed_boost_x2_duration = 1500 # Dauer - doppelte Geschwindigkeit  (1000 = 1 sec) 
        self.powerup_speed_half_duration = 1000 # Dauer - halbierte Geschwindigkeit  (1000 = 1 sec) 
        self.powerup_immunity_duration = 5000 #Dauer - Unverwundbarkeit ( 1000 = 1 sec) 

        

#region Main
class PowerUpMain:
    def __init__(self, particle_size=25):
        self.particle_size = particle_size
        self.position = None
        self.active_powerup = None
        self.powerup_spawned = True
        self.powerup_spawntime = 0
        self.powerup_despawntime = 0
        self.spawn_powerup_delay = 0
        self.power_up_activ_time = 5000 #löscht powerup  (1000 = 1 sec) 
        self.spawn_duration = 1000 # spawnzeit nach letztem Powerup ( 1000 = 1 sec) 
        self.config = PowerUpConfig ()
        self.menu = PowerupSettingsMenu() 
        self.powerupTypes = {
            "powerup_speed_boost_x2": {
                "menu_att": self.menu,
                "menu_button": "settingsMenu_speedx2",
                "duration_menu": "settingsMenu_speedx2_duration",
                "config_": self.config,
                "config_activ": "powerup_change_direction",
                "config_duration": "speed_boost_x2_duration",
                "image": "assets/powerup_speed2.png"
            },
            "powerup_speed_half": {
                "menu_att": self.menu,
                "menu_button": "settingsMenu_speedHalf",
                "duration_menu": "settingsMenu_speedHalf_duration",
                "config_att": self.config,
                "config_duration": "powerup_speed_half_duration",
                "image": "assets/powerup_speedhalf.png"
            },
            "powerup_magnet": {
                "menu_att": self.menu,
                "menu_button": "settingsMenu_powerup_magnet",
                "duration_menu": "settingsMenu_magnet_duration",
                "config_att": self.config,
                "config_activ": "powerup_change_direction",
                "config_duration": "powerup_magnet_duration",
                "image": "assets/powerup_magnet.webp"
            },
            "powerup_change_direction": {
                "menu_att": self.menu,
                "menu_button": "settingsMenu_change_direction",
                "duration_menu": "settingsMenu_change_direction_duration",
                "config_att": self.config,
                "config_activ": "powerup_change_direction",
                "config_duration": "powerup_change_direction_duration",
                "image": "assets/powerup_drunk.jpg"
            },
            "powerup_immunity": {
                "menu_att": self.menu,
                "menu_button": "settingsMenu_powerup_immunity",
                "duration_menu": "settingsMenu_powerup_immunity",
                "config_att": self.config,
                "config_activ": "powerup_immunity",
                "config_duration": "powerup_immunity_duration",
                "image": "assets/powerup_extra_life.png"
            }
        }





#region SettingsMenu
class PowerupSettingsMenu():
    def __init__(self):
        self.config = PowerUpConfig()
        self.settingsMenu_powerup_magnet = False
        self.settingsMenu_speedx2 = True
        self.settingsMenu_speedHalf = False
        self.settingsMenu_immunity = False
        self.settingsMenu_magnet_duration = "1000"
        self.settingsMenu_speedx2_duration = "1500"
        self.settingsMenu_speedHalf_duration = "1000"
        self.settingsMenu_immunity_duration = "1000"
        self.settingsMenu_change_direction_duration = "1000"


class PowerUp:
    def __init__(self,img,x,y,running_duration) -> None:
    
        img = pygame.image.load(resource_path(img)).convert_alpha()
        self.img = pygame.transform.scale(img, ((25, 25)))
        self.x = int(x)
        self.y = int(y)
        self.running_duration = running_duration

        self.start = None

    def effect(self,snake,food):
        pass

    def activate(self,snake):
        self.start = pygame.time.get_ticks()
        
    def check_collision(self,snake):        
        return [self.x,self.y] in snake.get_snake_headcords()


    def draw(self, screen):
        if self.start is not None:
            return
        cell = screen.get_particle_size()
        x = int(self.x) * cell
        y = screen.get_topbar_height() + int(self.y) * cell
        screen.display(self.img, (x, y))  # statt screen.blit


class GrowPowerUp(PowerUp):
    def __init__(self,x,y) -> None:
        img = "assets/powerup_magnet.webp"
        super().__init__(img,x,y, 1000)     

    def effect(self,snake,food):
        snake_x,snake_y = snake.get_snake_headcords()[0]
        if food.foodcoords[0][0] < snake_x:
            food.foodcoords[0][0] += 1
        if food.foodcoords[0][0] > snake_x:
            food.foodcoords[0][0] -= 1
        if food.foodcoords[0][1] < snake_y:
            food.foodcoords[0][1] += 1
        if food.foodcoords[0][1] > snake_y:
            food.foodcoords[0][1] -= 1
         

class PowerUps:
    def __init__(self,screen) -> None:
        self.dct = {}
        self.screen = screen

    def add(self, pw_id,x,y,pw_type):
        self.dct[pw_id] = GrowPowerUp(x,y)

    def draw(self):
        for pw_id,pw_up in self.dct.items():
            pw_up.draw(self.screen)
    
    def check_collison(self,snake):

        for k,v in self.dct.items():
            if v.check_collision(snake):
                v.activate(snake)
               

    def handle_active(self,snake,food):
        now = pygame.time.get_ticks()
        for k,v in self.dct.items():
            if v.start is None:
                continue
            
            if (v.start + v.running_duration) < now:
                continue 

            v.effect(snake,food)
            


if __name__ == "__main__":

    main = PowerUpMain()
    powerup = main.powerupTypes["powerup_speed_boost_x2"]
    menu_obj = powerup["menu_att"]
    menu_button = powerup["menu_button"]
    duration_menu = powerup["duration_menu"]

    status = getattr(menu_obj, menu_button)
    duration = int(getattr(menu_obj, duration_menu))

    print("Status:", status)
    print("Dauer:", duration)