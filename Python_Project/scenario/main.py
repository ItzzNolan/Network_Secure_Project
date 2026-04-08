# main.py
# Version avec ManagerVue et support des generaux IA
import os
import sys
parent_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
sys.path.append(parent_dir)
import random
import pygame
from backend.jeu import Jeu
from backend.save_manager import SaveManager
from frontend.manager_vue import ManagerVue

# --- GENERAUX DISPONIBLES ---
# "braindead" : CaptainBraindead (basique, chasse et attaque)
# "daft"      : MajorDAFT (plus intelligent, focus prioritaire)

GENERAL_BLEU = "daft"       # Modifier ici
GENERAL_ROUGE = "braindead"  # Modifier ici


def initialiser_partie(general_bleu="braindead", general_rouge="braindead"):
    """Cree une nouvelle partie avec les generaux specifies"""
    partie = Jeu(general_bleu=general_bleu, general_rouge=general_rouge)
    
    # jeu = Jeu(50,50)
    # carte = Carte(50, 50)
    # jeu.carte = carte  # si la classe Jeu possède un attribut "carte"

    # 2. Créer les généraux
    #general_joueur1 = MajorDAFT(0)
    #general_joueur2 = MajorDAFT(1)





#placer les unité de façon random
#taille map / 2 (longueur)

#dimension map
    H = 50
    L= 50
    L1= L//2 - 3
    L2 = L//2 + 3
#definir les unités de façon random
    N = (H * L1)//10 
    a1 = random.randint(0, N)
    b1 = random.randint(0, N-a1)

    c1 = N - a1 - b1

    a2 =a1
    b2 =b1
    c2 = c1

# 3. Ajouter les unités sur la carte
    #  (joueur 1)
    for x in range(L1):
        for y in range(H):  
            if c1 > 0:
                partie.ajouter_unite("Crossbowman",x,y,0)
                c1 -= 1

            if b1 > 0:
                partie.ajouter_unite("Knight",x,y,0)
                b1 -= 1

            if a1 > 0:
                partie.ajouter_unite("Pikeman",x,y,0)
                a1 -= 1
              
    # (joueur 2)
    for x in range(L2, L):
        for y in range(H):
            if a2 > 0:
                partie.ajouter_unite("Pikeman",x,y,1)
                a2 -= 1

            if b2 > 0:
                partie.ajouter_unite("Knight",x,y,1)
                b2 -= 1

            if c2 > 0:
                partie.ajouter_unite("Crossbowman",x,y,1)
                c2 -= 1
    return partie


if __name__ == "__main__":
    # --- INITIALISATION ---
    mon_jeu = initialiser_partie(GENERAL_BLEU, GENERAL_ROUGE)
    manager_vue = ManagerVue(mon_jeu)
    save_manager = SaveManager()
    
    clock = pygame.time.Clock()
    running = True
    paused = True
    game_tick = 0
    
    partie_terminee = False
    gagnant = None

    print("\n" + "="*60)
    print("  MedievAIl BAIttle GenerAIl")
    print("="*60)
    print(f"  General Bleu:  {mon_jeu.generaux[0].name}")
    print(f"  General Rouge: {mon_jeu.generaux[1].name}")
    print("-"*60)
    print("  CONTROLES:")
    print("  P             = Pause/Play")
    print("  F9            = Changer vue (Pygame/Terminal)")
    print("  F10           = Plein ecran")
    print("  F11           = Quicksave")
    print("  F12           = Quickload")
    print("  TAB           = Ouvrir stats HTML")
    print("  ZQSD/Fleches  = Deplacer camera")
    print("  Shift         = Deplacement rapide")
    print("  R             = Recommencer")
    print("  ESC           = Quitter")
    print("="*60 + "\n")

    # --- BOUCLE PRINCIPALE ---
    while running:
        # 1. Gerer les evenements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    
                if event.key == pygame.K_p:
                    if not partie_terminee:
                        paused = not paused
                        manager_vue.vue_pygame.paused = paused
                        print("PAUSE" if paused else "EN JEU")
                
                # F9 = Changer de vue
                if event.key == pygame.K_F9:
                    manager_vue.changer_mode()
                
                # F10 = Plein ecran
                if event.key == pygame.K_F10:
                    manager_vue.vue_pygame.fullscreen = not manager_vue.vue_pygame.fullscreen
                    if manager_vue.vue_pygame.fullscreen:
                        manager_vue.vue_pygame.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        manager_vue.vue_pygame.screen = pygame.display.set_mode(
                            (manager_vue.vue_pygame.SCREEN_WIDTH, manager_vue.vue_pygame.SCREEN_HEIGHT))
                
                # F11 = Quicksave
                if event.key == pygame.K_F11:
                    save_manager.sauvegarder(mon_jeu)
                
                # F12 = Quickload
                if event.key == pygame.K_F12:
                    if save_manager.charger(mon_jeu):
                        partie_terminee = False
                        gagnant = None
                
                # TAB = Stats HTML
                if event.key == pygame.K_TAB:
                    paused = True
                    manager_vue.vue_pygame.paused = True
                    save_manager.ouvrir_stats_html(mon_jeu)
                    print("Stats HTML ouvertes")
                
                # R = Restart
                if event.key == pygame.K_r:
                    mon_jeu = initialiser_partie(GENERAL_BLEU, GENERAL_ROUGE)
                    manager_vue.jeu = mon_jeu
                    partie_terminee = False
                    gagnant = None
                    paused = True
                    manager_vue.vue_pygame.paused = True
                    print("Nouvelle partie!")
        
        # 2. Gerer la camera (ZQSD + fleches + Shift)
        keys = pygame.key.get_pressed()
        manager_vue.vue_pygame.gerer_camera(keys)
        
        # 3. Mettre a jour la logique du jeu
        if not paused and not partie_terminee:
            game_tick += 1
            if game_tick >= 10:
                game_tick = 0
                mon_jeu.mettre_a_jour()
                
                # Verifier victoire
                bleus = [u for u in mon_jeu.unites if u.alive and u.equipe == 0]
                rouges = [u for u in mon_jeu.unites if u.alive and u.equipe == 1]
                
                if len(bleus) == 0 and len(rouges) > 0:
                    partie_terminee = True
                    gagnant = "ROUGE"
                    print(f"VICTOIRE {mon_jeu.generaux[1].name}!")
                elif len(rouges) == 0 and len(bleus) > 0:
                    partie_terminee = True
                    gagnant = "BLEU"
                    print(f"VICTOIRE {mon_jeu.generaux[0].name}!")
                elif len(bleus) == 0 and len(rouges) == 0:
                    partie_terminee = True
                    gagnant = "EGALITE"
                    print("EGALITE!")
        
        # 4. Afficher (le manager s'occupe de tout)
        manager_vue.afficher()
        
        # 5. Rafraichir l'ecran
        pygame.display.flip()
        
        # 6. Controler la vitesse (30 FPS)
        clock.tick(30)

    pygame.quit()