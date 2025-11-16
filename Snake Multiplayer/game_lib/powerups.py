import pygame



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


        



main = PowerUpMain()
powerup = main.powerupTypes["powerup_speed_boost_x2"]
menu_obj = powerup["menu_att"]
menu_button = powerup["menu_button"]
duration_menu = powerup["duration_menu"]

status = getattr(menu_obj, menu_button)
duration = int(getattr(menu_obj, duration_menu))

print("Status:", status)
print("Dauer:", duration)