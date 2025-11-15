import pygame
from game.helper import resource_path


class Snake:
    def __init__(self, particle_size=25, speed=4):
        self.particle_size = particle_size
        self.speed = speed  # Head-Speed in px per frame
        self.direction = (1, 0)  # Start Richtung: rechts
        self.head_pos = [400.0, 400.0]  # float für smooth Lerp

        # Node-Liste: speichert jede Head-Position
        self.nodes = [self.head_pos.copy()]

        # Body Segmente (float für smooth movement)
        self.body_segments = [
            self.head_pos.copy(),
            [self.head_pos[0]-particle_size, self.head_pos[1]],
            [self.head_pos[0]-2*particle_size, self.head_pos[1]]
        ]

        # Abstand zwischen Segmenten
        self.segment_distance = particle_size

        # Sprites
        self.head_imgs = self.get_head_imgs()
        self.body_img = self.get_body_image()

    def get_head_imgs(self):
        img = pygame.image.load(resource_path("assets/snakehead.jpg")).convert_alpha()
        img = pygame.transform.scale(img, (self.particle_size, self.particle_size))
        return {270 : pygame.transform.rotate(img, 270),
                90:  pygame.transform.rotate(img, 90),
                180: pygame.transform.rotate(img, 180),
                0: pygame.transform.rotate(img, 0)}

    def get_body_image(self):
        img = pygame.image.load(resource_path("assets/snakebody.jpg")).convert_alpha()
        return pygame.transform.scale(img, (self.particle_size, self.particle_size))

    def update(self):
        # 1) Head bewegen
        self.head_pos[0] += self.direction[0] * self.speed
        self.head_pos[1] += self.direction[1] * self.speed

        # 2) Node hinzufügen (jedes Frame)
        self.nodes.insert(0, self.head_pos.copy())

        # 3) Body Segmente smooth lerpen
        frames_per_segment = int(self.segment_distance / self.speed)

        for i in range(len(self.body_segments)):
            if i == 0:
                continue  # Segment 0 = Head
            else:
                node_index = i * frames_per_segment - 1
                if node_index >= len(self.nodes):
                    continue
                target = self.nodes[node_index]

            # Lerp: sanft nachziehen
            self.body_segments[i][0] += (target[0] - self.body_segments[i][0]) * 0.3
            self.body_segments[i][1] += (target[1] - self.body_segments[i][1]) * 0.3

        # 4) Node-Liste trimmen, um Speicher zu sparen
        max_nodes = len(self.body_segments) * frames_per_segment + 100
        if len(self.nodes) > max_nodes:
            self.nodes = self.nodes[:max_nodes]

    def draw(self, screen):
        # Body zuerst (ohne Head)
        for seg in self.body_segments[1:]:
            screen.blit(self.body_img, (int(seg[0]), int(seg[1])))

        # Head zuletzt
        if self.direction == (-1, 0):
            rotated_head = self.head_imgs[270]
        elif self.direction == (1, 0):
            rotated_head = self.head_imgs[90]
        elif self.direction ==  (0, -1):
            rotated_head = self.head_imgs[180]
        else:
            rotated_head = self.head_imgs[0]

        screen.blit(rotated_head, (int(self.head_pos[0]), int(self.head_pos[1])))

    # Richtungsfunktionen
    def move_left(self):
        self.direction = (-1, 0)
    def move_right(self): 
        self.direction = (1, 0)
    def move_up(self):
        self.direction = (0, -1)
    def move_down(self):
        self.direction = (0, 1)

    def get_head_rect(self):
        return pygame.Rect( self.head_pos[0],
                            self.head_pos[1],
                            self.head_pos[0]+self.particle_size,
                            self.head_pos[1]+self.particle_size) 
    

    # Optional: Body Segment hinzufügen (Wachstum)
    def grow(self):
        # Füge neues Segment an der Tail-Endposition hinzu
        tail = self.body_segments[-1].copy()
        self.body_segments.append(tail)
