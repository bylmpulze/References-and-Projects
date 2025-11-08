import sys
import pygame
import random
from game.powerups import powerupconfig

PLAYER_COLORS = {
    "p1":  (0, 200, 0),
    "p2":  (220, 40, 40),
    "p3":  (40, 120, 220),
    "p4":  (230, 170, 30),
    "p5":  (160, 32, 240),
    "p6":  (255, 105, 180),
    "p7":  (0, 200, 200),
    "p8":  (255, 140, 0),
    "p9":  (128, 0, 0),
    "p10": (0, 128, 128),
    "p11": (139, 69, 19),
    "p12": (112, 128, 144),
}

PLAYER_KEYS = list(PLAYER_COLORS.keys())  # ["p1","p2","p3","p4"]

def tint_surface(src: pygame.Surface, color: tuple[int,int,int]) -> pygame.Surface:
    tinted = src.copy()
    mask = pygame.Surface(src.get_size(), flags=pygame.SRCALPHA)
    mask.fill((*color, 255))
    tinted.blit(mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    return tinted

def make_snake_skins(body_img: pygame.Surface, head_img: pygame.Surface, color: tuple[int,int,int]):
    return (
        tint_surface(head_img, color),   # head
        tint_surface(body_img, color),   # body
    )

def rank_of_id(snake_id: str, all_ids: list[str]) -> int:
    # numerisch sortieren, höhere ID = höherer Player
    def id_to_int(s):
        # extrahiere Ziffern oder fallback auf int(s)
        num = ''.join(ch for ch in s if ch.isdigit())
        try:
            return int(num) if num else int(s)
        except ValueError:
            # lexikalisch fallback
            return 0
    ordered = sorted(all_ids, key=id_to_int)
    return ordered.index(snake_id)

def key_for_rank(rank: int) -> str:
    # clamp auf verfügbares Farbspektrum
    if rank < 0:
        rank = 0
    if rank >= len(PLAYER_KEYS):
        rank = len(PLAYER_KEYS) - 1
    return PLAYER_KEYS[rank]

def draw_other_snakes(other_snakes: dict[str, list[tuple[int,int]]],
                      particle: int, screen: pygame.Surface,
                      body_img: pygame.Surface, head_img: pygame.Surface):
    """other_snakes: {snake_id: [(x,y), ...]}"""
    all_ids = list(other_snakes.keys())

    # Precompute skins per player key
    predefined_skins = {
        pk: make_snake_skins(body_img, head_img, PLAYER_COLORS[pk])
        for pk in PLAYER_KEYS
    }

    for snake_id, segments in other_snakes.items():
        r = rank_of_id(snake_id, all_ids)
        pk = key_for_rank(r)  # p1..p4 nach Rang der ID
        head_surf, body_surf = predefined_skins[pk]

        for i, (x, y) in enumerate(segments):
            px, py = int(x * particle), int(y * particle)
            if i == 0:
                screen.blit(head_surf, (px, py))
            else:
                screen.blit(body_surf, (px, py))

def load_or_make_placeholders(cell: int = 24) -> tuple[pygame.Surface, pygame.Surface]:
    # Try loading disk sprites; otherwise create simple placeholders
    try:
        head = pygame.image.load("head_img.png").convert_alpha()
        body = pygame.image.load("body_img.png").convert_alpha()
        head = pygame.transform.smoothscale(head, (cell, cell))
        body = pygame.transform.smoothscale(body, (cell, cell))
        return body, head
    except Exception:
        body = pygame.Surface((cell, cell), pygame.SRCALPHA)
        head = pygame.Surface((cell, cell), pygame.SRCALPHA)
        # simple shading so tint shows differently on head/body
        body.fill((220, 220, 220))
        pygame.draw.rect(body, (180, 180, 180), (0, 0, cell, cell), 3)
        head.fill((240, 240, 240))
        pygame.draw.circle(head, (160, 160, 160), (cell//2, cell//2), cell//3, 0)
        return body, head

def preview_colors():
    pygame.init()
    pygame.display.set_caption("Snake Color Preview")
    font = pygame.font.SysFont(None, 18)

    cell = 28
    padding = 16
    per_row = 6  # how many previews per row
    count = len(PLAYER_COLORS)
    rows = (count + per_row - 1) // per_row

    # Each preview tile size
    tile_w = cell * 3 + padding * 2  # head + 2 body segments horizontally
    tile_h = cell + 28 + padding * 2 # snake row + label row

    width = per_row * tile_w
    height = rows * tile_h
    screen = pygame.display.set_mode((width, height))

    body_img, head_img = load_or_make_placeholders(cell)

    # Pre-tint skins
    tinted = {}
    for key, col in PLAYER_COLORS.items():
        head_s, body_s = make_snake_skins(body_img, head_img, col)
        tinted[key] = (head_s, body_s)

    clock = pygame.time.Clock()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

        screen.fill((20, 20, 24))

        # Draw grid of previews
        idx = 0
        for key in PLAYER_COLORS.keys():
            r = idx // per_row
            c = idx % per_row
            x0 = c * tile_w + padding
            y0 = r * tile_h + padding

            head_s, body_s = tinted[key]

            # draw head + two body segments
            screen.blit(head_s, (x0, y0))
            screen.blit(body_s, (x0 + cell, y0))
            screen.blit(body_s, (x0 + cell * 2, y0))

            # label
            label = f"{key}  {PLAYER_COLORS[key]}"
            text = font.render(label, True, (230, 230, 230))
            screen.blit(text, (x0, y0 + cell + 6))

            idx += 1

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def get_random_food_coords(snake,existing_food_cords):
    """ Generate random food coordinates not colliding with snake or existing food. """
    while True:
        coords = [random.randint(0, 27), random.randint(0, 27)]
        if coords not in snake and coords not in existing_food_cords:
            return coords


def handle_snake_collisions(new_head, snake, other_snakes, immunity_collected_time) -> bool:
    """
    Check if the snake collides with itself or other snakes. Considers immunity.
    """

    elapsed = pygame.time.get_ticks() - (immunity_collected_time or 0)
    if elapsed < powerupconfig.extra_life_duration:
        return False  # immune to collisions

    # self collision
    if new_head in snake:
        return True

    for _, other_snake in other_snakes.items():
        if new_head in other_snake:
            return True

    return False

if __name__ == "__main__":
    preview_colors()