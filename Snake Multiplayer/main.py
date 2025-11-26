import pygame
from game_lib.game_render import GameScreen
from game_lib.scenes.scene_manager import SceneManager
from game_lib.scenes.main_menu import MainMenuScene
from game_lib.scenes.settings_menu import SettingsMenuScene
from game_lib.scenes.game_scene import GameScene
from game_lib.scenes.multiplayer_scene import MultiplayerScene
from game_lib.scenes.powerup_settings import PowerupSettingsScene

pygame.init()  
game_screen_main = GameScreen(800)
clock = pygame.time.Clock()

scene_manager = SceneManager(game_screen_main.show_gameWindow)
main_menu = MainMenuScene(game_screen_main.show_gameWindow,scene_manager)
multiplayer_scene = MultiplayerScene(game_screen_main.show_gameWindow,scene_manager)
settings_menu = SettingsMenuScene(game_screen_main.show_gameWindow,scene_manager)
game_scene = GameScene(game_screen_main.show_gameWindow,scene_manager, game_screen_main)
powerup_settings_scene = PowerupSettingsScene(game_screen_main.show_gameWindow,scene_manager)

scene_manager.add_scene("MainMenu", main_menu)
scene_manager.add_scene("SettingsScene",settings_menu)
scene_manager.add_scene("GameScene",game_scene)
scene_manager.add_scene("MultiplayerScene",multiplayer_scene)
scene_manager.add_scene("powerup_settings",powerup_settings_scene)

scene_manager.switch_scene("powerup_settings")

while True:
    scene_manager.run_current_scene()
    pygame.display.update()
    clock.tick(60)




