# test_map.py

from engine.map import GameMap
from utils.serializer import Serializer
from backend.Units import Unit


def print_map_summary(game_map):
    print("\n=== Résumé de la carte ===")
    print(f"Taille : {game_map.width} x {game_map.height}")
    print(f"Nombre d'unités : {len(game_map.units)}")
    print(f"État IA : {game_map.ai_state}")
    print("==========================\n")

def main():
    print("\n--- Création de la carte ---")
    m = GameMap(5, 5)
    print_map_summary(m)

    print("--- Sauvegarde JSON ---")
    Serializer.save_json(m.to_dict(), "save/test_map.json")

    print("--- Sauvegarde PICKLE ---")
    Serializer.save_pickle(m, "save/test_map.pkl")

    print("--- Chargement JSON ---")
    data = Serializer.load_json("save/test_map.json")
    loaded_map = GameMap.from_dict(data, Unit)

    print_map_summary(loaded_map)


if __name__ == "__main__":
    main()
