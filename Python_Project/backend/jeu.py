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
        self.generaux: Dict[int, General] = {}
        self.next_player_id = 0
        self.ipc = None
        self.player_id = None

        if general_bleu:
            gen_bleu = make_general(general_bleu, id_player=0)
            self.generaux[0] = gen_bleu
            self.next_player_id = 1
        if general_rouge:
            gen_rouge = make_general(general_rouge, id_player=1)
            self.generaux[1] = gen_rouge
            self.next_player_id = 2

    def ajouter_joueur(self, ia_name: str, units_config: dict):
        pid = self.next_player_id
        self.next_player_id += 1
        general = make_general(ia_name, id_player=pid)
        self.generaux[pid] = general
        print(f"[JEU] Nouveau joueur {pid} avec IA: {general.name}")
        self._spawn_units_for_player(pid, units_config)
        return pid

    def _spawn_units_for_player(self, player_id: int, units_config: dict):
        for unit_type, count in units_config.items():
            for _ in range(count):
                x = random.randint(0, self.carte.largeur - 1)
                y = random.randint(0, self.carte.hauteur - 1)
                self.ajouter_unite(unit_type, x, y, player_id)

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

        # RESEAU : envoyer le déplacement SEULEMENT si c'est notre unité
        if self.ipc and self.player_id is not None:
            mon_equipe = self.player_id - 1
            if unit.equipe == mon_equipe:
                self.ipc.envoyer({
                    "type": "UPDATE", "action": "MOVE",
                    "entity_id": unit.id,
                    "x": unit.coords[0], "y": unit.coords[1],
                    "player_id": self.player_id
                })

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
            hp_avant = target.HP
            attacker.target = target
            attacker.inflict_damage()
            degats = hp_avant - target.HP

            # RESEAU : envoyer l'attaque SEULEMENT si c'est notre unité
            if self.ipc and self.player_id is not None:
                mon_equipe = self.player_id - 1
                if attacker.equipe == mon_equipe:
                    self.ipc.envoyer({
                        "type": "UPDATE", "action": "ATTACK",
                        "attacker_id": attacker.id, "target_id": target.id,
                        "damage": degats,
                        "player_id": self.player_id
                    })

            if target.HP <= 0:
                target.HP = 0
                target.alive = False

                # RESEAU : envoyer la mort SEULEMENT si c'est nous qui avons tué
                if self.ipc and self.player_id is not None:
                    mon_equipe = self.player_id - 1
                    if attacker.equipe == mon_equipe:
                        self.ipc.envoyer({
                            "type": "UPDATE", "action": "DIE",
                            "entity_id": target.id,
                            "player_id": self.player_id
                        })

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

        # RESEAU : recevoir et appliquer les messages
        if self.ipc:
            messages = self.ipc.recevoir()
            for msg in messages:
                if msg.get("player_id") == self.player_id:
                    continue

                msg_type = msg.get("type", "").lower()
                action = msg.get("action", "").lower()

                if msg_type == "join":
                    print(f"[RESEAU] Joueur {msg.get('player_id')} rejoint. Envoi du FULL_STATE.")
                    self._reseau_handle_join(msg.get("units", []), msg.get("player_id"))
                    self.reseau_envoyer_state()

                elif msg_type == "full_state":
                    print(f"[RESEAU] Reçu l'état complet du joueur {msg.get('player_id')}")
                    self._reseau_handle_join(msg.get("entities", []), msg.get("player_id"))

                elif msg_type == "update" and action == "move":
                    unit = self.get_unit_by_id(msg["entity_id"])
                    if unit:
                        unit.coords = (msg["x"], msg["y"])

                elif msg_type == "update" and action == "attack":
                    target = self.get_unit_by_id(msg.get("target_id"))
                    if target and target.alive:
                        damage = msg.get("damage", 0)
                        target.HP -= damage
                        if target.HP <= 0:
                            target.alive = False

                elif msg_type == "update" and action == "die":
                    unit = self.get_unit_by_id(msg["entity_id"])
                    if unit:
                        unit.alive = False
                        unit.HP = 0

                elif msg_type == "disconnect":
                    print(f"[RESEAU] Joueur {msg.get('player_id')} quitte")

        for unit in self.unites:
            if hasattr(unit, 'timer'):
                unit.timer += 1

        all_actions: List[Action] = []
        equipes = list(self.generaux.items())
        random.shuffle(equipes)

        for equipe, general in equipes:
            # BRIDAGE IA : On ne fait réfléchir QUE notre propre équipe !
            if self.ipc and self.player_id is not None:
                mon_equipe = self.player_id - 1
                if equipe != mon_equipe:
                    continue

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

    def check_victory(self):
        alive_by_team = {}
        for unit in self.unites:
            if unit is None:
                continue
            if not getattr(unit, "alive", False):
                continue
            team = getattr(unit, "equipe", None)
            if team is None:
                continue
            alive_by_team[team] = alive_by_team.get(team, 0) + 1

        alive_teams = [t for t, c in alive_by_team.items() if c > 0]

        if len(self.generaux) < 2:
            return None
        if len(alive_teams) == 0:
            return -1
        if len(alive_teams) == 1:
            return alive_teams[0]
        return None

    def trouver_ennemi_proche(self, unite):
        ennemi = self.nearest_enemy(unite)
        if ennemi:
            dist = self.distance_tiles(unite.coords, ennemi.coords)
            return ennemi, dist
        return None, None

    def deplacer_vers(self, unite, cible_x, cible_y):
        self._executer_move(unite, (cible_x, cible_y))

    def disconnect(self):
        if self.ipc:
            self.ipc.envoyer({"type": "DISCONNECT", "player_id": self.player_id})
            self.ipc.fermer()

    def _reseau_handle_join(self, units_list: list, owner_player_id: int):
        equipe_distante = owner_player_id - 1

        for u_data in units_list:
            entity_id = u_data.get("entity_id")
            existing_unit = self.get_unit_by_id(entity_id)

            if existing_unit:
                existing_unit.coords = (u_data.get("x"), u_data.get("y"))
                existing_unit.HP = u_data.get("hp", existing_unit.HP)
            else:
                nom_unite = u_data.get("unit_type", "pikeman")
                nouvelle_unite = Unit(nomUnite=nom_unite)
                nouvelle_unite.equipe = equipe_distante
                nouvelle_unite.coords = (float(u_data.get("x")), float(u_data.get("y")))
                nouvelle_unite.id = entity_id
                nouvelle_unite.HP = u_data.get("hp", nouvelle_unite.HP)
                self.unites.append(nouvelle_unite)

    def reseau_envoyer_join(self):
        if not self.ipc or self.player_id is None:
            return
        mes_unites = []
        mon_equipe = self.player_id - 1
        for u in self.unites:
            if u.equipe == mon_equipe:
                mes_unites.append({
                    "entity_id": u.id,
                    "unit_type": getattr(u, 'nomUnite', 'unknown'),
                    "x": u.coords[0] if u.coords else 0,
                    "y": u.coords[1] if u.coords else 0,
                    "hp": u.HP,
                    "version": 1
                })
        msg = {"type": "JOIN", "player_id": self.player_id, "units": mes_unites}
        self.ipc.envoyer(msg)

    def reseau_envoyer_state(self):
        if not self.ipc or self.player_id is None:
            return
        toutes_les_unites = []
        for u in self.unites:
            toutes_les_unites.append({
                "entity_id": u.id,
                "unit_type": getattr(u, 'nomUnite', 'unknown'),
                "x": u.coords[0] if u.coords else 0,
                "y": u.coords[1] if u.coords else 0,
                "hp": u.HP,
                "version": getattr(u, "version", 1)
            })
        msg = {"type": "FULL_STATE", "player_id": self.player_id, "entities": toutes_les_unites}
        self.ipc.envoyer(msg)
