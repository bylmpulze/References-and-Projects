import pygame
from game_lib.game_render import GameScreen

pygame.init()  

my_display = GameScreen()
clock = pygame.time.Clock()
running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    my_display.show_gameWindow.fill(my_display.background_colour)
    my_display.draw_topbar()
    pygame.display.update()
    clock.tick(60)

pygame.quit()

