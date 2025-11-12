import os
import time
import hashlib
from pathlib import Path

#Game_Size
SCREEN_SIZE = 800
TOPBAR_HEIGHT = 40
GAME_SIZE = SCREEN_SIZE - TOPBAR_HEIGHT
PARTICLE_SIZE = 25

#Player
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

PLAYER_KEYS = list(PLAYER_COLORS.keys())  # ["p1","p2","p3","p4""p5","p6","p7","p8""p9","p10","p11","p12"]

def compute_project_hash(base_dir: str = ".") -> str:
    """Erzeugt einen stabilen SHA1-Hash über alle .py-Dateien im Verzeichnis (rekursiv)."""
    h = hashlib.sha1()
    for root, _, files in os.walk(base_dir):
        for f in sorted(files):
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    with open(path, "rb") as fh:
                        while chunk := fh.read(8192):
                            h.update(chunk)
                except Exception as e:
                    print(f"[WARN] Datei übersprungen: {path} ({e})")
    return h.hexdigest()[:8]


def benchmark_compute_project_hash(base_dir: str = ".", repeat: int = 5):
    """Misst die durchschnittliche Laufzeit des Hash-Vorgangs."""
    durations = []
    print(f"🔍 Starte Benchmark für compute_project_hash('{base_dir}') ...")

    for i in range(repeat):
        start = time.perf_counter()
        _ = compute_project_hash(base_dir)
        end = time.perf_counter()
        dur = (end - start) * 1000  # ms
        durations.append(dur)
        print(f"  Durchlauf {i+1}: {dur:.2f} ms")

    avg = sum(durations) / len(durations)
    print(f"⏱️  Durchschnitt: {avg:.2f} ms für {repeat} Durchläufe "
          f"({len(durations)} Dateien gescannt)")


VERSION = compute_project_hash(Path(__file__).parent)

if __name__ == "__main__":
    benchmark_compute_project_hash("..", repeat=10)
