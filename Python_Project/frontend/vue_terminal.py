import pygame


class VueTerminal:
    def __init__(self):
        self.font_title = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_subtitle = pygame.font.SysFont("Segoe UI", 18)
        self.font_mono = pygame.font.SysFont("Consolas", 15)
        self.font_grid = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_hud = pygame.font.SysFont("Segoe UI", 18, bold=True)
        
        self.camera_x = 0
        self.camera_y = 0
        self.auto_follow = True  
        self.CELL_SIZE = 18
    
    def afficher(self, screen, jeu, partie_terminee=False, gagnant=None):
        current_w, current_h = screen.get_size()
        MAP_W = jeu.carte.largeur
        MAP_H = jeu.carte.hauteur
        
        screen.fill((10, 15, 20))

        pygame.draw.rect(screen, (15, 20, 28), (0, 0, current_w, 50))
        pygame.draw.line(screen, (50, 55, 65), (0, 49), (current_w, 49), 2)
        
        mode_txt = "AUTO" if self.auto_follow else "MANUEL"
        screen.blit(self.font_hud.render(f"|| Terminal [{mode_txt}]", True, (150, 200, 150)), (20, 14))
        screen.blit(self.font_hud.render(f"|  Tour: {jeu._tour}  |  Unites: {len([u for u in jeu.unites if u.alive])}  |  Map: {MAP_W}x{MAP_H}", 
                                         True, (150, 150, 150)), (220, 14))
        
        shortcuts = self.font_mono.render("ZQSD:Scroll | SPACE:Auto | F9:Vue", True, (100, 100, 100))
        screen.blit(shortcuts, (current_w - shortcuts.get_width() - 15, 16))

        bleus = [u for u in jeu.unites if u.alive and u.equipe == 0]
        rouges = [u for u in jeu.unites if u.alive and u.equipe == 1]
        nom_bleu = jeu.generaux[0].name if hasattr(jeu, 'generaux') and 0 in jeu.generaux else "JOUEUR 1"
        nom_rouge = jeu.generaux[1].name if hasattr(jeu, 'generaux') and 1 in jeu.generaux else "JOUEUR 2"
        
        box_w = 180
        box_h = 60
        margin = 15
        top_y = 60
        
        pygame.draw.rect(screen, (20, 30, 50), (margin, top_y, box_w, box_h))
        pygame.draw.rect(screen, (70, 130, 255), (margin, top_y, box_w, box_h), 2)
        pygame.draw.rect(screen, (70, 130, 255), (margin, top_y, box_w, 18))
        screen.blit(self.font_grid.render("EQUIPE 1 - BLEU", True, (255, 255, 255)), (margin + 8, top_y + 2))
        screen.blit(self.font_mono.render(nom_bleu, True, (100, 180, 255)), (margin + 8, top_y + 22))
        screen.blit(self.font_mono.render(f"Unites: {len(bleus)}", True, (150, 150, 150)), (margin + 8, top_y + 40))

        box_x_rouge = current_w - box_w - margin
        pygame.draw.rect(screen, (50, 20, 20), (box_x_rouge, top_y, box_w, box_h))
        pygame.draw.rect(screen, (255, 70, 70), (box_x_rouge, top_y, box_w, box_h), 2)
        pygame.draw.rect(screen, (255, 70, 70), (box_x_rouge, top_y, box_w, 18))
        screen.blit(self.font_grid.render("EQUIPE 2 - ROUGE", True, (255, 255, 255)), (box_x_rouge + 8, top_y + 2))
        screen.blit(self.font_mono.render(nom_rouge, True, (255, 150, 150)), (box_x_rouge + 8, top_y + 22))
        screen.blit(self.font_mono.render(f"Unites: {len(rouges)}", True, (150, 150, 150)), (box_x_rouge + 8, top_y + 40))

        grid_start_y = 135
        available_h = current_h - grid_start_y - 20
        available_w = current_w - 40
        
        visible_cols = available_w // self.CELL_SIZE
        visible_rows = available_h // self.CELL_SIZE

        if self.auto_follow:
            alive_units = [u for u in jeu.unites if u.alive and u.coords]
            if alive_units:
                center_x = sum(u.coords[0] for u in alive_units) / len(alive_units)
                center_y = sum(u.coords[1] for u in alive_units) / len(alive_units)
                self.camera_x = int(center_x - visible_cols // 2)
                self.camera_y = int(center_y - visible_rows // 2)
        

        self.camera_x = max(0, min(MAP_W - visible_cols, self.camera_x))
        self.camera_y = max(0, min(MAP_H - visible_rows, self.camera_y))

        grid_w = visible_cols * self.CELL_SIZE
        grid_h = visible_rows * self.CELL_SIZE
        grid_x = (current_w - grid_w) // 2
        grid_y = grid_start_y
        pygame.draw.rect(screen, (15, 20, 25), (grid_x - 3, grid_y - 3, grid_w + 6, grid_h + 6))
        pygame.draw.rect(screen, (40, 50, 60), (grid_x - 3, grid_y - 3, grid_w + 6, grid_h + 6), 1)
        for row in range(visible_rows):
            for col in range(visible_cols):
                gx = col + self.camera_x
                gy = row + self.camera_y
                if 0 <= gx < MAP_W and 0 <= gy < MAP_H:
                    if (gx + gy) % 2 == 0:
                        color = (25, 35, 30)
                    else:
                        color = (30, 40, 35)
                    pygame.draw.rect(screen, color, 
                                    (grid_x + col * self.CELL_SIZE, 
                                     grid_y + row * self.CELL_SIZE, 
                                     self.CELL_SIZE - 1, self.CELL_SIZE - 1))
        

        for u in jeu.unites:
            if not u.alive or not u.coords:
                continue
            
            col = int(u.coords[0]) - self.camera_x
            row = int(u.coords[1]) - self.camera_y
            
            if 0 <= col < visible_cols and 0 <= row < visible_rows:
                rx = grid_x + col * self.CELL_SIZE
                ry = grid_y + row * self.CELL_SIZE
                

                if u.equipe == 0:
                    bg = (40, 70, 130)
                    fg = (180, 220, 255)
                    border = (70, 130, 255)
                else:
                    bg = (130, 40, 40)
                    fg = (255, 180, 180)
                    border = (255, 70, 70)
                

                pygame.draw.rect(screen, bg, (rx, ry, self.CELL_SIZE - 1, self.CELL_SIZE - 1))
                pygame.draw.rect(screen, border, (rx, ry, self.CELL_SIZE - 1, self.CELL_SIZE - 1), 1)
                

                letter = self.font_grid.render(u.Unit[0].upper(), True, fg)
                screen.blit(letter, (rx + self.CELL_SIZE // 2 - letter.get_width() // 2, 
                                     ry + self.CELL_SIZE // 2 - letter.get_height() // 2))
        

        pos_txt = f"Vue: ({self.camera_x},{self.camera_y}) - ({self.camera_x + visible_cols},{self.camera_y + visible_rows})"
        pos_render = self.font_mono.render(pos_txt, True, (80, 80, 80))
        screen.blit(pos_render, (grid_x, current_h - 18))

        if MAP_W > 50 or MAP_H > 50:
            self._dessiner_minimap(screen, jeu, current_w, current_h, visible_cols, visible_rows)
        if partie_terminee:
            self._dessiner_victoire(screen, jeu, current_w, current_h, gagnant)
    
    def _dessiner_minimap(self, screen, jeu, current_w, current_h, visible_cols, visible_rows):
        MAP_W = jeu.carte.largeur
        MAP_H = jeu.carte.hauteur
        
        mm_size = 100
        mm_x = current_w - mm_size - 15
        mm_y = current_h - mm_size - 25
        

        pygame.draw.rect(screen, (20, 25, 30), (mm_x - 2, mm_y - 2, mm_size + 4, mm_size + 4))
        pygame.draw.rect(screen, (50, 60, 70), (mm_x - 2, mm_y - 2, mm_size + 4, mm_size + 4), 1)
        pygame.draw.rect(screen, (30, 40, 35), (mm_x, mm_y, mm_size, mm_size))
        
        scale_x = mm_size / MAP_W
        scale_y = mm_size / MAP_H

        for u in jeu.unites:
            if not u.alive or not u.coords:
                continue
            px = mm_x + int(u.coords[0] * scale_x)
            py = mm_y + int(u.coords[1] * scale_y)
            color = (70, 130, 255) if u.equipe == 0 else (255, 70, 70)
            pygame.draw.circle(screen, color, (px, py), 2)
        

        vx = mm_x + int(self.camera_x * scale_x)
        vy = mm_y + int(self.camera_y * scale_y)
        vw = int(visible_cols * scale_x)
        vh = int(visible_rows * scale_y)
        pygame.draw.rect(screen, (255, 255, 255), (vx, vy, vw, vh), 1)
        

        label = self.font_mono.render("MINIMAP", True, (80, 80, 80))
        screen.blit(label, (mm_x, mm_y - 15))
    
    def gerer_touches(self, keys, shift=False):

        speed = 5 if shift else 2
        moved = False
        
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            self.camera_y -= speed
            moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera_y += speed
            moved = True
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.camera_x -= speed
            moved = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera_x += speed
            moved = True
        
        if moved:
            self.auto_follow = False
    
    def toggle_auto_follow(self):
        self.auto_follow = not self.auto_follow
        return self.auto_follow
    
    def _dessiner_victoire(self, screen, jeu, current_w, current_h, gagnant):
        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if gagnant == "BLEU":
            nom = jeu.generaux[0].name if hasattr(jeu, 'generaux') and 0 in jeu.generaux else "BLEU"
            color = (70, 130, 255)
            text = f"VICTOIRE {nom}!"
        elif gagnant == "ROUGE":
            nom = jeu.generaux[1].name if hasattr(jeu, 'generaux') and 1 in jeu.generaux else "ROUGE"
            color = (255, 70, 70)
            text = f"VICTOIRE {nom}!"
        else:
            color = (200, 200, 200)
            text = "EGALITE!"
        
        font_victory = pygame.font.SysFont("Segoe UI", 40, bold=True)
        font_sub = pygame.font.SysFont("Segoe UI", 18)
        
        box_w, box_h = 500, 150
        box_x = (current_w - box_w) // 2
        box_y = (current_h - box_h) // 2
        
        pygame.draw.rect(screen, (20, 20, 30), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, color, (box_x, box_y, box_w, box_h), 3)
        
        txt = font_victory.render(text, True, color)
        screen.blit(txt, (current_w // 2 - txt.get_width() // 2, box_y + 35))
        
        txt2 = font_sub.render("R = Recommencer   ESC = Quitter", True, (150, 150, 150))
        screen.blit(txt2, (current_w // 2 - txt2.get_width() // 2, box_y + 100))


def afficher(jeu):
    print("\n" + "="*50)
    print(f"  Tour: {jeu._tour}")
    print("="*50)
    
    bleus = [u for u in jeu.unites if u.alive and u.equipe == 0]
    rouges = [u for u in jeu.unites if u.alive and u.equipe == 1]
    
    print(f"  Bleus: {len(bleus)}  |  Rouges: {len(rouges)}")
    print("-"*50)
    
    for u in jeu.unites:
        if not u.alive:
            continue
        equipe = "BLEU" if u.equipe == 0 else "ROUGE"
        print(f"  [{equipe}] {u.Unit} HP:{u.HP:.0f} @ ({u.coords[0]:.1f}, {u.coords[1]:.1f})")
    
    print("="*50 + "\n")
