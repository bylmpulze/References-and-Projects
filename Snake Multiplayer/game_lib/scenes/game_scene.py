# MainMenuScene.py

import pygame
from game_lib.snake import SnakeDisplay
from game_lib.food import Food
from game_lib.powerups import PowerUps
from game_lib.helper import quit_game
from server_lib.net_fake_client import FakeClient
from server_lib.net_tcp_client import TCPClient


class GameScene:
    def __init__(self, screen, scene_manager, game_screen_main, play_mode="single"):
        self.screen = screen
        self.scene_manager = scene_manager
        self.game_screen_main = game_screen_main
        self.font = pygame.font.Font(None, 36)
        self.play_mode = "single"

        self.snake_Display = SnakeDisplay(game_screen_main)
        self.food_main = Food(game_screen_main)
        self.power_ups = PowerUps(game_screen_main)
        self.client = self.get_client()
        self.power_ups.add_client(self.client)

        self.food_main.spawn_food(self.snake_Display.get_snake_segments())

    def get_client(self):
        if self.play_mode == "single":
            print("using fake client")
            fc = FakeClient(self.power_ups)
            fc.connect()
            return fc
        try:
            client = TCPClient(self.power_ups)
            client.connect()
        except Exception as E:
            print("Connecting to multiplayer failed! using single player client")
            print("Error", E)
            client = FakeClient(self.power_ups)
            client.connect()

        return client

    def setup(self):
        pass

    def cleanup(self):
        pass

    def update(self):
        pass

    def render(self):
        # draw background
        self.game_screen_main.show_gameWindow.fill(
            self.game_screen_main.background_colour
        )
        self.game_screen_main.draw_topbar()

        # draw snake/food
        self.snake_Display.draw_snake()
        self.food_main.draw_food()
        self.food_main.check_collision(self.snake_Display)

        # snake Movement
        self.snake_Display.snake_movement()
        self.snake_Display.wrap_around()

        self.client.process_messages()
        self.power_ups.draw()
        self.power_ups.check_collision(self.snake_Display)
        self.power_ups.handle_active(self.snake_Display, self.food_main)
        self.snake_Display.move_counter += 1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.snake_Display.snake_direction = (
                self.snake_Display.handle_normal_movement(
                    event, self.snake_Display.snake_direction
                )
            )
            if event.key == pygame.K_ESCAPE:
                quit_game()

    def handle_selection(self):
        pass
