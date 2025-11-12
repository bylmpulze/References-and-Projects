# settings_menu.py
import pygame
import sys
from pathlib import Path

try:
    import game.constants as CONSTANTS
    from game.settings import load_settings, save_settings
except ImportError:
    from game.settings import load_settings, save_settings
    import constants as CONSTANTS

# Für FileDialog
import tkinter as tk
from tkinter import filedialog
tk.Tk().withdraw()  # Tkinter root verstecken

pygame.init()
FONT = pygame.font.SysFont("Segoe UI Emoji", 20)
BIGFONT = pygame.font.SysFont("Segoe UI Emoji", 40)

WHITE = (245, 245, 245)
GRAY = (200, 200, 200)
DARKGRAY = (100, 100, 100)
GREEN = (0, 150, 0)
BLUE = (0, 100, 200)
RED = (200, 50, 50)
BLACK = (0, 0, 0)

BUTTON_W, BUTTON_H = int(CONSTANTS.SCREEN_SIZE*0.05), int(CONSTANTS.SCREEN_SIZE*0.05)
AVATAR_SIZE = int(CONSTANTS.SCREEN_SIZE*0.18)


def draw_text(surface, text, pos, color=BLACK, font=FONT):
    render = font.render(text, True, color)
    surface.blit(render, pos)


def draw_button(surface, rect, text, active=False):
    color = GREEN if active else GRAY
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)
    txt = FONT.render(text, True, BLACK)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)


