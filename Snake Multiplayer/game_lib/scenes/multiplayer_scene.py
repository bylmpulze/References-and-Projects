import re
import pygame
from pathlib import Path

# Initialize Pygame
pygame.init()

# Fonts
FONT = pygame.font.SysFont("Segoe UI Emoji", 22)
BIGFONT = pygame.font.SysFont("Segoe UI Emoji", 40)
SMALLFONT = pygame.font.SysFont("Segoe UI Emoji", 18)

# Colors
WHITE = (245, 245, 245)
LIGHT_BG = (235, 238, 245)
PANEL_BG = (250, 250, 255)
GRAY = (200, 200, 200)
DARKGRAY = (120, 120, 130)
GREEN = (0, 160, 90)
BLUE = (40, 110, 210)
RED = (210, 70, 70)
BLACK = (15, 15, 20)

# Screen and layout constants
SCREEN_W, SCREEN_H = 900, 700
PADDING = 24
PANEL_WIDTH = 600
PANEL_HEIGHT = 420
FIELD_HEIGHT = 44
FIELD_SPACING = 28
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 48
AVATAR_SIZE = 110


class MultiplayerScene:
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 36)

        # Card / panel rect (centered in window)
        self.panel_rect = pygame.Rect(0, 0, PANEL_WIDTH, PANEL_HEIGHT)
        self.panel_rect.center = self.screen.get_rect().center

        # Title bar inside the panel
        self.title_bar_rect = pygame.Rect(
            self.panel_rect.x,
            self.panel_rect.y,
            self.panel_rect.w,
            70
        )

        # Content area origin (top-left inside the card, below title)
        content_x = self.panel_rect.x + PADDING
        content_y = self.panel_rect.y + 90

        # Input handling
        self.ip_active = False
        self.name_active = False
        self.ip_text = ""
        self.name_text = ""

        # Field boxes (aligned in a column)
        field_width = self.panel_rect.w - 2 * PADDING - AVATAR_SIZE - 20
        self.ip_box = pygame.Rect(content_x, content_y, field_width, FIELD_HEIGHT)
        self.name_box = pygame.Rect(
            content_x,
            content_y + FIELD_HEIGHT + FIELD_SPACING,
            field_width,
            FIELD_HEIGHT
        )

        # Avatar area on the right inside the panel
        self.avatar_rect = pygame.Rect(
            self.panel_rect.right - PADDING - AVATAR_SIZE,
            content_y,
            AVATAR_SIZE,
            AVATAR_SIZE
        )

        # Buttons row at bottom of card
        buttons_y = self.panel_rect.bottom - PADDING - BUTTON_HEIGHT
        total_button_width = 2 * BUTTON_WIDTH + 20
        start_x = self.panel_rect.centerx - total_button_width // 2

        self.save_rect = pygame.Rect(start_x, buttons_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.cancel_rect = pygame.Rect(
            start_x + BUTTON_WIDTH + 20,
            buttons_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )

        # Load settings
        self.settings = scene_manager.settings
        self.ip_text = self.settings.get("multiplayer_ip", "127.0.0.1")
        self.name_text = self.settings.get("default_name", "Spieler1")

    def setup(self):
        pass

    def cleanup(self):
        # Reset to stored values
        self.ip_text = self.settings.get("multiplayer_ip", "127.0.0.1")
        self.name_text = self.settings.get("default_name", "Spieler1")
        self.ip_active = False
        self.name_active = False

    def update(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Activate/deactivate text fields
            self.ip_active = self.ip_box.collidepoint(mx, my)
            self.name_active = self.name_box.collidepoint(mx, my)

            # Buttons (no real logic here yet, just placeholders)
            if self.save_rect.collidepoint(mx, my):
                self.settings["multiplayer_ip"] = self.ip_text
                self.settings["default_name"] = self.name_text

            if self.cancel_rect.collidepoint(mx, my):
                self.cleanup()
                self.scene_manager.switch_scene("MainMenu")

        elif event.type == pygame.KEYDOWN:
            # IP input
            if self.ip_active:
                if event.key == pygame.K_RETURN:
                    self.ip_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.ip_text = self.ip_text[:-1]
                else:
                    if len(event.unicode) == 1 and (event.unicode.isdigit() or event.unicode == "."):
                        self.ip_text += event.unicode

            # Name input
            elif self.name_active:
                if event.key == pygame.K_RETURN:
                    self.name_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.name_text = self.name_text[:-1]
                else:
                    if len(event.unicode) == 1:
                        self.name_text += event.unicode
            else:
                if event.key == pygame.K_ESCAPE:
                    self.cleanup()
                    self.scene_manager.switch_scene("MainMenu")

    def draw_text_left(self, text, pos, color=BLACK, font=FONT):
        surface = font.render(text, True, color)
        self.screen.blit(surface, pos)

    def draw_text_center(self, text, center, color=BLACK, font=FONT):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=center)
        self.screen.blit(surface, rect)

    def draw_button(self, rect, text, color, hover=False):
        bg = color
        if hover:
            bg = (min(color[0] + 20, 255),
                  min(color[1] + 20, 255),
                  min(color[2] + 20, 255))

        pygame.draw.rect(self.screen, bg, rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=10)
        self.draw_text_center(text, rect.center, WHITE)

    def render(self):
        mouse_pos = pygame.mouse.get_pos()

        # Background
        self.screen.fill(LIGHT_BG)

        # Card shadow
        shadow_rect = self.panel_rect.move(4, 4)
        pygame.draw.rect(self.screen, (210, 210, 220), shadow_rect, border_radius=16)

        # Card / panel
        pygame.draw.rect(self.screen, PANEL_BG, self.panel_rect, border_radius=16)
        pygame.draw.rect(self.screen, (210, 210, 220), self.panel_rect, 2, border_radius=16)

        # Title bar
        text_rect = self.title_bar_rect
        text_rect.y = int(self.screen.get_height() * 0.1)
        pygame.draw.rect(self.screen, BLUE, self.title_bar_rect, border_radius=16)
        self.draw_text_center("⚙️ Multiplayer-Einstellungen", self.title_bar_rect.center, WHITE, BIGFONT)

        # IP label + field
        self.draw_text_left("Server-IP", (self.ip_box.x, self.ip_box.y - 24), DARKGRAY, SMALLFONT)
        pygame.draw.rect(
            self.screen,
            BLUE if self.ip_active else GRAY,
            self.ip_box,
            2,
            border_radius=8
        )
        self.draw_text_left(self.ip_text, (self.ip_box.x + 10, self.ip_box.y + 10))

        # Name label + field
        self.draw_text_left("Spielername", (self.name_box.x, self.name_box.y - 24), DARKGRAY, SMALLFONT)
        pygame.draw.rect(
            self.screen,
            BLUE if self.name_active else GRAY,
            self.name_box,
            2,
            border_radius=8
        )
        self.draw_text_left(self.name_text, (self.name_box.x + 10, self.name_box.y + 10))

        # Avatar
        pygame.draw.rect(self.screen, GRAY, self.avatar_rect, border_radius=16)
        avatar_path = self.settings.get("avatar_path")
        if avatar_path and Path(avatar_path).exists():
            avatar_image = pygame.image.load(avatar_path)
            avatar_image = pygame.transform.smoothscale(avatar_image, (AVATAR_SIZE, AVATAR_SIZE))
            self.screen.blit(avatar_image, self.avatar_rect)
        else:
            self.draw_text_center("🙂", self.avatar_rect.center, BLACK, BIGFONT)
            self.draw_text_center("Avatar", (self.avatar_rect.centerx, self.avatar_rect.bottom + 16), DARKGRAY, SMALLFONT)

        # Buttons (hover effect)
        save_hover = self.save_rect.collidepoint(mouse_pos)
        cancel_hover = self.cancel_rect.collidepoint(mouse_pos)

        self.draw_button(self.save_rect, "💾 Speichern", GREEN, hover=save_hover)
        self.draw_button(self.cancel_rect, "❌ Abbrechen", RED, hover=cancel_hover)

    
    def is_valid_ip(self, ip: str) -> bool:
        """Checks whether the given string is a valid IPv4 address."""
        if not ip or len(ip) > 15:
            return False
        pattern = r"^(25[0-5]|2[0-4]\d|1?\d{1,2})(\.(25[0-5]|2[0-4]\d|1?\d{1,2})){3}$"
        return re.match(pattern, ip) is not None




if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    print("Settings menu loaded - expected to be used with SceneManager.")
