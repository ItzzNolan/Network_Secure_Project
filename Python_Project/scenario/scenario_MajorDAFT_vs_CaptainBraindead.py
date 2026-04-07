from backend.carte import Carte
from backend.Units import Unit  
from backend.jeu import Jeu
from ia.general import CaptainBraindead, MajorDAFT
from frontend.vue_terminal import afficher

def scenario_MajorDAFT_vs_CaptainBraindead():  

    # 1. Créer le jeu et la carte
    jeu = Jeu(10, 10)

    # 2. Créer les généraux
    general_joueur1 = MajorDAFT(0)
    general_joueur2 = CaptainBraindead(1)

    # 3. Ajouter les unités sur la carte
    # --- MajorDAFT (joueur 1) BLEU
    for x in range(3):
        for y in range(10):
            jeu.ajouter_unite("Pikeman",x,y,0)  

    # --- CaptainBraindead (joueur 2) ROUGE
    for x in range(7, 10):
        for y in range(10):
            jeu.ajouter_unite("Pikeman",x,y,1)

    # 4. Lancer et retourner le jeu complet
    while not jeu.est_termine():
        jeu.mettre_a_jour()
    return jeu

if __name__ == "__main__":
    scenario_MajorDAFT_vs_CaptainBraindead()
    