def settings_menu(screen):
    settings = load_settings()
    clock = pygame.time.Clock()

    colors = ["p1", "p2", "p3", "p4"]
    color_index = colors.index(settings["player_color"]) if settings["player_color"] in colors else 0

    # Multiplayer IP
    input_active = False
    input_text = settings.get("multiplayer_ip", "127.0.0.1")

    # Spielername
    name_active = False
    name_text = settings.get("default_name", "Spieler1")

    # Avatar
    avatar_path = settings.get("avatar_path")
    avatar_image = None
    if avatar_path and Path(avatar_path).exists():
        avatar_image = pygame.image.load(avatar_path)
        avatar_image = pygame.transform.scale(avatar_image, (AVATAR_SIZE, AVATAR_SIZE))

    # Button Rects
    save_rect = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.1), int(CONSTANTS.SCREEN_SIZE * 0.8), int(CONSTANTS.SCREEN_SIZE * 0.2), int(CONSTANTS.SCREEN_SIZE * 0.05))
    cancel_rect = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.32), int(CONSTANTS.SCREEN_SIZE * 0.8), int(CONSTANTS.SCREEN_SIZE * 0.2), int(CONSTANTS.SCREEN_SIZE * 0.05))
    avatar_rect = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.66), int(CONSTANTS.SCREEN_SIZE * 0.16), AVATAR_SIZE, AVATAR_SIZE)
    choose_avatar_rect = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.56), int(CONSTANTS.SCREEN_SIZE * 0.4), int(CONSTANTS.SCREEN_SIZE * 0.2), int(CONSTANTS.SCREEN_SIZE * 0.05))
    reset_avatar_rect = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.78), int(CONSTANTS.SCREEN_SIZE * 0.4),  int(CONSTANTS.SCREEN_SIZE * 0.2), int(CONSTANTS.SCREEN_SIZE * 0.05))

    running = True
    while running:
        screen.fill(WHITE)
        draw_text(screen, "⚙️ Einstellungen", (220, 10), BLUE, BIGFONT)

        # Volume
        draw_text(screen, f"Lautstärke: {settings['volume']:.1f}", (int(CONSTANTS.SCREEN_SIZE * 0.05), 150))
        minus_rect = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.22), int(CONSTANTS.SCREEN_SIZE * 0.18), BUTTON_W, BUTTON_H)
        plus_rect = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.28), int(CONSTANTS.SCREEN_SIZE * 0.18), BUTTON_W, BUTTON_H)
        draw_button(screen, minus_rect, "-")
        draw_button(screen, plus_rect, "+")

        # Fullscreen
        fs_rect = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.16), 220, 25, 25)
        pygame.draw.rect(screen, BLACK, fs_rect, 2)
        if settings["fullscreen"]:
            pygame.draw.line(screen, GREEN, (int(CONSTANTS.SCREEN_SIZE * 0.16), 220), (125, 245), 4)
            pygame.draw.line(screen, GREEN, (125, 220), (int(CONSTANTS.SCREEN_SIZE * 0.16), 245), 4)
        draw_text(screen, "Vollbild", (int(CONSTANTS.SCREEN_SIZE * 0.05), 220))

        # Tickrate
        draw_text(screen, f"Tickrate: {settings['tickrate']}", (int(CONSTANTS.SCREEN_SIZE * 0.05), 290))
        minus_t = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.2), 285, BUTTON_W, BUTTON_H)
        plus_t = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.27), 285, BUTTON_W, BUTTON_H)
        draw_button(screen, minus_t, "-")
        draw_button(screen, plus_t, "+")

        # Player color
        draw_text(screen, "Spielerfarbe:", (int(CONSTANTS.SCREEN_SIZE * 0.05), 360))
        color_button = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.27), 355, 120, 40)
        draw_button(screen, color_button, settings["player_color"].upper())

        # Multiplayer-IP input
        draw_text(screen, "Multiplayer-IP:", (int(CONSTANTS.SCREEN_SIZE * 0.05), 430))
        ip_box = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.25), 425, 200, 40)
        pygame.draw.rect(screen, BLUE if input_active else DARKGRAY, ip_box, 2, border_radius=6)
        draw_text(screen, input_text, (int(CONSTANTS.SCREEN_SIZE * 0.26), 430))

        # Spielername
        draw_text(screen, "Spielername:", (int(CONSTANTS.SCREEN_SIZE * 0.05), 480))
        name_box = pygame.Rect(int(CONSTANTS.SCREEN_SIZE * 0.25), 475, 200, 40)
        pygame.draw.rect(screen, BLUE if name_active else DARKGRAY, name_box, 2, border_radius=6)
        draw_text(screen, name_text, (int(CONSTANTS.SCREEN_SIZE * 0.26), 480))

        # Avatar
        draw_text(screen, "Avatar:", (int(CONSTANTS.SCREEN_SIZE * 0.55), int(CONSTANTS.SCREEN_SIZE * 0.16)))
        if avatar_image:
            screen.blit(avatar_image, avatar_rect)
        draw_button(screen, choose_avatar_rect, "Bild auswählen")
        draw_button(screen, reset_avatar_rect, "Zurücksetzen")

        # Save / Cancel
        draw_button(screen, save_rect, "💾 Speichern")
        draw_button(screen, cancel_rect, "❌ Abbrechen")

        pygame.display.flip()
        clock.tick(30)

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Volume
                if minus_rect.collidepoint(mx, my):
                    settings["volume"] = max(0.0, round(settings["volume"] - 0.1, 1))
                elif plus_rect.collidepoint(mx, my):
                    settings["volume"] = min(1.0, round(settings["volume"] + 0.1, 1))

                # Fullscreen
                elif fs_rect.collidepoint(mx, my):
                    settings["fullscreen"] = not settings["fullscreen"]

                # Tickrate
                elif minus_t.collidepoint(mx, my):
                    settings["tickrate"] = max(10, settings["tickrate"] - 5)
                elif plus_t.collidepoint(mx, my):
                    settings["tickrate"] = min(240, settings["tickrate"] + 5)

                # Player color
                elif color_button.collidepoint(mx, my):
                    color_index = (color_index + 1) % len(colors)
                    settings["player_color"] = colors[color_index]

                # IP input
                elif ip_box.collidepoint(mx, my):
                    input_active = True
                    name_active = False
                # Name input
                elif name_box.collidepoint(mx, my):
                    name_active = True
                    input_active = False
                else:
                    input_active = False
                    name_active = False

                # Avatar
                if choose_avatar_rect.collidepoint(mx, my):
                    file_path = filedialog.askopenfilename(
                        title="Avatar auswählen",
                        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
                    )
                    if file_path:
                        avatar_image = pygame.image.load(file_path)
                        avatar_image = pygame.transform.scale(avatar_image, (AVATAR_SIZE, AVATAR_SIZE))
                        avatar_path = file_path
                elif reset_avatar_rect.collidepoint(mx, my):
                    avatar_image = None
                    avatar_path = None

                # Save / Cancel
                if save_rect.collidepoint(mx, my):
                    settings["multiplayer_ip"] = input_text
                    settings["default_name"] = name_text or "Spieler1"
                    settings["avatar_path"] = avatar_path
                    save_settings(settings)
                    running = False
                elif cancel_rect.collidepoint(mx, my):
                    running = False

            elif event.type == pygame.KEYDOWN:
                # IP input
                if input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(event.unicode) == 1 and (event.unicode.isdigit() or event.unicode == "."):
                            input_text += event.unicode
                    settings["multiplayer_ip"] = input_text

                # Name input
                if name_active:
                    if event.key == pygame.K_RETURN:
                        name_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    else:
                        if len(event.unicode) == 1:
                            name_text += event.unicode


if __name__ == "__main__":
    screen = pygame.display.set_mode((700, 600))
    settings_menu(screen)
