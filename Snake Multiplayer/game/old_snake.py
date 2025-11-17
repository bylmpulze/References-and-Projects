import pygame
from game_lib.helper import resource_path

WORLD_SIZE = 800   # world is 800x800


class SnakeDisplay:
    def __init__(self, screen, particle_size=25, speed=4):
        self.screen = screen
        self.particle_size = particle_size
        self.speed = speed  # pixels per frame
        self.direction = (1, 0)
        self.move_counter = 0
        self.snake_direction = 0
        # Use floats for smooth movement
        self.head_pos = [400.0, 400.0]

        # Node history stores continuous (unwrapped) coordinates
        self.nodes = [self.head_pos.copy()]

        # Body segments stored in continuous coordinates as well
        self.body_segments = [
            self.head_pos.copy(),
            [self.head_pos[0] - particle_size, self.head_pos[1]],
            [self.head_pos[0] - 2 * particle_size, self.head_pos[1]]
        ]

        # desired distance between segments
        self.segment_distance = particle_size

        # sprites
        self.head_imgs = self.get_head_imgs()
        self.body_img = self.get_body_image()

    # ---------- assets ----------
    def get_head_imgs(self):
        img = pygame.image.load(resource_path("assets/snakehead.jpg")).convert_alpha()
        img = pygame.transform.scale(img, (self.particle_size, self.particle_size))
        return {
            270: pygame.transform.rotate(img, 270),
            90:  pygame.transform.rotate(img, 90),
            180: pygame.transform.rotate(img, 180),
            0:   pygame.transform.rotate(img, 0)
        }

    def get_body_image(self):
        img = pygame.image.load(resource_path("assets/snakebody.jpg")).convert_alpha()
        return pygame.transform.scale(img, (self.particle_size, self.particle_size))

    # ---------- update ----------
    def update(self):
        # 1) move head logically (continuous coordinates, no teleport)
        self.head_pos[0] += self.direction[0] * self.speed
        self.head_pos[1] += self.direction[1] * self.speed

        # 2) push new head node (continuous coords)
        self.nodes.insert(0, self.head_pos.copy())

        # 3) compute frames_per_segment (guard min value 1)
        frames_per_segment = max(1, int(self.segment_distance / max(1e-6, self.speed)))

        # 4) update each body segment by lerping toward the corresponding node
        #    Note: body_segments[0] is effectively the head sprite position; keep it synced
        for i in range(len(self.body_segments)):
            if i == 0:
                # Keep the head-segment position synced to head_pos (continuous)
                self.body_segments[0][0] = self.head_pos[0]
                self.body_segments[0][1] = self.head_pos[1]
                continue

            node_index = i * frames_per_segment
            if node_index >= len(self.nodes):
                # Not enough history yet
                continue

            target = self.nodes[node_index]

            # LERP factor: tuned to 0.3 like your original code
            self.body_segments[i][0] += (target[0] - self.body_segments[i][0]) * 0.3
            self.body_segments[i][1] += (target[1] - self.body_segments[i][1]) * 0.3

        # 5) trim node history to reasonable length
        max_nodes = len(self.body_segments) * frames_per_segment + 100
        if len(self.nodes) > max_nodes:
            # keep the newest max_nodes entries
            self.nodes = self.nodes[:max_nodes]

    def handle_normal_movement(self,event, direction):
        if event.key in [pygame.K_UP, pygame.K_w]:
            self.direction = (0, -1) 
        if event.key in [pygame.K_RIGHT, pygame.K_d]:
            self.direction = (1, 0)
        if event.key in [pygame.K_DOWN, pygame.K_s]:
            self.direction = (0, 1)
        if event.key in [pygame.K_LEFT, pygame.K_a]:
            self.direction = (-1, 0)
        return direction
    # ---------- drawing helpers ----------
    def _wrap_point(self, pos):
        """Return a tuple with wrapped coordinates for drawing: (x % WORLD_SIZE, y % WORLD_SIZE)."""
        return (pos[0] % WORLD_SIZE, pos[1] % WORLD_SIZE)

    def draw(self):
        # Draw body segments (skip index 0 which is head)
        for seg in self.body_segments[1:]:
            rx, ry = self._wrap_point(seg)
            self.screen.blit(self.body_img, (int(rx), int(ry)))

        # choose correct head image
        if self.direction == (-1, 0):
            rotated_head = self.head_imgs[270]
        elif self.direction == (1, 0):
            rotated_head = self.head_imgs[90]
        elif self.direction == (0, -1):
            rotated_head = self.head_imgs[180]
        else:
            rotated_head = self.head_imgs[0]

        # draw head wrapped
        hx, hy = self._wrap_point(self.head_pos)
        self.screen.blit(rotated_head, (int(hx), int(hy)))

    # ---------- controls ----------
    def move_left(self):
        self.direction = (-1, 0)
    def move_right(self):
        self.direction = (1, 0)
    def move_up(self):
        self.direction = (0, -1)
    def move_down(self): 
        self.direction = (0, 1)

    def get_snake_headcords(self):
        """
        Gibt die Kopfposition als Grid-Koordinaten zurück.
        Beispiel: Bei head_pos=(400,400) und particle_size=25 → (16,16)
        """
        gx = int((self.head_pos[0] % WORLD_SIZE) // self.particle_size)
        gy = int((self.head_pos[1] % WORLD_SIZE) // self.particle_size)
        return gx, gy

    # ---------- collision helpers ----------
    def get_head_rect(self, wrapped=True):
        """
        Return a pygame.Rect representing the head position.
        If wrapped==True, return a rect at the wrapped-on-screen coordinates (good for drawing/collisions with on-screen objects).
        If wrapped==False, return continuous coords rect (rarely needed).
        """
        if wrapped:
            hx, hy = self._wrap_point(self.head_pos)
            return pygame.Rect(int(hx), int(hy), self.particle_size, self.particle_size)
        else:
            return pygame.Rect(int(self.head_pos[0]), int(self.head_pos[1]),
                               self.particle_size, self.particle_size)

    # ---------- grow ----------
    def grow(self):
        # append a copy of the current tail segment (continuous coords)
        self.body_segments.append(self.body_segments[-1].copy())
