# MainMenuScene.py

import re
import sys
import pygame
from game.settings import save_settings, load_settings
from server_lib.client import TCPClient


class MainMenuScene:
    def __init__(self, screen, scene_manager):
        """Start menu: choose Singleplayer or Multiplayer with IP input."""
        self.screen = screen
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 36)

        self.font_big = pygame.font.SysFont("Segoe UI Emoji", 80)
        self.font_small = pygame.font.SysFont("Segoe UI Emoji", 40)

        self.title_text = self.font.render("Game Title", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(
            center=(screen.get_width() // 2, 100)
        )

        self.input_text = ""
        self.selected_mode = None
        self.error_text = ""

        self.menu_options = ["Continue", "New Game", "Settings", "Quit"]
        self.selected_option = 0

    def setup(self):
        pass

    def cleanup(self):
        pass

    def update(self):
        pass

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title_text, self.title_rect)

        for i, option in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.selected_option else (150, 150, 150)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.screen.get_width() // 2, 200 + i * 50))
            self.screen.blit(text, rect)

        settings = load_settings()

        self.screen.fill((255, 255, 255))
        self.draw_text_centered("🐍 Snake Game 🐍", self.font_big, (0, 0, 0), 200)
        self.draw_text_centered(
            "Drücke 1 für Singleplayer", self.font_small, (0, 100, 0), 350
        )
        self.draw_text_centered(
            "Drücke 2 für Multiplayer", self.font_small, (0, 0, 200), 400
        )

        if self.selected_mode == "multi":
            self.draw_text_centered(
                "Gib IP-Adresse ein:", self.font_small, (0, 0, 0), 470
            )
            pygame.draw.rect(
                self.screen,
                (220, 220, 220),
                (self.screen.get_width() // 2 - 150, 500, 300, 40),
            )
            ip_render = self.font_small.render(
                self.input_text or settings.get("multiplayer_ip"), True, (0, 0, 0)
            )
            self.screen.blit(ip_render, (self.screen.get_width() // 2 - 140, 505))
            self.draw_text_centered(
                "Drücke ENTER zum Start", self.font_small, (0, 0, 0), 580
            )
            self.draw_text_centered(
                "oder ESC zum Abbrechen", self.font_small, (0, 0, 0), 620
            )

            if self.error_text:
                self.draw_text_centered(
                    self.error_text, self.font_small, (255, 0, 0), 660
                )

    def handle_event(self, event):
        settings = load_settings()

        if event.type == pygame.KEYDOWN:
            # --- Mode selection ---
            if self.selected_mode is None:
                if event.key == pygame.K_1:
                    self.scene_manager.switch_scene("GameScene")
                if event.key == pygame.K_2:
                    self.selected_mode = "multi"

            # --- Multiplayer IP entry ---
            elif self.selected_mode == "multi":
                if event.key == pygame.K_ESCAPE:
                    # Cancel input → return to menu
                    self.selected_mode = None

                elif event.key == pygame.K_RETURN:
                    ip_to_check = self.input_text or settings.get("multiplayer_ip")
                    if self.is_valid_ip(ip_to_check):
                        settings["multiplayer_ip"] = ip_to_check
                        save_settings(settings)
                        self.scene_manager.scenes["GameScene"].client = TCPClient(
                            "127.0.0.1"
                        )

                        self.scene_manager.scenes[
                            "GameScene"
                        ].client.power_ups = self.scene_manager.scenes[
                            "GameScene"
                        ].power_ups

                        self.scene_manager.switch_scene("GameScene")
                    else:
                        self.error_text = f"❌ Ungültige IP-Adresse: {ip_to_check}"

                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    self.error_text = ""
                else:
                    # Allow only numbers and dots
                    if len(event.unicode) == 1 and (
                        event.unicode.isdigit() or event.unicode == "."
                    ):
                        self.input_text += event.unicode
                        self.error_text = ""

    def is_valid_ip(self, ip: str) -> bool:
        """Checks whether the given string is a valid IPv4 address."""
        if not ip or len(ip) > 15:
            return False
        pattern = r"^(25[0-5]|2[0-4]\d|1?\d{1,2})(\.(25[0-5]|2[0-4]\d|1?\d{1,2})){3}$"
        return re.match(pattern, ip) is not None

    def draw_text_centered(self, text, font, color, y):
        """Hilfsfunktion für zentrierten Text"""
        render = font.render(text, True, color)
        rect = render.get_rect(center=(800 // 2, y))
        self.screen.blit(render, rect)
