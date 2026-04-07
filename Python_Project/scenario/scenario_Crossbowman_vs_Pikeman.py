from backend.carte import Carte
from backend.Units import Unit  
from backend.jeu import Jeu
from ia.general import MajorDAFT
from frontend.vue_terminal import afficher

def scenario_Crossbowman_vs_Pikeman():  

    # 1. Créer le jeu et la carte
    jeu = Jeu(10, 10)

    # 2. Créer les généraux
    general_joueur1 = MajorDAFT(0)
    general_joueur2 = MajorDAFT(1)

    # 3. Ajouter les unités sur la carte
    # --- Crossbowman (joueur 1)
    for x in range(3):
        for y in range(10):
            jeu.ajouter_unite("Crossbowman",x,y,0)  

    # --- Pikeman (joueur 2)
    for x in range(7, 10):
        for y in range(10):
            jeu.ajouter_unite("Pikeman",x,y,1)

    # 4. Lancer et retourner le jeu complet
    while not jeu.est_termine():
        jeu.mettre_a_jour()
    return jeu

if __name__ == "__main__":
    scenario_Crossbowman_vs_Pikeman()




