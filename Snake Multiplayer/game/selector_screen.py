import re
import sys
import pygame

def is_valid_ip(ip: str) -> bool:
    """Checks whether the given string is a valid IPv4 address."""
    if not ip or len(ip) > 15:
        return False
    pattern = r"^(25[0-5]|2[0-4]\d|1?\d{1,2})(\.(25[0-5]|2[0-4]\d|1?\d{1,2})){3}$"
    return re.match(pattern, ip) is not None

def draw_text_centered(screen, SCREEN_SIZE,text, font, color, y):
    """Hilfsfunktion für zentrierten Text"""
    render = font.render(text, True, color)
    rect = render.get_rect(center=(SCREEN_SIZE//2, y))
    screen.blit(render, rect)


def menu_screen(screen, SCREEN_SIZE):
    """Start menu: choose Singleplayer or Multiplayer with IP input."""
    input_text = ""
    selected_mode = None
    error_text = ""
    font_big = pygame.font.SysFont(None, 80)
    font_small = pygame.font.SysFont(None, 40)

    while True:
        screen.fill((255, 255, 255))
        draw_text_centered(screen, SCREEN_SIZE, "🐍 Snake Game 🐍", font_big, (0, 0, 0), 200)
        draw_text_centered(screen, SCREEN_SIZE,"Drücke 1 für Singleplayer", font_small, (0, 100, 0), 350)
        draw_text_centered(screen, SCREEN_SIZE,"Drücke 2 für Multiplayer", font_small, (0, 0, 200), 400)

        if selected_mode == "multi":
            draw_text_centered(screen, SCREEN_SIZE,"Gib IP-Adresse ein:", font_small, (0, 0, 0), 470)
            pygame.draw.rect(screen, (220, 220, 220), (SCREEN_SIZE//2 - 150, 500, 300, 40))
            ip_render = font_small.render(input_text or "127.0.0.1", True, (0, 0, 0))
            screen.blit(ip_render, (SCREEN_SIZE//2 - 140, 505))
            draw_text_centered(screen, SCREEN_SIZE,"Drücke ENTER zum Start oder ESC zum Abbrechen", font_small, (0, 0, 0), 560)
            
            if error_text:
                draw_text_centered(screen, SCREEN_SIZE,error_text, font_small, (255, 0, 0), 600)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # --- Mode selection ---
                if selected_mode is None:
                    if event.key == pygame.K_1:
                        return None
                    if event.key == pygame.K_2:
                        selected_mode = "multi"
              
                # --- Multiplayer IP entry ---
                elif selected_mode == "multi":
                    if event.key == pygame.K_ESCAPE:
                        # Cancel input → return to singleplayer
                        return None

                    elif event.key == pygame.K_RETURN:
                        ip_to_check = input_text or "127.0.0.1"
                        if is_valid_ip(ip_to_check):
                            return ip_to_check
                        else:
                            error_text = f"❌ Ungültige IP-Adresse: {ip_to_check}"

                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                        error_text = ""
                    else:
                        # Allow only numbers and dots
                        if len(event.unicode) == 1 and (event.unicode.isdigit() or event.unicode == "."):
                            input_text += event.unicode
                            error_text = ""
