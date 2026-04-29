import math, random
from typing import List, Optional, Dict
from backend.carte import Carte
from backend.Units import Unit
from ia.general import General, Action, TypeAction, make_general
from ipc.ipc_python import IPCClient

TEAM_NAMES = ["BLEU", "ROUGE", "VERT", "JAUNE"]
TEAM_COLORS = [(70,130,255), (255,70,70), (80,200,80), (255,200,50)]
def get_team_name(tid): return TEAM_NAMES[tid % 4]
def get_team_color(tid): return TEAM_COLORS[tid % 4]

class Jeu:
    def __init__(self, largeur=120, hauteur=120, port_python=9998):
        self.carte, self.unites, self._tour, self.generaux = Carte(largeur, hauteur), [], 0, {}
        self.player_id, self.next_player_id, self.unit_counter = 0, 0, 0
        self.ipc = IPCClient(port_python=port_python)

    @property
    def tick(self): return self._tour
    def get_ipc(self): return self.ipc

    def ajouter_joueur(self, ia_name, units_config):
        pid = self.next_player_id
        self.next_player_id += 1
        self.generaux[pid] = make_general(ia_name, id_player=pid)
        if pid == self.player_id: # On ne cree les unites que pour NOUS
            for utype, count in units_config.items():
                for _ in range(count):
                    self.ajouter_unite(utype, random.randint(0, self.carte.largeur-1), random.randint(0, self.carte.hauteur-1), pid)
        return pid

    def ajouter_unite(self, nom, x, y, equipe, force_id=None):
        u = Unit(nomUnite=nom)
        u.equipe, u.coords = equipe, (float(x), float(y))
        # FIX 4: IDs uniques (prefixés par player_id)
        if force_id is not None: u.id = force_id
        else:
            u.id = (equipe * 1000) + self.unit_counter
            self.unit_counter += 1
        self.unites.append(u)

    def get_unit_by_id(self, uid):
        for u in self.unites:
            if getattr(u, 'id', -1) == uid: return u
        return None

    def envoyer_join(self):
        uds = [{"entity_id": u.id, "unit_type": getattr(u, 'Unit', 'Knight'), "x": u.coords[0], "y": u.coords[1]} for u in self.unites if u.equipe == self.player_id]
        self.ipc.envoyer({"type": "JOIN", "player_id": self.player_id, "ia": self.generaux[self.player_id].name, "units": uds})

    def _executer_attack(self, u, target):
        if not u.can_attack(): return
        u.target = target
        u.inflict_damage()
        # FIX 5: Sync HP et Mort
        self.ipc.envoyer({"type":"UPDATE","action":"attack","player_id":self.player_id,"target_id":target.id,"target_hp":target.HP})
        if target.HP <= 0:
            target.alive = False
            self.ipc.envoyer({"type":"UPDATE","action":"die","player_id":self.player_id,"entity_id":target.id})

    def mettre_a_jour(self):
        self._tour += 1
        for u in self.unites: 
            if hasattr(u, 'timer'): u.timer += 1 # FIX 1: Increment timer
        
        if self.player_id in self.generaux:
            mine = [u for u in self.unites if u.alive and u.equipe == self.player_id]
            acts = self.generaux[self.player_id].decider_actions(mine, self)
            for a in acts:
                u = self.get_unit_by_id(a.unit_id)
                if not u or not u.alive: continue
                if a.type in [TypeAction.MOVE, TypeAction.FORM_UP]:
                    dist = math.sqrt((a.target_pos[0]-u.coords[0])**2 + (a.target_pos[1]-u.coords[1])**2)
                    if dist > 0.1:
                        v = getattr(u, 'Speed', 1.0)
                        if dist <= v: u.coords = a.target_pos
                        else: u.coords = (u.coords[0]+(a.target_pos[0]-u.coords[0])*v/dist, u.coords[1]+(a.target_pos[1]-u.coords[1])*v/dist)
                        self.ipc.envoyer({"type":"UPDATE","action":"move","entity_id":u.id,"x":u.coords[0],"y":u.coords[1],"player_id":u.equipe})
                elif a.type == TypeAction.ATTACK: # FIX 1: Gérer les attaques
                    target = self.get_unit_by_id(a.target_id)
                    if target and target.alive: self._executer_attack(u, target)

    def appliquer_message(self, m):
        t, pid = m.get("type", "").lower(), int(m.get("player_id", -1))
        if pid == self.player_id: return
        if t == "join":
            if pid not in self.generaux: # FIX 3: Repondre au JOIN sans boucle infinie
                self.generaux[pid] = make_general(m.get("ia", "braindead"), id_player=pid)
                for u in m.get("units", []): 
                    self.ajouter_unite(u.get("unit_type"), u.get("x"), u.get("y"), pid, force_id=u.get("entity_id"))
                self.envoyer_join()
        elif t == "update":
            act = m.get("action", "").lower()
            if act == "move":
                u = self.get_unit_by_id(m.get("entity_id"))
                if u: u.coords = (m.get("x"), m.get("y"))
            elif act == "attack": # FIX 5: Sync HP
                target = self.get_unit_by_id(m.get("target_id"))
                if target: target.HP = m.get("target_hp", target.HP)
            elif act == "die": # FIX 5: Sync Mort
                u = self.get_unit_by_id(m.get("entity_id"))
                if u: u.alive, u.HP = False, 0

    def enemy_in_los(self, u): return [e for e in self.unites if e.alive and e.equipe != u.equipe]
    def nearest_enemy(self, u):
        ens = self.enemy_in_los(u)
        return min(ens, key=lambda e: abs(u.coords[0]-e.coords[0])+abs(u.coords[1]-e.coords[1])) if ens else None
