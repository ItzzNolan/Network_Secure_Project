import math
import random
from typing import List, Optional, Dict
from backend.carte import Carte
from backend.Units import Unit
from ia.general import General, Action, TypeAction, make_general

class Jeu:
    def __init__(self, general_bleu: str = "braindead", general_rouge: str = "braindead", 
                 largeur: int = 120, hauteur: int = 120):
        self.carte = Carte(largeur=largeur, hauteur=hauteur)
        self.unites: List[Unit] = []
        self._tour = 0
        self.generaux: Dict[int, General] = {
            0: make_general(general_bleu, id_player=0),
            1: make_general(general_rouge, id_player=1)
        }
        
        print(f"[JEU] General Bleu: {self.generaux[0].name}")
        print(f"[JEU] General Rouge: {self.generaux[1].name}")
        print(f"[JEU] Carte: {largeur}x{hauteur}")

    @property
    def tick(self) -> int:
        return self._tour
    
    def raycast(self, x, y) -> bool:
        return True
    
    def enemy_in_los(self, unit) -> List:
        los_range = 20
        enemies = []
        for other in self.unites:
            if not other.alive:
                continue
            if other.equipe == unit.equipe:
                continue
            if other.coords is None or unit.coords is None:
                continue
            dist = self.distance_tiles(unit.coords, other.coords)
            if dist <= los_range and self.raycast(unit.coords, other.coords):
                enemies.append(other)
        return enemies
    
    def nearest_enemy(self, unit) -> Optional[Unit]:
        enemies = [u for u in self.unites if u.alive and u.equipe != unit.equipe and u.coords]
        if not enemies:
            return None
        return min(enemies, key=lambda e: self.distance_tiles(unit.coords, e.coords))
    
    def all_seen_enemies(self, id_player: int) -> List:
        return [u for u in self.unites if u.alive and u.equipe != id_player and u.coords]
    
    def all_seen_allies(self, id_player: int) -> List:
        return [u for u in self.unites if u.alive and u.equipe == id_player and u.coords]
    
    def distance_tiles(self, pos1, pos2) -> int:
        if pos1 is None or pos2 is None:
            return 999
        return abs(int(pos1[0]) - int(pos2[0])) + abs(int(pos1[1]) - int(pos2[1]))
    
    def is_walkable(self, pos) -> bool:
        if pos is None:
            return False
        x, y = pos
        return self.carte.est_dans_grille(int(x), int(y))
    
    def map_ascii(self) -> List[str]:
        grid = [["." for _ in range(self.carte.largeur)] for _ in range(self.carte.hauteur)]
        for unit in self.unites:
            if not unit.alive or not unit.coords:
                continue
            x, y = int(unit.coords[0]), int(unit.coords[1])
            if 0 <= x < self.carte.largeur and 0 <= y < self.carte.hauteur:
                grid[y][x] = str(unit.equipe)
        return ["".join(row) for row in grid]

    def ajouter_unite(self, nom_unite: str, x: int, y: int, equipe: int = 0):
        if self.carte.est_dans_grille(x, y):
            nouvelle_unite = Unit(nomUnite=nom_unite)
            nouvelle_unite.equipe = equipe
            nouvelle_unite.coords = (float(x), float(y))
            nouvelle_unite.id = len(self.unites)
            self.unites.append(nouvelle_unite)
            self.carte.placer_unite(nouvelle_unite, x, y)

    def get_unit_by_id(self, unit_id: int) -> Optional[Unit]:
        for u in self.unites:
            if u.id == unit_id:
                return u
        return None

    def _executer_move(self, unit: Unit, target_pos):
        if unit.coords is None or target_pos is None:
            return
        
        ux, uy = unit.coords
        tx, ty = target_pos
        
        dx = tx - ux
        dy = ty - uy
        
        vitesse = getattr(unit, 'Speed', 1.0)
        if vitesse is None:
            vitesse = 1.0
        
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 0.1:
            return
        
        if distance <= vitesse:
            unit.coords = (float(tx), float(ty))
        else:
            ratio = vitesse / distance
            unit.coords = (ux + dx * ratio, uy + dy * ratio)

    def _executer_attack(self, attacker: Unit, target: Unit):
        if not attacker.alive or not target.alive:
            return
        if attacker.coords is None or target.coords is None:
            return
        dist = self.distance_tiles(attacker.coords, target.coords)
        portee = getattr(attacker, 'Max_Range', 1.5)
        if portee is None:
            portee = 1.5
        
        if not attacker.can_attack():
            return
        
        if dist <= portee + 1:
            attacker.target = target
            attacker.inflict_damage()
            
            if target.HP <= 0:
                target.HP = 0
                target.alive = False

    def _executer_action(self, action: Action):
        unit = self.get_unit_by_id(action.unit_id)
        if unit is None or not unit.alive:
            return
        
        if action.type == TypeAction.MOVE:
            if action.target_pos:
                self._executer_move(unit, action.target_pos)
        
        elif action.type == TypeAction.ATTACK:
            if action.target_id is not None:
                target = self.get_unit_by_id(action.target_id)
                if target:
                    self._executer_attack(unit, target)
        
        elif action.type == TypeAction.HOLD:
            pass
        
        elif action.type == TypeAction.FORM_UP:
            if action.target_pos:
                self._executer_move(unit, action.target_pos)

    def mettre_a_jour(self):
        self._tour += 1
        
        for unit in self.unites:
            if hasattr(unit, 'timer'):
                unit.timer += 1
        
        all_actions: List[Action] = []
        
        equipes = list(self.generaux.items())
        random.shuffle(equipes)
        
        for equipe, general in equipes:
            unites_equipe = [u for u in self.unites if u.alive and u.equipe == equipe and u.coords]
            
            if not unites_equipe:
                continue
            
            try:
                actions = general.decider_actions(unites_equipe, self)
                all_actions.extend(actions)
            except Exception as e:
                print(f"[JEU] Erreur general {general.name}: {e}")
        
        move_actions = [a for a in all_actions if a.type in [TypeAction.MOVE, TypeAction.FORM_UP]]
        attack_actions = [a for a in all_actions if a.type == TypeAction.ATTACK]
        
        random.shuffle(move_actions)
        random.shuffle(attack_actions)
        
        for action in move_actions:
            self._executer_action(action)
        for action in attack_actions:
            self._executer_action(action)
        
        self.unites = [u for u in self.unites if u.alive]

    def check_victory(self) -> Optional[int]:
        alive_0 = [u for u in self.unites if u.alive and u.equipe == 0]
        alive_1 = [u for u in self.unites if u.alive and u.equipe == 1]
        
        if not alive_0 and alive_1:
            return 1
        if not alive_1 and alive_0:
            return 2
        if not alive_0 and not alive_1:
            return 0
        return None

    def trouver_ennemi_proche(self, unite):
        ennemi = self.nearest_enemy(unite)
        if ennemi:
            dist = self.distance_tiles(unite.coords, ennemi.coords)
            return ennemi, dist
        return None, None

    def deplacer_vers(self, unite, cible_x, cible_y):
        self._executer_move(unite, (cible_x, cible_y))