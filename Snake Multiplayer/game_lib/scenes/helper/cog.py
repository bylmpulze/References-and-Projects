import pygame
import math

class GearSprite:
    def __init__(self, center, outer_radius, inner_radius, tooth_count, tooth_cut_radius, text, font):
        self.center = center
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.tooth_count = tooth_count
        self.tooth_cut_radius = tooth_cut_radius
        self.text = text
        self.font = font
        self.size = outer_radius * 2 + 2
        self.hovered = False

        self.top_left = (center[0] - self.size // 2, center[1] - self.size // 2)

        # Normal (dark gear)
        self.image_normal = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._draw_gear(self.image_normal, gear_color=(60,60,60), text_color=(255,255,0), text_bright=False)

        # Hover (silver gear, brighter yellow text)
        self.image_hover = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._draw_gear(self.image_hover, gear_color=(180,180,200), text_color=(255,210,40), text_bright=True)

    def _draw_gear(self, surf, gear_color, text_color, text_bright):
        cx = cy = self.size // 2
        # Draw gear body
        pygame.draw.circle(surf, gear_color, (cx, cy), self.outer_radius)
        # Draw inner hole
        pygame.draw.circle(surf, (0,0,0,0), (cx, cy), self.inner_radius)
        # Cut out "teeth"
        angle_step = 2 * math.pi / self.tooth_count
        for i in range(self.tooth_count):
            angle = i * angle_step
            tx = int(cx + math.cos(angle) * self.outer_radius)
            ty = int(cy + math.sin(angle) * self.outer_radius)
            pygame.draw.circle(surf, (0,0,0,0), (tx, ty), self.tooth_cut_radius)
        # Draw text centered
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=(cx, cy))
        # Optional: Draw subtle shadow for better contrast
        if text_bright:
            shadow_surf = self.font.render(self.text, True, (40,40,40))
            shadow_rect = shadow_surf.get_rect(center=(cx, cy+2))
            surf.blit(shadow_surf, shadow_rect)
        surf.blit(text_surf, text_rect)

    def is_hovered(self, pos):
        mx, my = pos
        
        gx, gy = self.center
        dist = math.hypot(mx - gx, my - gy)
        self.hovered = dist <= self.outer_radius

    def draw(self, target_surf):

        img = self.image_hover if self.hovered else self.image_normal
        target_surf.blit(img, self.top_left)


def main():

    # --- Usage Example ---
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 32, bold=True)

    gear = GearSprite(center=(200,200), outer_radius=110, inner_radius=66,
                    tooth_count=6, tooth_cut_radius=32, text="SETUP", font=font)

    running = True
    hovered = False
    SCREEN_W, SCREEN_H = 400, 400
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    # ...rest of code...

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                gx, gy = SCREEN_W // 2, SCREEN_H // 2
                dist = math.hypot(mx-gx, my-gy)
                hovered = dist <= gear.outer_radius

        screen.fill((255,255,255))

        center_x = (SCREEN_W - gear.size) // 2
        center_y = (SCREEN_H - gear.size) // 2
        gear.draw(screen, (center_x, center_y))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

