import sys
import pygame
from game_lib.game_render import GameScreen
from game_lib.snake import SnakeDisplay
from game_lib.food import Food
from game_lib.helper import quit_game


pygame.init()  
game_screen_main = GameScreen(800)
snake_Display = SnakeDisplay(game_screen_main)  
food_main = Food(game_screen_main)

#init pictures - snake/food
snake_Display.create_snake_body_image()
snake_Display.create_snake_head_image()
#food_Display.create_foodImage()
clock = pygame.time.Clock()
food_main.spawn_food(snake_Display.get_snake_headcords())


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            snake_Display.snake_direction = snake_Display.handle_normal_movement(event,snake_Display.snake_direction)
            if event.key == pygame.K_ESCAPE:
                quit_game()

    #draw background
    game_screen_main.show_gameWindow.fill(game_screen_main.background_colour)
    game_screen_main.draw_topbar()
    
    #draw snake/food
    snake_Display.draw_snake()
    food_main.draw_food()
    food_main.check_collision(snake_Display)
    
    #snake Movement
    snake_Display.snake_movement()
    snake_Display.wrap_around()


    pygame.display.update()
    snake_Display.move_counter += 1
    clock.tick(60)


