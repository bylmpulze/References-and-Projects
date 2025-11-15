# spawn_rules.py
import random
from typing import Iterable, Tuple, Optional, List, Dict

Coord = Tuple[int, int]

def should_spawn(last_ms: int, now_ms: int, interval_ms: int, has_active: bool) -> bool:
    """Zeitsteuerung: nur spawnen, wenn keine aktiven Powerups vorhanden und Intervall verstrichen."""
    return (not has_active) and (now_ms - last_ms >= interval_ms)

def pick_powerup_type(available: List[str], rng: random.Random) -> str:
    """Wählt einen Typ deterministisch mit übergebenem RNG."""
    return rng.choice(available)

def pick_spawn_cell(
    grid_w: int,
    grid_h: int,
    forbidden: Iterable[Coord],
    rng: random.Random,
    max_attempts: int = 2000,
) -> Optional[Coord]:
    """Wählt eine freie Zelle, die nicht in forbidden liegt; None, wenn kein Platz."""
    blocked = set(forbidden)
    attempts = 0
    while attempts < max_attempts:
        x = rng.randrange(grid_w)
        y = rng.randrange(grid_h)
        if (x, y) not in blocked:
            return (x, y)
        attempts += 1
    return None

def spawn_one(
    grid_w: int,
    grid_h: int,
    available_types: List[str],
    forbidden: Iterable[Coord],
    rng: Optional[random.Random] = None,
) -> Optional[Dict]:
    """Bereitet ein Power-up-Spawn-Resultat vor: {'x','y','pw_type'} oder None, wenn kein Platz."""
    rng = rng or random.Random()
    cell = pick_spawn_cell(grid_w, grid_h, forbidden, rng)
    if cell is None:
        return None
    pw_type = pick_powerup_type(available_types, rng)
    x, y = cell
    return {"x": x, "y": y, "pw_type": pw_type}
