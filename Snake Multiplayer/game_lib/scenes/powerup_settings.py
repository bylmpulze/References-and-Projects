# settings_menu.py
import sys
import json
import pygame
from pathlib import Path

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


class PowerupSettingsScene:
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 36)

        self.title_text = self.font.render("Powerup", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(screen.get_width() // 2, 100))

           

          # Button Rects
        self.save_rect = pygame.Rect(int(SCRREN_SIZE * 0.1), int(SCRREN_SIZE * 0.8), int(SCRREN_SIZE * 0.2), int(SCRREN_SIZE * 0.05))
        self.cancel_rect = pygame.Rect(int(SCRREN_SIZE * 0.32), int(SCRREN_SIZE * 0.8), int(SCRREN_SIZE * 0.2), int(SCRREN_SIZE * 0.05))

    
        checkbox_rect = pygame.Rect(int(SCRREN_SIZE * 0.16), 220, 25, 25)
        self.json_data = self.load_json()
        self.checkboxes = self.create_checkbox()

    def load_json(self):
        with open("Snake Multiplayer\\powerupconfig.json", "r", encoding="utf-8") as file:
            return json.load(file)

    def setup(self):
        pass

    def cleanup(self):
        pass

    def update(self):
        pass


    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

               
            for pw_name, pw_dct in self.checkboxes.items():
                checkbox_rect = pw_dct["checkbox_rect"]

                # Powerup Enabled
                if checkbox_rect.collidepoint(mx, my):
                    pw_dct["enabled"] = not pw_dct["enabled"]

            # Save / Cancel
            if self.save_rect.collidepoint(mx, my):
                self.scene_manager.switch_scene("MainMenu")



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
          
        self.screen.fill(WHITE)
        self.draw_text("⚙️ Powerup Settings", (220, 10), BLUE, BIGFONT)

        for pw_name, pw_dct in self.checkboxes.items():

            checkbox_rect = pw_dct["checkbox_rect"]
            rect = pw_dct["tickrate_minus_rect"]
            rect2 = pw_dct["tickrate_plus_rect"]
            
            self.draw_text(pw_name, (int(SCRREN_SIZE * 0.3), checkbox_rect.y))
            self.draw_checkbox(checkbox_rect, pw_dct["enabled"])       
            
            # Tickrate
            self.draw_text(f"Dauer", (int(SCRREN_SIZE * 0.66), checkbox_rect.y))
            self.draw_button(rect, "-")
            self.draw_button(rect2, "+")
        
  

        # Save / Cancel
        self.draw_button(self.save_rect, "💾 Speichern")
        self.draw_button(self.cancel_rect, "❌ Abbrechen")

    def create_checkbox(self):
        dct = {}
        y = 100
        for pw_name,pw_dct in self.json_data.items():
            #"speed_boost_x2": {"enabled": true,  "duration": 1500},
            checkbox_rect = pygame.Rect(int(SCRREN_SIZE * 0.1), y, int(SCRREN_SIZE * 0.03), int(SCRREN_SIZE * 0.03))
            rect = pygame.Rect(int(SCRREN_SIZE * 0.5), y, int(SCRREN_SIZE * 0.05), int(SCRREN_SIZE * 0.025))
            rect2 = pygame.Rect(int(SCRREN_SIZE * 0.56), y, int(SCRREN_SIZE * 0.05), int(SCRREN_SIZE * 0.025))

            dct[pw_name] = {
                "enabled": pw_dct["enabled"],
                "duration": pw_dct["duration"],
                "tickrate_minus_rect": rect,
                "tickrate_plus_rect": rect2,
                "checkbox_rect": checkbox_rect
            }

            y += 100

        return dct



    def draw_checkbox(self,checkbox_rect, active=False):

        starting_pos = (checkbox_rect.x + 1, checkbox_rect.y + 1)
        ending_pos = (checkbox_rect.x + checkbox_rect.w - 1, checkbox_rect.y + checkbox_rect.h - 1)
        startpos_2 = (checkbox_rect.x + checkbox_rect.w - 1, checkbox_rect.y + 1)
        endpos_2 = (checkbox_rect.x + 1, checkbox_rect.y + checkbox_rect.h - 1)

        if active:
            pygame.draw.line(self.screen, GREEN, starting_pos, ending_pos, 3)
            pygame.draw.line(self.screen, GREEN, startpos_2, endpos_2, 3)

        pygame.draw.rect(self.screen, BLACK, checkbox_rect, 2)



if __name__ == "__main__":
    screen = pygame.display.set_mode((700, 600))
    settings_menu(screen)
