import random as randomizer
import pygame

# Feedspawn around 39x25 pixels ( 975 )
def feedCordsRandomizer():
    while True:
        Coord = [randomizer.randint(0, 27), randomizer.randint(0, 27)]
        if Coord not in snake and Coord not in feedCordrnd:
            return Coord
        
def draw_other_snakes(other_snakes, particle, screen, snake_skins):
    """Zeichnet andere Schlangen auf dem Bildschirm."""
    for snake_id,other_snake in other_snakes.items():
        for i, (x, y) in enumerate(other_snake):
            x *= particle
            y *= particle
            if i == 0:
                # Kopf zeichnen
                snake_head = snake_skins["p2"][0]  # Beispiel: p2 Farbe für andere Spieler
                rotated_head = pygame.transform.rotate(snake_head, 0)
                screen.blit(rotated_head, (int(x), int(y)))
            else:
                # Körper zeichnen
                snake_body = snake_skins["p2"][1]  # Beispiel: p2 Farbe für andere Spieler
                screen.blit(snake_body, (int(x), int(y)))


        




