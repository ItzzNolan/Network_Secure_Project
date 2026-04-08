import pygame
import random
import os
from frontend.iso import grid_to_iso
from assets.loader import load_sprite


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
            self.gold_sprite = pygame.transform.smoothscale(self.gold_sprite, 
                (int(self.gold_sprite.get_width() * 0.7), int(self.gold_sprite.get_height() * 0.7)))
            crossbow_sprite = load_sprite(os.path.join(base_dir, "assets/Crossbowman.png"), upscale_factor=1).convert_alpha()
            knight_sprite = load_sprite(os.path.join(base_dir, "assets/Knight.png"), upscale_factor=1).convert_alpha()
            pikeman_sprite = load_sprite(os.path.join(base_dir, "assets/Pikeman.png"), upscale_factor=1).convert_alpha()
            self.unit_sprites = {
                "Crossbowman": pygame.transform.smoothscale(crossbow_sprite, 
                    (int(crossbow_sprite.get_width() * 1.3), int(crossbow_sprite.get_height() * 1.3))),
                "Knight": pygame.transform.smoothscale(knight_sprite, 
                    (int(knight_sprite.get_width() * 1.3), int(knight_sprite.get_height() * 1.3))),
                "Pikeman": pygame.transform.smoothscale(pikeman_sprite, 
                    (int(pikeman_sprite.get_width() * 1.3), int(pikeman_sprite.get_height() * 1.3)))
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

    def afficher(self, jeu, partie_terminee=False, gagnant=None):
        current_w, current_h = self.screen.get_size()
        self.screen.fill((121, 127, 58))
        self.screen.blit(self.map_surface, (self.camera_x, self.camera_y))
        self._dessiner_unites(jeu)
        self._dessiner_minimap(jeu, current_w, current_h)
        self._dessiner_equipes(jeu, current_w, current_h)
        self._dessiner_hud(jeu, current_w)
        if partie_terminee:
            self._dessiner_victoire(jeu, current_w, current_h, gagnant)

    def _dessiner_unites(self, jeu):
        for u in jeu.unites:
            if not u.alive or not u.coords:
                continue
            
            ux, uy = u.coords
            iso_x, iso_y = grid_to_iso(ux, uy, self.TILE_W, self.TILE_H)
            dx = self.camera_x + self.origin_x + iso_x
            dy = self.camera_y + self.origin_y + iso_y + self.TILE_H // 2
            
            color = (70, 130, 255) if u.equipe == 0 else (255, 70, 70)
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
                color = (70, 130, 255) if u.equipe == 0 else (255, 70, 70)
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
        
        bleus = [u for u in jeu.unites if u.alive and u.equipe == 0]
        rouges = [u for u in jeu.unites if u.alive and u.equipe == 1]
        
        nom_bleu = jeu.generaux[0].name if hasattr(jeu, 'generaux') and 0 in jeu.generaux else "JOUEUR 1"
        nom_rouge = jeu.generaux[1].name if hasattr(jeu, 'generaux') and 1 in jeu.generaux else "JOUEUR 2"
        
        pygame.draw.rect(self.screen, (20, 30, 50), (margin, top_y, box_w, box_h))
        pygame.draw.rect(self.screen, (70, 130, 255), (margin, top_y, box_w, box_h), 3)
        pygame.draw.rect(self.screen, (70, 130, 255), (margin, top_y, box_w, 20))
        
        title_bleu = self.font_mono.render("EQUIPE 1 - BLEU", True, (255, 255, 255))
        self.screen.blit(title_bleu, (margin + 8, top_y + 2))
        
        nom_surface = self.font_mono.render(nom_bleu, True, (100, 180, 255))
        self.screen.blit(nom_surface, (margin + 8, top_y + 25))
        
        units_surface = self.font_mono.render(f"Unites: {len(bleus)}", True, (150, 150, 150))
        self.screen.blit(units_surface, (margin + 8, top_y + 45))
        
        box_x_rouge = current_w - box_w - margin
        
        pygame.draw.rect(self.screen, (50, 20, 20), (box_x_rouge, top_y, box_w, box_h))
        pygame.draw.rect(self.screen, (255, 70, 70), (box_x_rouge, top_y, box_w, box_h), 3)
        pygame.draw.rect(self.screen, (255, 70, 70), (box_x_rouge, top_y, box_w, 20))
        
        title_rouge = self.font_mono.render("EQUIPE 2 - ROUGE", True, (255, 255, 255))
        self.screen.blit(title_rouge, (box_x_rouge + 8, top_y + 2))
        
        nom_surface = self.font_mono.render(nom_rouge, True, (255, 150, 150))
        self.screen.blit(nom_surface, (box_x_rouge + 8, top_y + 25))
        
        units_surface = self.font_mono.render(f"Unites: {len(rouges)}", True, (150, 150, 150))
        self.screen.blit(units_surface, (box_x_rouge + 8, top_y + 45))

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
            nom_bleu = jeu.generaux[0].name if 0 in jeu.generaux else "?"
            nom_rouge = jeu.generaux[1].name if 1 in jeu.generaux else "?"
            self.screen.blit(self.font_mono.render(f"BLEU: {nom_bleu}", True, (100, 150, 255)), (350, 16))
            self.screen.blit(self.font_mono.render(f"ROUGE: {nom_rouge}", True, (255, 120, 120)), (550, 16))
        
        shortcuts = self.font_mono.render("F9:Vue | F10:Fullscreen | F11:Save | F12:Load", True, (100, 100, 100))
        self.screen.blit(shortcuts, (current_w - shortcuts.get_width() - 15, 16))

    def _dessiner_victoire(self, jeu, current_w, current_h, gagnant):
        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        if gagnant == "BLEU":
            nom_general = jeu.generaux[0].name if hasattr(jeu, 'generaux') and 0 in jeu.generaux else "BLEU"
            color = (70, 130, 255)
            text = f"VICTOIRE {nom_general}!"
        elif gagnant == "ROUGE":
            nom_general = jeu.generaux[1].name if hasattr(jeu, 'generaux') and 1 in jeu.generaux else "ROUGE"
            color = (255, 70, 70)
            text = f"VICTOIRE {nom_general}!"
        else:
            color = (200, 200, 200)
            text = "EGALITE!"
 
        font_victory = pygame.font.SysFont("Segoe UI", 40, bold=True)
        font_sub = pygame.font.SysFont("Segoe UI", 18)
        
        box_w, box_h = 500, 150
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
        cam_x_min = -self.surface_w + current_w
        cam_x_max = 0
        cam_y_min = -self.surface_h + current_h
        cam_y_max = 0
        
        self.camera_x = max(cam_x_min, min(cam_x_max, self.camera_x))
        self.camera_y = max(cam_y_min, min(cam_y_max, self.camera_y))
    
    
