from powerups import PowerUpMain

def debug_powerup(self, name):
    if name not in PowerUpMain.types:
        print(f"Powerup '{name}' nicht im Register gefunden.")
        return

    entry = PowerUpMain[name]

    print(f"\n--- Debug für Powerup '{name}' ---")
    print("Menu-Objekt:", entry["menu_obj"])
    print("Toggle-Attribut:", entry["toggle_attr"])
    print("Duration-Attribut:", entry["duration_attr"])
    print("Config-Objekt:", entry["config_target"])
    print("Config-Attribut:", entry.get("config_duration", "Nicht gesetzt"))
    print("Bild:", entry["image"])

    # Prüfen, ob wir auf Menu-Attribute zugreifen können
    toggle_value = getattr(entry["menu_obj"], entry["toggle_attr"], None)
    duration_value = getattr(entry["menu_obj"], entry["duration_attr"], None)
    print("Toggle-Wert im Menu:", toggle_value)
    print("Duration-Wert im Menu:", duration_value)
 


if __name__ == "__main__":
    main = PowerUpMain()
    main.menu.settingsMenu_speedx2 = True
    main.debug_powerup("speed_boost_x2")