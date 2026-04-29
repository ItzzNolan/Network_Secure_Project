import math
import random
from typing import List, Optional, Dict
from backend.carte import Carte
from backend.Units import Unit
from ia.general import General, Action, TypeAction, make_general
from ipc.ipc_python import IPCClient
from moteur.propriete import Propriete

TEAM_COLORS = [
    (70, 130, 255), (255, 70,  70), (80,  200, 80), (255, 200, 50),
    (200, 80,  255), (255, 150, 50), (80,  220, 220), (255, 120, 180)
]
TEAM_NAMES = ["BLEU", "ROUGE", "VERT", "JAUNE", "VIOLET", "ORANGE", "CYAN", "ROSE"]

def get_team_color(team_id:int): return TEAM_COLORS[team_id % len(TEAM_COLORS)]
def get_team_name(team_id:int): return TEAM_NAMES[team_id % len(TEAM_NAMES)]

class Jeu:
    def __init__(self, largeur:int = 120, hauteur:int = 120):
        self.carte = Carte(largeur=largeur, hauteur=hauteur)
        self.unites: List[Unit] = []
        self._tour = 0
        self.generaux: Dict[int, General] = {}
        
        self.player_id = 0
        self.next_player_id = 0

        self.ipc = IPCClient()
        self.propriete = Propriete(self.player_id, self.ipc) 

    def get_ipc(self):
        return self.ipc

    def ajouter_joueur(self, ia_name:str, units_config:dict):
        pid = self.next_player_id
        self.next_player_id += 1
        general = make_general(ia_name, id_player=pid)
        self.generaux[pid] = general
        print(f"[JEU] Nouveau joueur {pid} ({get_team_name(pid)}) avec IA: {general.name}")
        self._spawn_units_for_player(pid, units_config)
        return pid
    
    def _spawn_units_for_player(self, player_id: int, units_config: dict):
        for unit_type, count in units_config.items():
            for _ in range(count):
                x = random.randint(0, self.carte.largeur-1)
                y = random.randint(0, self.carte.hauteur-1)
                self.ajouter_unite(unit_type, x, y, player_id)

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
            if getattr(u, 'id', -1) == unit_id: return u
        return None

    def _executer_move(self, unit: Unit, target_pos):
        if unit.coords is None or target_pos is None: return
        ux, uy = unit.coords
        tx, ty = target_pos
        dx, dy = tx - ux, ty - uy
        vitesse = getattr(unit, 'Speed', 1.0) or 1.0
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 0.1: return
        if distance <= vitesse: unit.coords = (float(tx), float(ty))
        else:
            ratio = vitesse / distance
            unit.coords = (ux + dx * ratio, uy + dy * ratio)
        if unit.equipe == self.player_id:
            self.ipc.envoyer({"type": "UPDATE", "action": "MOVE", "entity_id": unit.id, "x": unit.coords[0], "y": unit.coords[1], "player_id": unit.equipe})

    def envoyer_join(self):
        units_data = []
        for u in self.unites:
            if u.coords and u.equipe == self.player_id:
                u_type = getattr(u, 'Unit', getattr(u, 'unit_type', 'Knight'))
                units_data.append({"entity_id": u.id, "unit_type": u_type, "x": u.coords[0], "y": u.coords[1]})
        ia_name = self.generaux[self.player_id].name if self.player_id in self.generaux else "Unknown"
        self.ipc.envoyer({"type": "JOIN", "player_id": self.player_id, "player_name": get_team_name(self.player_id), "ia": ia_name, "units": units_data})

    def _executer_attack(self, attacker: Unit, target: Unit):
        if not attacker.alive or not target.alive: return
        dist = abs(attacker.coords[0] - target.coords[0]) + abs(attacker.coords[1] - target.coords[1])
        if not attacker.can_attack(): return
        
        if dist <= getattr(attacker, 'Max_Range', 1.5) + 1:
            attacker.target = target
            attacker.inflict_damage()

            if attacker.equipe == self.player_id:
                self.ipc.envoyer({"type": "UPDATE", "action": "ATTACK", "attacker_id": attacker.id, "target_id": target.id, "damage": getattr(attacker, 'Attack', 0), "player_id": attacker.equipe})

            if target.HP <= 0:
                target.HP = 0
                target.alive = False
                if attacker.equipe == self.player_id:
                    self.ipc.envoyer({"type": "UPDATE", "action": "DIE", "entity_id": target.id, "player_id": attacker.equipe})

    def _executer_action(self, action: Action):
        unit = self.get_unit_by_id(action.unit_id)
        if not unit or not unit.alive: return
        if action.type in [TypeAction.MOVE, TypeAction.FORM_UP]:
            self._executer_move(unit, action.target_pos)
        elif action.type == TypeAction.ATTACK:
            target = self.get_unit_by_id(action.target_id)
            if target: self._executer_attack(unit, target)

    def mettre_a_jour(self):
        self._tour += 1
        for unit in self.unites:
            if hasattr(unit, 'timer'): unit.timer += 1

        all_actions = []
        if self.player_id in self.generaux:
            general = self.generaux[self.player_id]
            unites_equipe = [u for u in self.unites if u.alive and u.equipe == self.player_id and u.coords]
            if unites_equipe:
                try: all_actions.extend(general.decider_actions(unites_equipe, self))
                except Exception as e: print(f"[JEU] Erreur IA: {e}")

        move_actions = [a for a in all_actions if a.type in [TypeAction.MOVE, TypeAction.FORM_UP]]
        attack_actions = [a for a in all_actions if a.type == TypeAction.ATTACK]
        random.shuffle(move_actions)
        random.shuffle(attack_actions)

        for action in move_actions: self._executer_action(action)
        for action in attack_actions: self._executer_action(action)
        self.unites = [u for u in self.unites if u.alive]

    def appliquer_message(self, message: Dict):
        type_msg = message.get("type", "").lower()
        player_id = int(message.get("player_id", -1))
        if player_id == self.player_id: return

        if type_msg == "join":
            units = message.get("units", [])
            ia = message.get("ia", "braindead")
            self.generaux[player_id] = make_general(ia, id_player=player_id)
            for u in units:
                self.ajouter_unite(nom_unite=u.get("unit_type"), x=u.get("x"), y=u.get("y"), equipe=player_id)
            
            entities = []
            for u in self.unites:
                if u.alive:
                    u_type = getattr(u, 'Unit', getattr(u, 'unit_type', 'Knight'))
                    entities.append({"entity_id": u.id, "owner_id": u.equipe, "unit_type": u_type, "x": u.coords[0], "y": u.coords[1], "hp": u.HP})
            self.ipc.envoyer({"type": "FULL_STATE", "player_id": self.player_id, "entities": entities})

        elif type_msg == "full_state":
            for ent in message.get("entities", []):
                u = self.get_unit_by_id(ent.get("entity_id"))
                if u:
                    u.coords = (ent.get("x"), ent.get("y"))
                    u.HP = ent.get("hp")
                    u.equipe = ent.get("owner_id")
                    self.carte.placer_unite(u, int(ent.get("x")), int(ent.get("y")))
                else:
                    self.ajouter_unite(nom_unite=ent.get("unit_type"), x=ent.get("x"), y=ent.get("y"), equipe=ent.get("owner_id"))

        elif type_msg == "update":
            action = message.get("action", "").lower()
            if action == "move":
                u = self.get_unit_by_id(message.get("entity_id"))
                if u: self._executer_move(u, (message.get("x"), message.get("y")))
            elif action == "attack":
                att = self.get_unit_by_id(message.get("attacker_id"))
                tgt = self.get_unit_by_id(message.get("target_id"))
                if att and tgt: self._executer_attack(att, tgt)
            elif action == "die":
                u = self.get_unit_by_id(message.get("entity_id"))
                if u:
                    u.HP, u.alive = 0, False
                    self.carte.retirer_unite(u)

        elif type_msg == "disconnect":
            if player_id in self.generaux: del self.generaux[player_id]
            for u in self.unites:
                if getattr(u, 'equipe', -1) == player_id:
                    u.HP, u.alive = 0, False
                    self.carte.retirer_unite(u)

    def disconnect(self):
        self.ipc.envoyer({"type": "DISCONNECT", "player_id": self.player_id})

    def check_victory(self):
        if len(self.generaux)<2: return None
        alive_by_team = {}
        for unit in self.unites:
            if unit and getattr(unit, "alive", False):
                team = getattr(unit, "equipe", None)
                if team is not None:
                    alive_by_team[team] = alive_by_team.get(team, 0)+1
        alive_teams = [t for t,c in alive_by_team.items() if c>0]
        if len(alive_teams)==0: return -1
        if len(alive_teams)==1: return alive_teams[0]
        return None

    @property
    def tick(self) -> int: return self._tour
    def raycast(self, x, y) -> bool: return True
    def enemy_in_los(self, unit) -> List:
        return [u for u in self.unites if u.alive and u.equipe != unit.equipe and u.coords]
    def nearest_enemy(self, unit) -> Optional[Unit]:
        enemies = self.enemy_in_los(unit)
        if not enemies: return None
        return min(enemies, key=lambda e: abs(unit.coords[0]-e.coords[0]) + abs(unit.coords[1]-e.coords[1]))
    def all_seen_enemies(self, id_player: int) -> List: return [u for u in self.unites if u.alive and u.equipe != id_player and u.coords]
    def all_seen_allies(self, id_player: int) -> List: return [u for u in self.unites if u.alive and u.equipe == id_player and u.coords]
    def distance_tiles(self, pos1, pos2) -> int: return abs(int(pos1[0]) - int(pos2[0])) + abs(int(pos1[1]) - int(pos2[1])) if pos1 and pos2 else 999
    def is_walkable(self, pos) -> bool: return self.carte.est_dans_grille(int(pos[0]), int(pos[1])) if pos else False
