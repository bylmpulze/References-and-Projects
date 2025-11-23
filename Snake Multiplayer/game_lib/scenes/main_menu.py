# MainMenuScene.py

import re
import sys
import pygame
from game_lib.scenes.helper.cog import GearSprite


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

        self.mouse_pos = (0, 0)

        self.input_text = ""
        self.selected_mode = None
        self.error_text = ""

        self.menu_options = [
            {"label": "Singleplayer (1)", "color": (80, 200, 90), "y": 180, "icon": "🐍"},
            {"label": "Multiplayer (2)",  "color": (70, 140, 230), "y": 300, "icon": "👥"},
            {"label": "Optionen (3)",     "color": (230, 200, 40), "y": 420, "icon": "⚙"},
            {"label": "Beenden (4)",      "color": (200, 60, 80),  "y": 540, "icon": "✖"},
        ]

        self.selected_option = 0
        self.settings = scene_manager.settings

    def setup(self):
        pass

    def cleanup(self):
        pass

    def update(self):
        pass

    def _create_raster_background(self):
        # Rasterhintergrund
        for x in range(0, self.screen.get_width(), 40):
            pygame.draw.line(self.screen, (38,48,67), (x,0), (x,self.screen.get_height()))
        for y in range(0, self.screen.get_height(), 40):
            pygame.draw.line(self.screen, (38,48,67), (0,y), (self.screen.get_width(),y))

    def render(self):
        self.screen.fill((20, 26, 38))

        self._create_raster_background()
        self.draw_text_centered("🐍 Snake Game 🐍", self.font_big, (255, 255, 255), int(self.screen.get_height() * 0.1))

        for btn in self.menu_options:
            w, h = 440, 80
            x, y =  self.screen.get_width() //2 - w//2, btn["y"]
            rect = pygame.Rect(x, y, w, h)
            hovered = rect.collidepoint(self.mouse_pos[0],self.mouse_pos[1])
            color = btn["color"]
            if hovered:
                # Hover-Effekt: heller + Rand
                color = tuple(min(c+40,255) for c in color)
                pygame.draw.rect(self.screen, (255,240,100), rect.inflate(8,8), border_radius=16)
            pygame.draw.rect(self.screen, color, rect, border_radius=16)

            # Schatten für Retro/Effekt
            pygame.draw.rect(self.screen, (40,40,40), rect.move(0,5), border_radius=16, width=0)

            # Buttontext & Icon
            text_surface = self.font_small.render(f"{btn['icon']} {btn['label']}", True, (255,255,255) if hovered else (150,150,150))
            self.screen.blit(text_surface, (x+28, y+15))

        # Info links unten
        info = self.font_small.render("v1.0  | bylmpulze & MMA92 |  © 2025", True, (170,170,170))
        self.screen.blit(info, (20,self.screen.get_height()-60))

            
        settings = self.settings

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
        settings = self.settings
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos

        elif event.type == pygame.KEYDOWN:
            # --- Mode selection ---
            if self.selected_mode is None:
                if event.key == pygame.K_1:
                    self.scene_manager.switch_scene("GameScene")
                if event.key == pygame.K_2:
                    self.selected_mode = "multi"
                if event.key == pygame.K_3:
                    self.scene_manager.switch_scene("SettingsScene")
                if event.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()

            # --- Multiplayer IP entry ---
            elif self.selected_mode == "multi":
                if event.key == pygame.K_ESCAPE:
                    # Cancel input → return to menu
                    self.selected_mode = None

                elif event.key == pygame.K_RETURN:
                    ip_to_check = self.input_text or settings.get("multiplayer_ip","")
                    if self.is_valid_ip(ip_to_check):
                        settings["multiplayer_ip"] = ip_to_check
                        save_settings(settings)
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
