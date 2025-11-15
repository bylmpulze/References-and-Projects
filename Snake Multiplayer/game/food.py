import pygame
from game.helper import resource_path


class Food(pygame.sprite.Sprite):
    def __init__(self, particle_size: int):
        """
        particle_size: Zellgröße in Pixeln.
        """
        super().__init__()  # fügt sich selbst der Gruppe hinzu, wenn angegeben
        self.particle_size = int(particle_size)
        img_path = resource_path('assets/apfel2.jpg')
        base_img = pygame.image.load(img_path).convert_alpha()
        self.base_image = pygame.transform.smoothscale(
            base_img, (self.particle_size, self.particle_size)
        )  

        # Renderbild und Rect (Rect basiert auf Pixelkoordinaten) [web:34]
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.grid_pos = (0, 0)  # (gx, gy) in Zellen
        self.sound_file = pygame.mixer.Sound(resource_path('assets/sounds/food.mp3'))

    def draw(self,screen):
        screen.blit(self.image,self.grid_pos)

    def collides_with_rect(self, rect: pygame.Rect) -> bool:
        return self.rect.colliderect(rect)

    def on_eaten(self) -> None:
        """
        Sound etc.
        """
        self.sound_file.play()
        


