import sys
import os
parent_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
sys.path.append(parent_dir)
from backend.jeu import Jeu

def test_equilibre(nb_combats=100):
    wins = {0: 0, 1: 0, "egalite": 0}
    
    for i in range(nb_combats):
        jeu = Jeu("braindead", "braindead")
        
        for x in range(3):
            for y in range(3):
                jeu.ajouter_unite("Knight", 2 + x, 10 + y, 0)
                jeu.ajouter_unite("Knight", 25 + x, 10 + y, 1)
        
        tours = 0
        while jeu.check_victory() is None and tours < 1000:
            jeu.mettre_a_jour()
            tours += 1
        
        result = jeu.check_victory()
        if result == 1:
            wins[1] += 1
        elif result == 2:
            wins[0] += 1
        else:
            wins["egalite"] += 1
        
        if (i + 1) % 10 == 0:
            print(f"Combat {i+1}/{nb_combats} - Equipe0: {wins[0]} | Equipe1: {wins[1]} | Egalites: {wins['egalite']}")
    
    print("\n" + "=" * 50)
    print("RESULTATS FINAUX")
    print("=" * 50)
    print(f"Equipe 0 (Bleu):  {wins[0]:3d} victoires ({wins[0]/nb_combats*100:.1f}%)")
    print(f"Equipe 1 (Rouge): {wins[1]:3d} victoires ({wins[1]/nb_combats*100:.1f}%)")
    print(f"Egalites:         {wins['egalite']:3d}")
    print("=" * 50)
    
    if 40 <= wins[0]/nb_combats*100 <= 60:
        print("OK - Equilibre correct (~50%)")
    else:
        print("PROBLEME - Desequilibre detecte!")
if __name__ == "__main__":
    test_equilibre(100)
