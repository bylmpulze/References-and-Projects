import pygame
from game_lib.helper import resource_path

class PowerUp:
    def __init__(self, img, x, y, running_duration, sound_file=None,onetime = False) -> None:
        img = pygame.image.load(resource_path(img)).convert_alpha()
        self.img = pygame.transform.scale(img, ((25, 25)))

        self.fadeout_started = False

        self.x = int(x)
        self.y = int(y)
        self.id = None
        self.onetime = onetime
        self.running_duration = running_duration

        self.start = None
        self._send = False
        self.last = None
        self.volume = 1.0

        if sound_file is not None:
            self.sound_file = pygame.mixer.Sound(resource_path(sound_file))
        else:
            self.sound_file = sound_file
    
    def set_volume(self, vol: float):
        self.volume = vol
        if self.sound_file:
            self.sound_file.set_volume(vol)

    def add_client(self, client):
        self.client = client


    def effect(self, snake, food):
        pass
        
    def activate(self, pw_id):
        self.start = pygame.time.get_ticks()
        self.client.power_up_collected(int(pw_id))
        if self.sound_file is not None:
            self.sound_file.play()

    def check_collision(self, snake):
        return [self.x, self.y] == snake.get_head_cords()

    def draw(self, screen):
        if self.start is not None:
            return
        cell = screen.get_particle_size()
        x = int(self.x) * cell
        y = screen.get_topbar_height() + int(self.y) * cell
        screen.display(self.img, (x, y))  # statt screen.blit


class MagnetPowerUp(PowerUp):
    def __init__(self, x, y) -> None:
        img = "assets/Items/powerup magnet.png"
        sound_file = "assets/Sounds/magnet.flac"
        super().__init__(img, x, y, 1000, sound_file)

    def effect(self, snake, food):
        if self.last is None:
            self.last = pygame.time.get_ticks()

        now = pygame.time.get_ticks()
        if (now - self.last) < 100:
            return

        snake_x, snake_y = snake.get_head_cords()
        if food.foodcoords[0][0] < snake_x:
            food.foodcoords[0][0] += 1
        if food.foodcoords[0][0] > snake_x:
            food.foodcoords[0][0] -= 1
        if food.foodcoords[0][1] < snake_y:
            food.foodcoords[0][1] += 1
        if food.foodcoords[0][1] > snake_y:
            food.foodcoords[0][1] -= 1

        self.last = pygame.time.get_ticks()


class SpeedupPowerUp(PowerUp):
    def __init__(self, x, y) -> None:
        img = "assets/Items/powerup speed.png"
        super().__init__(img, x, y, 1000)
    
    def effect(self,snake,food):
        if self.last is not None:
            return
        snake_speed = snake.get_snake_speed()
        snake.snake_speed = snake_speed / 2
        print(snake_speed)
        self.last = pygame.time.get_ticks()


class ExtraLifePowerUp(PowerUp):
    def __init__(self, x, y) -> None:
        img = "assets/Items/powerup extra life.png"
        super().__init__(img, x, y, 1000)


class SlowDownPowerUp(PowerUp):
    def __init__(self, x, y) -> None:
        img = "assets/Items/powerup slow.png"
        super().__init__(img, x, y, 1000)


class DrunkPowerUp(PowerUp):
    def __init__(self, x, y) -> None:
        img = "assets/Items/powerup drunk.png"
        super().__init__(img, x, y, 1000)


class JumpPowerUp(PowerUp):
    def __init__(self, x, y) -> None:
        img = "assets/Items/GET_IMG_HERE!!!!.png"
        super().__init__(img, x, y, 1000)


POWERUP_CLASS_MAP = {
    "speed_boost_x2": SpeedupPowerUp,
    "speed_half": SlowDownPowerUp,
    "extra_life": ExtraLifePowerUp,
    "powerup_drunk": DrunkPowerUp,
    "powerup_magnet": MagnetPowerUp,  # once you add it
    "powerup_jump": JumpPowerUp,
}


class PowerUps:
    def __init__(self, screen, scene_manager) -> None:
        self.uncollected_power_ups = {}
        self.active_power_ups = {}
        self.screen = screen
        self.client = None
        self.settings = scene_manager.settings

    def add_client(self, client):
        self.client = client

    def add(self, pw_id, x, y, pw_type):
        cls = POWERUP_CLASS_MAP.get(pw_type)
        if cls is None:
            raise ValueError(f"Unknown power-up: {pw_type}")

        obj = cls(x, y)
        obj.add_client(self.client)
        obj.set_volume(self.settings.volume)
        self.uncollected_power_ups[pw_id] = obj

    def draw(self):
        for pw_id, pw_up in self.uncollected_power_ups.items():
            pw_up.draw(self.screen)

    def check_collision(self, snake):
        for pw_id, v in self.uncollected_power_ups.items():
            if v.check_collision(snake):
                v.activate(pw_id)
                self.active_power_ups[pw_id] = v
                self.client.power_up_collected(pw_id)

        self.uncollected_power_ups = {
            k: v
            for k, v in self.uncollected_power_ups.items()
            if k not in self.active_power_ups
        }

    def handle_active(self, snake, food):
        now = pygame.time.get_ticks()
        for pw_id, pw_up in self.active_power_ups.items():
            if pw_up.start is None:
                continue

            end_time = pw_up.start + pw_up.running_duration
            time_left = end_time - now

            # Fade-out: last 1000 ms
            if 0 < time_left <= 1000:
                if pw_up.sound_file and not pw_up.fadeout_started :
                    pw_up.sound_file.fadeout(time_left)
                    pw_up.fadeout_started = True

            if time_left > 0:
                pw_up.effect(snake, food)
                

  


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
