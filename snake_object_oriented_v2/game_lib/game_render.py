import pygame
import sys


#region Display
class Display:
    def __init__(self):
        self.resolution_width = 1920
        self.resolution_height = 1080
        self.max_fps = 240
        self.vsync = False
        self.fullscreen = False

    def set_fullscreen_on_off(self,settings_menu_fullscreen):
        settings_menu_fullscreen = bool(settings_menu_fullscreen) # bool in true oder false ->set ("x")/1/[1]  = true(1) 0/""/[] = false
        return self.fullscreen
    
    def set_vsync_on_off(self,settings_menu_vsync):
        settings_menu_vsync = bool(settings_menu_vsync) # bool in true oder false ->set ("x")/1/[1]  = true(1) 0/""/[] = false
        return self.vsync

#region GameScreen
class GameScreen:
    def __init__(self):
        self.screen_size_height = 1000
        self.screen_size_width = 1000
        self.topbar_height = 40
        self.particle_size = 25
        self.show_score = 0
        self.background_colour = 100,150,200
        self.show_gameWindow = pygame.display.set_mode([self.screen_size_height, self.screen_size_width])
        self.font = pygame.font.SysFont(None, 40)

    def game_over_screen(self):
        self.show_gameWindow.fill((255, 255, 255))
        game_over_text = self.font.render(f"Spiel zuende! Deine Punktzahl: {self.show_score}", True, (255, 0, 0))
        restart_text = self.font.render("Klicke oder Taste zum Neustart", True, (0, 0, 0))

        self.show_gameWindow.blit(game_over_text, (50, 300))
        self.show_gameWindow.blit(restart_text, (50, 350))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False


    def draw_topbar(self):
        settings_text, settings_rect = self.get_settingsrekt()       
        pygame.draw.rect(self.show_gameWindow, (200, 200, 200),
                         (0, 0, self.screen_size_width, self.topbar_height))
        
        score_text = self.font.render(f"Punkte: {self.show_score}", True, (0, 0, 0))
        self.show_gameWindow.blit(score_text, (10, 10))
        self.show_gameWindow.blit(settings_text, settings_rect)

    def get_settingsrekt(self):
        settings_text = self.font.render("Einstellungen", True, (0, 0, 0))
        settings_rect = settings_text.get_rect(topright=(self.screen_size_width - 10, 10))
        return settings_text,settings_rect

    def game_over_screen(self):
        self.show_gameWindow.fill((255, 255, 255))
        game_over_text = self.font.render(f"Spiel zuende! Deine Punktzahl: {self.show_score}", True, (255, 0, 0))
        restart_text = self.font.render("Klicke oder Taste zum Neustart", True, (0, 0, 0))

        self.show_gameWindow.blit(game_over_text, (50, 300))
        self.show_gameWindow.blit(restart_text, (50, 350))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
    
    #region GameScreen helper functions
    def get_topbar_height(self):
        return self.topbar_height
    
    def get_score(self):
        return self.show_score
    
    def add_score(self,points):
        self.show_score += points
        print("10 points added")
    
    def get_particle_size(self):
        return self.particle_size
    
    def get_screen_size_width(self):
        return self.screen_size_width

    def get_screen_size_height(self):
        return self.screen_size_height
       
    def display(self, source, dest, area = None, special_flags= 0):
        self.show_gameWindow.blit(source, dest, area, special_flags)

    
