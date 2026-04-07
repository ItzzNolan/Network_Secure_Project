import os
import sys
import random
parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(parent_dir)
from backend.jeu import Jeu
from ia.general import make_general
from scenario.tournament_calcul import Tournament


def end_fight(generaux: list, list_unite: dict, swap_positions=False, map_size=30):
    partie = initialiser(generaux, list_unite, swap_positions, map_size)
    return partie


def initialiser(generaux: list, list_unite: dict, swap_positions=False, map_size=30):
    if len(generaux) == 1:
        partie = Jeu(generaux[0], generaux[0], largeur=map_size, hauteur=map_size)
    else:
        partie = Jeu(generaux[0], generaux[1], largeur=map_size, hauteur=map_size)
    
    liste = []
    for k, v in list_unite.items():
        for i in range(v):
            liste.append(k)
    random.shuffle(liste)
    
    h = partie.carte.hauteur
    mid = h // 2
    x = 0
    taille = len(liste)
    cpt = 0
    
    while taille > h:
        taille //= 2
        x += 1
    
    equipe_gauche = 1 if swap_positions else 0
    equipe_droite = 0 if swap_positions else 1
    
    for i in range(x + 1):
        for j in range(mid - taille // 2, mid - taille // 2 + taille):
            partie.ajouter_unite(f"{liste[cpt]}", i, j, equipe_gauche)
            partie.ajouter_unite(f"{liste[cpt]}", partie.carte.largeur - i - 1, j, equipe_droite)
            cpt += 1
    
    return partie


def tournoi(generaux: list, list_unite: dict, nb_combat=100, not_alternate=False, map_size=30, scenario_name="sc1", tournament=None):
    """
    Lance un tournoi entre les généraux.
    
    Si tournament est fourni, les résultats y sont ajoutés (mode multi-scénarios).
    Sinon, un nouveau Tournament est créé et le rapport est généré à la fin.
    """
    # Mode standalone (un seul scénario)
    standalone = tournament is None
    if standalone:
        tournament = Tournament(generaux, {scenario_name: list_unite})
    
    for idx_g1 in range(len(generaux)):
        for idx_g2 in range(idx_g1, len(generaux)):
            g1_name = generaux[idx_g1]
            g2_name = generaux[idx_g2]
            
            wins_equipe0 = 0
            wins_equipe1 = 0
            draws = 0
            
            print(f"\n{'='*50}")
            print(f"  {g1_name} vs {g2_name}")
            if not_alternate:
                print(f"  (positions fixes)")
            else:
                print(f"  (positions alternees)")
            print(f"{'='*50}")
            print(list_unite)
            
            for combat_num in range(nb_combat):
                if not_alternate:
                    swap = False
                else:
                    swap = (combat_num % 2 == 1)
                
                partie = initialiser([g1_name, g2_name], list_unite, swap_positions=swap, map_size=map_size)
                
                print(f"Combat {combat_num + 1}/{nb_combat} - {len(partie.unites)} unites")
                
                max_tours = 1000
                while partie.check_victory() is None and partie._tour < max_tours:
                    partie.mettre_a_jour()
                
                result = partie.check_victory()
                
                if result == 1:
                    vainqueur = g2_name
                    wins_equipe1 += 1
                elif result == 2:
                    vainqueur = g1_name
                    wins_equipe0 += 1
                else:
                    vainqueur = "egalite"
                    draws += 1
                
                print(f"  -> Vainqueur: {vainqueur} (tour {partie._tour}, {len(partie.unites)} restants)")
                
                tournament.enregistrer_resultat(
                    scenario_name,
                    g1_name,
                    g2_name,
                    vainqueur
                )
            
            print(f"\n{'='*50}")
            print(f"  RESULTATS: {g1_name} vs {g2_name}")
            print(f"{'='*50}")
            total = wins_equipe0 + wins_equipe1 + draws
            pct_0 = (wins_equipe0 / total * 100) if total > 0 else 0
            pct_1 = (wins_equipe1 / total * 100) if total > 0 else 0
            print(f"  Equipe 0 ({g1_name}): {wins_equipe0} victoires ({pct_0:.1f}%)")
            print(f"  Equipe 1 ({g2_name}): {wins_equipe1} victoires ({pct_1:.1f}%)")
            print(f"  Egalites: {draws}")
            if g1_name == g2_name:
                if 40 <= pct_0 <= 60 and 40 <= pct_1 <= 60:
                    print(f"  -> OK: Equilibre correct (~50%)")
                else:
                    print(f"  -> ATTENTION: Desequilibre detecte!")
            print(f"{'='*50}")
    
    # Générer le rapport seulement en mode standalone
    if standalone:
        tournament.generer_rapport_html()
    
    return tournament


if __name__ == "__main__":
    tournoi(["braindead", "daft"], {"Pikeman": 20, "Knight": 20, "Crossbowman": 20}, 10, not_alternate=False)
