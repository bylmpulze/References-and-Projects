import pygame
from game_lib.game_render import GameScreen as GameScreen
from game_lib.snake import SnakeDisplay


pygame.init()  

game_render = GameScreen()
clock = pygame.time.Clock()
game_Started = True
endgame = True
snakedisplay = SnakeDisplay(game_render)
snakedisplay.get_SnakeImages()



#region Mainloop
while game_Started:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_Started = False
        if event.type == pygame.KEYDOWN:
            snakedisplay.snake_direction = snakedisplay.handle_normal_movement(event,snakedisplay.snake_direction)


    #draw background
    game_render.show_gameWindow.fill(game_render.background_colour)
    #draw snake
    game_render.draw_topbar(),snakedisplay.draw_snake(),snakedisplay.snake_movement(), snakedisplay.wrap_around()

    
    
    pygame.display.update()
    snakedisplay.move_counter += 1
    clock.tick(60)

pygame.quit()

