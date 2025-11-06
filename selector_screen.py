import sys
import pygame

def draw_text_centered(screen, SCREEN_SIZE,text, font, color, y):
    """Hilfsfunktion für zentrierten Text"""
    render = font.render(text, True, color)
    rect = render.get_rect(center=(SCREEN_SIZE//2, y))
    screen.blit(render, rect)

def menu_screen(screen, SCREEN_SIZE):
    """Startmenü mit Auswahl Single-/Multiplayer"""
    input_active = False
    input_text = ""
    selected_mode = None
    font_big = pygame.font.SysFont(None, 80)
    font_small = pygame.font.SysFont(None, 40)

    while True:
        screen.fill((255, 255, 255))
        draw_text_centered(screen, SCREEN_SIZE,"🐍 Snake Game 🐍", font_big, (0, 0, 0), 200)
        draw_text_centered(screen, SCREEN_SIZE,"Drücke 1 für Singleplayer", font_small, (0, 100, 0), 350)
        draw_text_centered(screen, SCREEN_SIZE,"Drücke 2 für Multiplayer", font_small, (0, 0, 200), 400)
        if selected_mode == "multi":
            draw_text_centered(screen, SCREEN_SIZE,"Gib IP-Adresse ein:", font_small, (0, 0, 0), 470)
            pygame.draw.rect(screen, (220, 220, 220), (SCREEN_SIZE//2 - 150, 500, 300, 40))
            ip_render = font_small.render(input_text or "127.0.0.1", True, (0, 0, 0))
            screen.blit(ip_render, (SCREEN_SIZE//2 - 140, 505))
            draw_text_centered(screen, SCREEN_SIZE,"Drücke ENTER zum Start", font_small, (0, 0, 0), 560)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if selected_mode is None:
                    if event.key == pygame.K_1:
                        return None
                    if event.key == pygame.K_2:
                        selected_mode = "multi"
                        input_active = True
                elif selected_mode == "multi":
                    if event.key == pygame.K_RETURN:
                        return input_text or "127.0.0.1"
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        # Nur druckbare Zeichen
                        if len(event.unicode) == 1 and (event.unicode.isalnum() or event.unicode in ".:-"):
                            input_text += event.unicode
