# engine/map.py

class Tile:
    """Case élémentaire de la carte."""
    def __init__(self, terrain="grass", walkable=True):
        self.terrain = terrain
        self.walkable = walkable

    def to_dict(self):
        return {
            "terrain": self.terrain,
            "walkable": self.walkable
        }

    @staticmethod
    def from_dict(data):
        return Tile(
            terrain=data["terrain"],
            walkable=data["walkable"]
        )


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Grille NxM de tuiles
        self.grid = [
            [Tile() for _ in range(width)]
            for _ in range(height)
        ]

        # Unités présentes sur la carte (joueurs, IA, ennemis…)
        self.units = []

        # Etat mental de l’IA (ordres, objectifs…)
        self.ai_state = {
            "current_orders": [],
            "target": None,
            "mode": "idle"
        }

    # -------------------
    #  Export JSON-friendly
    # -------------------
    def to_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "grid": [
                [tile.to_dict() for tile in row]
                for row in self.grid
            ],
            "units": [u.to_dict() for u in self.units],
            "ai_state": self.ai_state
        }

    # -------------------
    #  Reconstruction depuis JSON
    # -------------------
    @staticmethod
    def from_dict(data, unit_class):
        gamemap = GameMap(data["width"], data["height"])

        # Reconstruire la grille
        gamemap.grid = [
            [Tile.from_dict(tile_data) for tile_data in row]
            for row in data["grid"]
        ]

        # Reconstruire les unités
        gamemap.units = [
            unit_class.from_dict(u)
            for u in data["units"]
        ]

        gamemap.ai_state = data["ai_state"]
        return gamemap
