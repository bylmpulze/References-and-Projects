import pygame
from game_lib.game_render import GameScreen  #importiert die klasse Gamescreen von der datei game_render in dem ordner game_lib
from game_lib.snake import SnakeDisplay
from game_lib.food import FoodMain


pygame.init()  
game_screen_main = GameScreen() #erstellt ein objekt "game render" von der klasse "GameScreen"
snake_Display = SnakeDisplay(game_screen_main) #erstellt ein objekt "snakedisplay" von der Klasse snakedisplay und gibt das objekt game_render mit - Das bedeutet SnakeDisplay hat zugriff auf die klasse GameScreen() 
food_main = FoodMain(game_screen_main)



#init pictures - snake/food
snake_Display.create_snake_body_image(),snake_Display.create_snake_head_image(),#food_Display.create_foodImage()
clock = pygame.time.Clock()
game_Started = True
endgame = True
food_main.spawn_food(snake_Display.get_snake_headcords()) #init foodspawn




#region Mainloop
while game_Started:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_Started = False
        if event.type == pygame.KEYDOWN:
            snake_Display.snake_direction = snake_Display.handle_normal_movement(event,snake_Display.snake_direction)


    #draw background
    game_screen_main.show_gameWindow.fill(game_screen_main.background_colour)
    game_screen_main.draw_topbar()
    
    #draw snake/food
    snake_Display.draw_snake(),food_main.draw_food()
    food_main.food_kollision_check(snake_Display)
    
    #snake Movement
    snake_Display.snake_movement(), snake_Display.wrap_around()



    
    
    pygame.display.update()
    snake_Display.move_counter += 1
    clock.tick(60)

pygame.quit()

