import pygame
import random
import os
from frontend.iso import grid_to_iso
from assets.loader import load_sprite
from backend.jeu import get_team_color, get_team_name, TEAM_COLORS
import math


class VuePygame:
    def __init__(self, largeur_carte, hauteur_carte):
        pygame.init()
        self.SCREEN_WIDTH = 1100
        self.SCREEN_HEIGHT = 750
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("MedievAIl BAIttle GenerAIl")


        self.largeur_carte = largeur_carte
        self.hauteur_carte = hauteur_carte


        self.TILE_GRASS = 0
        self.TILE_TREE = 1
        self.TILE_GOLD = 2


        self.camera_x = 0
        self.camera_y = 0
        self.speed = 20
        self.speed_fast = 50


        self.paused = False
        self.fullscreen = False
        self._charger_sprites()
        self._generer_carte()
        self._pre_rendre_carte()
        self._creer_minimap()
        self.font_hud = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.font_mono = pygame.font.SysFont("Consolas", 15)

    def _charger_sprites(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        try:
            self.grass_sprite = load_sprite(os.path.join(base_dir, "assets/tile_grass.png"), upscale_factor=1).convert_alpha()
            self.tree_sprite = load_sprite(os.path.join(base_dir, "assets/tile_tree.png"), upscale_factor=1).convert_alpha()
            self.gold_sprite = load_sprite(os.path.join(base_dir, "assets/tile_gold.png"), upscale_factor=1).convert_alpha()
            self.tree_sprite = pygame.transform.smoothscale(self.tree_sprite,(int(self.tree_sprite.get_width() * 0.5), int(self.tree_sprite.get_height() * 0.5)))
            self.gold_sprite = pygame.transform.smoothscale(self.gold_sprite,(int(self.gold_sprite.get_width() * 0.7), int(self.gold_sprite.get_height() * 0.7)))
            crossbow_sprite = load_sprite(os.path.join(base_dir, "assets/Crossbowman.png"), upscale_factor=1).convert_alpha()
            knight_sprite = load_sprite(os.path.join(base_dir, "assets/Knight.png"), upscale_factor=1).convert_alpha()
            pikeman_sprite = load_sprite(os.path.join(base_dir, "assets/Pikeman.png"), upscale_factor=1).convert_alpha()
            self.unit_sprites = {
                "Crossbowman": pygame.transform.smoothscale(crossbow_sprite,(int(crossbow_sprite.get_width() * 1.3), int(crossbow_sprite.get_height() * 1.3))),
                "Knight": pygame.transform.smoothscale(knight_sprite,(int(knight_sprite.get_width() * 1.3), int(knight_sprite.get_height() * 1.3))),
                "Pikeman": pygame.transform.smoothscale(pikeman_sprite,(int(pikeman_sprite.get_width() * 1.3), int(pikeman_sprite.get_height() * 1.3)))
            }
            self.TILE_W = self.grass_sprite.get_width()
            self.TILE_H = self.grass_sprite.get_height()

        except Exception as e:
            print(f"ERREUR chargement sprites: {e}")
            self.TILE_W = 64
            self.TILE_H = 32
            self.grass_sprite = None
            self.tree_sprite = None
            self.gold_sprite = None
            self.unit_sprites = {}

    def _generer_carte(self):
        self.world_map = [[self.TILE_GRASS for _ in range(self.largeur_carte)] for _ in range(self.hauteur_carte)]

        for y in range(self.hauteur_carte):
            for x in range(self.largeur_carte):
                r = random.random()
                if r < 0.10:
                    self.world_map[y][x] = self.TILE_TREE
                elif r < 0.13:
                    self.world_map[y][x] = self.TILE_GOLD

    def _pre_rendre_carte(self):
        self.surface_w = self.largeur_carte * self.TILE_W + self.TILE_W
        self.surface_h = self.hauteur_carte * self.TILE_H + self.TILE_H

        self.map_surface = pygame.Surface((self.surface_w, self.surface_h), pygame.SRCALPHA).convert_alpha()

        self.origin_x = self.surface_w // 2
        self.origin_y = self.TILE_H // 2

        if self.grass_sprite is None:
            return
        
        for gy in range(self.hauteur_carte):
            for gx in range(self.largeur_carte):
                iso_x, iso_y = grid_to_iso(gx, gy, self.TILE_W, self.TILE_H)
                draw_x = self.origin_x + iso_x - self.TILE_W // 2
                draw_y = self.origin_y + iso_y
                self.map_surface.blit(self.grass_sprite, (draw_x, draw_y))


                tile = self.world_map[gy][gx]
                if tile == self.TILE_TREE and self.tree_sprite:
                    self.map_surface.blit(self.tree_sprite,
                        (draw_x + self.TILE_W // 2 - self.tree_sprite.get_width() // 2,
                         draw_y + self.TILE_H - self.tree_sprite.get_height()))
                elif tile == self.TILE_GOLD and self.gold_sprite:
                    self.map_surface.blit(self.gold_sprite,
                        (draw_x + self.TILE_W // 2 - self.gold_sprite.get_width() // 2,
                         draw_y + self.TILE_H - self.gold_sprite.get_height()))

        self.camera_x = -self.surface_w // 2 + self.SCREEN_WIDTH // 2
        self.camera_y = -self.surface_h // 4

    def _creer_minimap(self):
        self.MINIMAP_SIZE = 120
        self.minimap_scale = self.MINIMAP_SIZE / self.largeur_carte

        self.minimap_base = pygame.Surface((self.MINIMAP_SIZE, self.MINIMAP_SIZE))

        for y in range(self.hauteur_carte):
            for x in range(self.largeur_carte):
                tile = self.world_map[y][x]
                if tile == self.TILE_TREE:
                    color = (0, 80, 0)
                elif tile == self.TILE_GOLD:
                    color = (255, 200, 0)
                else:
                    color = (50, 120, 50)
                
                px = int(x * self.minimap_scale)
                py = int(y * self.minimap_scale)
                pygame.draw.rect(self.minimap_base, color,
                    (px, py, max(1, int(self.minimap_scale)), max(1, int(self.minimap_scale))))

    def afficher(self, jeu, partie_terminee=False, gagnant=None, gagnant_id=None):
        current_w, current_h = self.screen.get_size()
        self.screen.fill((121, 127, 58))
        self.screen.blit(self.map_surface, (self.camera_x, self.camera_y))
        self._dessiner_unites(jeu)
        self._dessiner_minimap(jeu, current_w, current_h)
        self._dessiner_equipes(jeu, current_w, current_h)
        self._dessiner_hud(jeu, current_w)
        if hasattr(jeu, "waiting_for_player") and jeu.waiting_for_player:
            self._dessiner_message_attente(jeu)
        if partie_terminee:
            self._dessiner_victoire(jeu, current_w, current_h, gagnant, gagnant_id)
    
    def _dessiner_message_attente(self, jeu):
        current_w, current_h = self.screen.get_size()
        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        time_ms = pygame.time.get_ticks()
        pulse = (math.sin(time_ms*0.005) + 1)/2

        if jeu.domination_team is not None:
            base_color = get_team_color(jeu.domination_team)
            color = (min(255, int(base_color[0] + pulse * 80)),min(255, int(base_color[1] + pulse * 80)),min(255, int(base_color[2] + pulse * 80)),)
            color_name = get_team_name(jeu.domination_team)
            name = jeu.domination_team
            text_main = f"DOMINATION TEAM {name} - {color_name}"
        else:
            color = (200, 200, 200)
            text_main = "DOMINATION"

        text_sub = "En attente d'un autre joueur..."
        font_main = pygame.font.SysFont("Segoe UI", 38, bold=True)
        font_sub  = pygame.font.SysFont("Segoe UI", 18)
        box_w, box_h = 600, 160
        box_x = (current_w - box_w) // 2
        box_y = (current_h - box_h) // 2

        pygame.draw.rect(self.screen, (20, 20, 30), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, color, (box_x, box_y, box_w, box_h), 3)

        scale = 1 + pulse * 0.05
        txt_main = font_main.render(text_main, True, color)
        txt_main = pygame.transform.smoothscale(txt_main,(int(txt_main.get_width() * scale), int(txt_main.get_height() * scale)))
        self.screen.blit(txt_main, (current_w // 2 - txt_main.get_width() // 2,box_y+30))
        txt_sub = font_sub.render(text_sub, True, (150, 150, 150))
        self.screen.blit(txt_sub, (current_w // 2 - txt_sub.get_width() // 2,box_y+95))

    def _dessiner_unites(self, jeu):
        for u in jeu.unites:
            if not u.alive or not u.coords:
                continue

            ux, uy = u.coords
            iso_x, iso_y = grid_to_iso(ux, uy, self.TILE_W, self.TILE_H)
            dx = self.camera_x + self.origin_x + iso_x
            dy = self.camera_y + self.origin_y + iso_y + self.TILE_H // 2

            color = get_team_color(u.equipe)
            pygame.draw.ellipse(self.screen, color, (dx - 18, dy - 8, 36, 16), 2)
            sprite = self.unit_sprites.get(u.Unit)
            if sprite:
                sx = dx - sprite.get_width() // 2
                sy = dy - sprite.get_height() + 8
                self.screen.blit(sprite, (sx, sy))
                hp_ratio = max(0, min(1, u.HP / 35))
                pygame.draw.rect(self.screen, (40, 40, 40), (dx - 18, sy - 8, 36, 5))
                hp_color = (50, 220, 50) if hp_ratio > 0.3 else (255, 100, 50)
                pygame.draw.rect(self.screen, hp_color, (dx - 18, sy - 8, int(36 * hp_ratio), 5))

    def _dessiner_minimap(self, jeu, current_w, current_h):
        minimap = self.minimap_base.copy()

        for u in jeu.unites:
            if u.alive and u.coords:
                color = get_team_color(u.equipe)
                px = int(u.coords[0] * self.minimap_scale)
                py = int(u.coords[1] * self.minimap_scale)
                pygame.draw.rect(minimap, color, (px - 2, py - 2, 5, 5))

        mm_x = current_w - self.MINIMAP_SIZE - 15
        mm_y = current_h - self.MINIMAP_SIZE - 15
        pygame.draw.rect(self.screen, (80, 80, 80), (mm_x - 2, mm_y - 2, self.MINIMAP_SIZE + 4, self.MINIMAP_SIZE + 4), 2)
        self.screen.blit(minimap, (mm_x, mm_y))

    def _dessiner_equipes(self, jeu, current_w, current_h):
        box_w = 160
        box_h = 70
        margin = 15
        top_y = 60
        gap = 8

        generaux = jeu.generaux if hasattr(jeu, 'generaux') else {}
        nb = len(generaux)
        if nb == 0:
            return

        pids = sorted(generaux.keys())
        left_pids  = pids[:nb // 2 + nb % 2]
        right_pids = pids[nb // 2 + nb % 2:]

        for i, pid in enumerate(left_pids):
            x = margin
            y = top_y + i * (box_h + gap)
            self._dessiner_boite_equipe(jeu, pid, x, y, box_w, box_h)

        for i, pid in enumerate(right_pids):
            x = current_w - box_w - margin
            y = top_y + i * (box_h + gap)
            self._dessiner_boite_equipe(jeu, pid, x, y, box_w, box_h)

    def _dessiner_boite_equipe(self, jeu, pid, x, y, box_w, box_h):
        alive_units = [u for u in jeu.unites if u.alive and u.equipe == pid]
        count = len(alive_units)
        is_alive = count > 0
        color = get_team_color(pid)
        name = get_team_name(pid)
        gen_name = jeu.generaux[pid].name if pid in jeu.generaux else "?"
        count = len([u for u in jeu.unites if u.alive and u.equipe == pid])

        if is_alive:
            bg_color = tuple(max(0, c // 5) for c in color)
            border_color = color
            text_color = color
            alpha = 255
        else:
            bg_color = (30, 30, 30)
            border_color = (80, 80, 80)
            text_color = (100, 100, 100)
            alpha = 120
        
        box_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surface.set_alpha(alpha)

        pygame.draw.rect(box_surface, bg_color, (0, 0, box_w, box_h))
        pygame.draw.rect(box_surface, color, (0, 0, box_w, box_h), 2)
        pygame.draw.rect(box_surface, color, (0, 0, box_w, 18))

        self.screen.blit(box_surface, (x, y))   

        title_surf = self.font_mono.render(f"EQ {pid} - {name}", True, (255, 255, 255))
        self.screen.blit(title_surf, (x + 5, y + 1))

        gen_surf = self.font_mono.render(gen_name, True, color)
        self.screen.blit(gen_surf, (x + 5, y + 22))

        units_surf = self.font_mono.render(f"Unites: {count}", True, (150, 150, 150))
        self.screen.blit(units_surf, (x + 5, y + 42))

    def _dessiner_hud(self, jeu, current_w):

        pygame.draw.rect(self.screen, (15, 20, 28), (0, 0, current_w, 50))
        pygame.draw.line(self.screen, (50, 55, 65), (0, 49), (current_w, 49), 2)

        status = "PAUSE" if self.paused else "EN JEU"
        status_color = (255, 200, 100) if self.paused else (100, 255, 150)

        nb_unites = len([u for u in jeu.unites if u.alive])

        self.screen.blit(self.font_hud.render(f"|| {status}", True, status_color), (20, 14))
        self.screen.blit(self.font_hud.render(f"| Tour: {jeu._tour}  |  Unites: {nb_unites}",
                                              True, (150, 150, 150)), (130, 14))
        if hasattr(jeu, 'generaux'):
            offset_x = 370
            for pid, gen in sorted(jeu.generaux.items()):
                color = get_team_color(pid)
                label = f"{get_team_name(pid)[:3]}: {gen.name}"
                surf = self.font_mono.render(label, True, color)
                self.screen.blit(surf, (offset_x, 16))
                offset_x += surf.get_width() + 20
                if offset_x > current_w - 350:
                    break

        shortcuts = self.font_mono.render("F9:Vue | F10:Full | F11:Save | F12:Load | A:+IA",
                                          True, (100, 100, 100))
        self.screen.blit(shortcuts, (current_w - shortcuts.get_width() - 15, 16))

    def _dessiner_victoire(self, jeu, current_w, current_h, gagnant, gagnant_id=None):
        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if gagnant_id is not None and gagnant_id >= 0:
            color = get_team_color(gagnant_id)
            gen_name = jeu.generaux[gagnant_id].name if gagnant_id in jeu.generaux else "?"
            text = f"VICTOIRE {get_team_name(gagnant_id)} — {gen_name}!"
        else:
            color = (200, 200, 200)
            text = "EGALITE!"

        font_victory = pygame.font.SysFont("Segoe UI", 38, bold=True)
        font_sub     = pygame.font.SysFont("Segoe UI", 18)

        box_w, box_h = 600, 150
        box_x = (current_w - box_w) // 2
        box_y = (current_h - box_h) // 2

        pygame.draw.rect(self.screen, (20, 20, 30), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, color, (box_x, box_y, box_w, box_h), 3)
        txt = font_victory.render(text, True, color)
        self.screen.blit(txt, (current_w // 2 - txt.get_width() // 2, box_y + 35))
        txt2 = font_sub.render("R = Recommencer   ESC = Quitter", True, (150, 150, 150))
        self.screen.blit(txt2, (current_w // 2 - txt2.get_width() // 2, box_y + 100))

    def gerer_camera(self, keys):
        current_w, current_h = self.screen.get_size()
        current_speed = self.speed_fast if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else self.speed

        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.camera_x += current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x -= current_speed
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.camera_y += current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y -= current_speed

        self.camera_x = max(-self.surface_w + current_w, min(0, self.camera_x))
        self.camera_y = max(-self.surface_h + current_h, min(0, self.camera_y))