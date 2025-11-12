import pygame
import sys
import game.constants as CONSTANTS


def draw_rejected(screen,msg_str):
    # Main Loop
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((255, 255, 255))
        game_over_text = font.render("Der Server hat deine Verbindung ablehnt", True, (255, 0, 0))
        reason_text = font.render(msg_str, True, (0, 0, 0))

        game_over_text_rect = game_over_text.get_rect(center=(CONSTANTS.SCREEN_SIZE/2, CONSTANTS.SCREEN_SIZE/2 - 50))
        reason_text_rect = reason_text.get_rect(center=(CONSTANTS.SCREEN_SIZE/2, CONSTANTS.SCREEN_SIZE/2 + 50) )
        
        screen.blit(game_over_text, game_over_text_rect)
        screen.blit(reason_text,reason_text_rect)

        pygame.display.update()
        clock.tick(60)
