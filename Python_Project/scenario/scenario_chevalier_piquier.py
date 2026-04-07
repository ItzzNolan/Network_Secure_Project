import os
import sys
import random
import pygame
parent_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
sys.path.append(parent_dir)
from backend.carte import Carte
from backend.Units import Unit  
from backend.jeu import Jeu
from ia.general import *
from frontend.vue_terminal import afficher
from backend.save_manager import SaveManager



def scenario_piquiers_vs_chevaliers():  

    # 1. Créer le jeu et la carte
    jeu = Jeu(50,50)
    carte = Carte(50, 50)
    jeu.carte = carte  # si la classe Jeu possède un attribut "carte"

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
                jeu.ajouter_unite("Crossbowman",x,y,0)
                c1 -= 1

            if b1 > 0:
                jeu.ajouter_unite("Knight",x,y,0)
                b1 -= 1

            if a1 > 0:
                jeu.ajouter_unite("Pikeman",x,y,0)
                a1 -= 1
              
    # (joueur 2)
    for x in range(L2, L):
        for y in range(H):
            if a2 > 0:
                jeu.ajouter_unite("Pikeman",x,y,1)
                a2 -= 1

            if b2 > 0:
                jeu.ajouter_unite("Knight",x,y,1)
                b2 -= 1

            if c2 > 0:
                jeu.ajouter_unite("Crossbowman",x,y,1)
                c2 -= 1           

    # 4. Ajouter les joueurs au jeu
    #jeu.ajouter_joueur(general_joueur1)
    #jeu.ajouter_joueur(general_joueur2)

    # (optionnel) Afficher la carte
#    afficher(jeu)
    gv = TestGameView(tick=0, units=jeu.unites)
    # jeu.death0[0]=len([u for u in gv.units if u.alive and u.equipe==0])
    # jeu.death1[0]=len([u for u in gv.units if u.alive and u.equipe==1])
    #MajorDAFT pour l'equipe 1 avec un point de regroupement proche
    g1 = MajorDAFT(id_player=0, regroup_at=(4,4))

    #CaptainBraindead pour l'equipe 2 pour voir la difference
    g2 = CaptainBraindead(id_player=1)

    generals = {0:g1, 1:g2}

    mv=ManagerVue(jeu)
    save_manager = SaveManager()



    clock = pygame.time.Clock()
    TICKS = 0
    running=True
    paused=False

#     for _ in range(TICKS):
#         print_state(gv)
#         tick_simulation(gv, generals)
    #    jeu.death0.append(len([u for u in gv.units if u.alive and u.equipe==0]))
    #    jeu.death1.append(len([u for u in gv.units if u.alive and u.equipe==1]))
#         if check_victory(gv)!=None:
#             break
    
    while running:
        # 1. Gerer les evenements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    
                if event.key == pygame.K_p:
                    if check_victory(gv)==None:
                        paused = not paused
                        mv.vue_pygame.paused = paused
                        print("PAUSE" if paused else "EN JEU")
                
                # F9 = Changer de vue
                if event.key == pygame.K_F9:
                    mv.changer_mode()
                
                # F10 = Plein ecran
                if event.key == pygame.K_F10:
                    mv.vue_pygame.fullscreen = not mv.vue_pygame.fullscreen
                    if mv.vue_pygame.fullscreen:
                        mv.vue_pygame.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        mv.vue_pygame.screen = pygame.display.set_mode(
                            (mv.vue_pygame.SCREEN_WIDTH, mv.vue_pygame.SCREEN_HEIGHT))
            
                # F11 = Quicksave
                if event.key == pygame.K_F11:
                    save_manager.sauvegarder(jeu)
                
                # F12 = Quickload
                if event.key == pygame.K_F12:
                    if save_manager.charger(jeu):
                        partie_terminee = False
                        gagnant = None

                # TAB = Stats HTML
                if event.key == pygame.K_TAB:
                    paused = True
                    mv.vue_pygame.paused = True
                    # jeu.ouvrir_stats_html()
                    # print("Stats HTML ouvertes")
                
                # # R = Restart
                # if event.key == pygame.K_r:
                #     mon_jeu = initialiser_partie()
                #     mv.jeu = mon_jeu
                #     partie_terminee = False
                #     gagnant = None
                #     paused = True
                #     mv.vue_pygame.paused = True
                #     print("Nouvelle partie!")
        
        # 2. Gerer la camera (ZQSD + fleches + Shift)
        keys = pygame.key.get_pressed()
        mv.vue_pygame.gerer_camera(keys)
        
        # 3. Mettre a jour la logique du jeu
        if not paused and check_victory(gv)==None:
            TICKS += 1
            if TICKS >= 10:
                # TICKS = 0
                tick_simulation(gv, generals)
                jeu.mettre_a_jour()
                
        mv.afficher()
        pygame.display.update()
        clock.tick(30)

    #jeu.graphic(_)
    return jeu

if __name__ == "__main__":
    jeu = scenario_piquiers_vs_chevaliers()
    #jeu.lancer()  # ou toute autre méthode pour démarrer le jeu



