# settings_menu.py
import pygame
import sys
from pathlib import Path
from game.settings import load_settings, save_settings

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
SCRREN_SIZE = 800
BUTTON_W, BUTTON_H = int(SCRREN_SIZE*0.05), int(SCRREN_SIZE*0.05)
AVATAR_SIZE = int(SCRREN_SIZE*0.18)


class SettingsMenuScene:
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 36)

        self.title_text = self.font.render("Settings", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(screen.get_width() // 2, 100))

      
        self.settings = load_settings()
        self.selected_option = 0
        self.input_text = ""
        self.name_text = ""
        self.input_active = False
        self.name_active = False
        self.avatar_image = None
        self.avatar_path = None

        
        self.colors = ["p1", "p2", "p3", "p4"]
        self.color_index = self.colors.index(self.settings["player_color"]) if self.settings["player_color"] in self.colors else 0

          # Button Rects
        self.save_rect = pygame.Rect(int(SCRREN_SIZE * 0.1), int(SCRREN_SIZE * 0.8), int(SCRREN_SIZE * 0.2), int(SCRREN_SIZE * 0.05))
        self.cancel_rect = pygame.Rect(int(SCRREN_SIZE * 0.32), int(SCRREN_SIZE * 0.8), int(SCRREN_SIZE * 0.2), int(SCRREN_SIZE * 0.05))
        self.avatar_rect = pygame.Rect(int(SCRREN_SIZE * 0.66), int(SCRREN_SIZE * 0.16), AVATAR_SIZE, AVATAR_SIZE)
        self.choose_avatar_rect = pygame.Rect(int(SCRREN_SIZE * 0.56), int(SCRREN_SIZE * 0.4), int(SCRREN_SIZE * 0.2), int(SCRREN_SIZE * 0.05))
        self.reset_avatar_rect = pygame.Rect(int(SCRREN_SIZE * 0.78), int(SCRREN_SIZE * 0.4),  int(SCRREN_SIZE * 0.2), int(SCRREN_SIZE * 0.05))
        self.color_button = pygame.Rect(int(SCRREN_SIZE * 0.27), 355, 120, 40)
        self.name_box = pygame.Rect(int(SCRREN_SIZE * 0.25), 475, 200, 40)

        self.minus_rect = pygame.Rect(int(SCRREN_SIZE * 0.22), int(SCRREN_SIZE * 0.18), BUTTON_W, BUTTON_H)
        self.plus_rect = pygame.Rect(int(SCRREN_SIZE * 0.28), int(SCRREN_SIZE * 0.18), BUTTON_W, BUTTON_H)
        self.minus_t = pygame.Rect(int(SCRREN_SIZE * 0.2), 285, BUTTON_W, BUTTON_H)
        self.plus_t = pygame.Rect(int(SCRREN_SIZE * 0.27), 285, BUTTON_W, BUTTON_H)


        self.ip_box = pygame.Rect(int(SCRREN_SIZE * 0.25), 425, 200, 40)
        self.fs_rect = pygame.Rect(int(SCRREN_SIZE * 0.16), 220, 25, 25)

    def setup(self):
        pass

    def cleanup(self):
        pass

    def update(self):
        pass


    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Volume
            if self.minus_rect.collidepoint(mx, my):
                self.settings["volume"] = max(0.0, round(self.settings["volume"] - 0.1, 1))
            elif self.plus_rect.collidepoint(mx, my):
                self.settings["volume"] = min(1.0, round(self.settings["volume"] + 0.1, 1))

            # Fullscreen
            elif self.fs_rect.collidepoint(mx, my):
                self.settings["fullscreen"] = not self.settings["fullscreen"]

            # Tickrate
            elif self.minus_t.collidepoint(mx, my):
                self.settings["tickrate"] = max(10, self.settings["tickrate"] - 5)
            elif self.plus_t.collidepoint(mx, my):
                self.settings["tickrate"] = min(240, self.settings["tickrate"] + 5)

            # Player color
            elif self.color_button.collidepoint(mx, my):
                color_index = (self.color_index + 1) % len(self.colors)
                self.settings["player_color"] = self.colors[color_index]

            # IP input
            elif self.ip_box.collidepoint(mx, my):
                self.input_active = True
                self.name_active = False
            # Name input
            elif self.name_box.collidepoint(mx, my):
                self.name_active = True
                self.input_active = False
            else:
                self.input_active = False
                self.name_active = False

            # Avatar
            if self.choose_avatar_rect.collidepoint(mx, my):
                file_path = filedialog.askopenfilename(
                    title="Avatar auswählen",
                    filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
                )
                if file_path:
                    self.avatar_image = pygame.image.load(file_path)
                    self.avatar_image = pygame.transform.scale(self.avatar_image, (AVATAR_SIZE, AVATAR_SIZE))
                    self.avatar_path = file_path
            elif self.reset_avatar_rect.collidepoint(mx, my):
                self.avatar_image = None
                self.avatar_path = None

            # Save / Cancel
            if self.save_rect.collidepoint(mx, my):
                self.settings["multiplayer_ip"] = self.input_text
                self.settings["default_name"] = self.name_text or "Spieler1"
                self.settings["avatar_path"] = self.avatar_path
                save_settings(self.settings)
                self.scene_manager.switch_scene("MainMenu")
            
            elif self.cancel_rect.collidepoint(mx, my):
                self.scene_manager.switch_scene("MainMenu")

        elif event.type == pygame.KEYDOWN:
            # IP input
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    if len(event.unicode) == 1 and (event.unicode.isdigit() or event.unicode == "."):
                        self.input_text += event.unicode
                self.settings["multiplayer_ip"] = self.input_text

            # Name input
            if self.name_active:
                if event.key == pygame.K_RETURN:
                    self.name_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.name_text = self.name_text[:-1]
                else:
                    if len(event.unicode) == 1:
                        self.name_text += event.unicode


    def draw_text(self, text, pos, color=BLACK, font=FONT):
        render = font.render(text, True, color)
        self.screen.blit(render, pos)


    def draw_button(self, rect, text, active=False):
        color = GREEN if active else GRAY
        pygame.draw.rect(self.screen , color, rect, border_radius=8)
        pygame.draw.rect(self.screen , BLACK, rect, 2, border_radius=8)
        txt = FONT.render(text, True, BLACK)
        txt_rect = txt.get_rect(center=rect.center)
        self.screen.blit(txt, txt_rect)


    def render(self):
    
        # Multiplayer IP
        input_active = False
        input_text = self.settings.get("multiplayer_ip", "127.0.0.1")

        # Spielername
        name_active = False
        name_text = self.settings.get("default_name", "Spieler1")

        # Avatar
        avatar_path = self.settings.get("avatar_path")
        avatar_image = None
        if avatar_path and Path(avatar_path).exists():
            avatar_image = pygame.image.load(avatar_path)
            avatar_image = pygame.transform.scale(avatar_image, (AVATAR_SIZE, AVATAR_SIZE))

      
        self.screen.fill(WHITE)
        self.draw_text("⚙️ Einstellungen", (220, 10), BLUE, BIGFONT)

        # Volume
        self.draw_text(f"Lautstärke: {self.settings['volume']:.1f}", (int(SCRREN_SIZE * 0.05), 150))
        self.draw_button(self.minus_rect, "-")
        self.draw_button(self.plus_rect, "+")

        # Fullscreen
    
        pygame.draw.rect(self.screen, BLACK, self.fs_rect, 2)
        if self.settings["fullscreen"]:
            pygame.draw.line(self.screen, GREEN, (int(SCRREN_SIZE * 0.16), 220), (125, 245), 4)
            pygame.draw.line(self.screen, GREEN, (125, 220), (int(SCRREN_SIZE * 0.16), 245), 4)
        self.draw_text("Vollbild", (int(SCRREN_SIZE * 0.05), 220))

        # Tickrate
        self.draw_text(f"Tickrate: {self.settings['tickrate']}", (int(SCRREN_SIZE * 0.05), 290))
        self.draw_button(self.minus_t, "-")
        self.draw_button(self.plus_t, "+")

        # Player color
        self.draw_text("Spielerfarbe:", (int(SCRREN_SIZE * 0.05), 360))
        self.draw_button(self.color_button, self.settings["player_color"].upper())

        # Multiplayer-IP input
        self.draw_text("Multiplayer-IP:", (int(SCRREN_SIZE * 0.05), 430))
        pygame.draw.rect(self.screen, BLUE if input_active else DARKGRAY, self.ip_box, 2, border_radius=6)
        self.draw_text(input_text, (int(SCRREN_SIZE * 0.26), 430))

        # Spielername
        self.draw_text("Spielername:", (int(SCRREN_SIZE * 0.05), 480))
        pygame.draw.rect(self.screen, BLUE if name_active else DARKGRAY, self.name_box, 2, border_radius=6)
        self.draw_text(name_text, (int(SCRREN_SIZE * 0.26), 480))

        # Avatar
        self.draw_text("Avatar:", (int(SCRREN_SIZE * 0.55), int(SCRREN_SIZE * 0.16)))
        if avatar_image:
            self.screen.blit(avatar_image, self.avatar_rect)
        self.draw_button(self.choose_avatar_rect, "Bild auswählen")
        self.draw_button(self.reset_avatar_rect, "Zurücksetzen")

        # Save / Cancel
        self.draw_button(self.save_rect, "💾 Speichern")
        self.draw_button(self.cancel_rect, "❌ Abbrechen")



if __name__ == "__main__":
    screen = pygame.display.set_mode((700, 600))
    settings_menu(screen)
