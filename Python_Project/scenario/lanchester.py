import random
import os
import sys
import matplotlib.pyplot as plt  
parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(parent_dir)

from backend.jeu import Jeu

def initialiser(generaux: list, list_unite: dict, map_size: int = 50):
    gen1 = generaux[0]
    gen2 = generaux[1] if len(generaux) > 1 else generaux[0]
    partie = Jeu(gen1, gen2, largeur=map_size, hauteur=map_size)
    
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
    col_max = (len(liste) // h) + 1
    
    current_idx = 0
    for col in range(col_max + 2):
        if current_idx >= len(liste): break
        for y in range(h):
            if current_idx >= len(liste): break
            pos_x_0 = 2 + col
            pos_y = y
            pos_x_1 = partie.carte.largeur - 3 - col
            
            unit_type = liste[current_idx]
            
            if partie.carte.est_dans_grille(pos_x_0, pos_y):
                partie.ajouter_unite(unit_type, pos_x_0, pos_y, 0)
            
            if partie.carte.est_dans_grille(pos_x_1, pos_y):
                partie.ajouter_unite(unit_type, pos_x_1, pos_y, 1)
                
            current_idx += 1

    return partie


def run_lanchester_simulation(unit_type, N):
    map_sz = 120 
    partie = Jeu("daft", "daft", largeur=map_sz, hauteur=map_sz)
    col = 0
    row = 0
    for _ in range(N):
        partie.ajouter_unite(unit_type, 10 + col, 10 + row, 0)
        row += 1
        if row > 50:
            row = 0
            col += 1
    col = 0
    row = 0
    for _ in range(2 * N):
        partie.ajouter_unite(unit_type, map_sz - 10 - col, 10 + row, 1)
        row += 1
        if row > 50:
            row = 0
            col += 1
    while partie.check_victory() is None and partie._tour < 2000: 
        partie.mettre_a_jour()
    survivants_bleus = len([u for u in partie.unites if u.alive and u.equipe == 0])
    survivants_rouges = len([u for u in partie.unites if u.alive and u.equipe == 1])
    
    return max(survivants_bleus, survivants_rouges)


def plot_lanchester(ai_name, unit_types, range_values, n_simulations=1):
    print(f"\n--- Simulation Lanchester Multi-Unités ---")
    
    plt.figure(figsize=(10, 6))
    for unit_type in unit_types:
        print(f"\nCalcul pour l'unité : {unit_type}")
        results_x = []
        results_y = []
        
        for n in range_values:
            print(f"  N={n}...", end="", flush=True)
            total_survivors = 0
            for _ in range(n_simulations):
                surv = run_lanchester_simulation(unit_type, n)
                total_survivors += surv
            
            avg_survivors = total_survivors / n_simulations
            results_x.append(n)
            results_y.append(avg_survivors)
            print(" Done.")
        plt.plot(results_x, results_y, marker='o', label=f'Survivants {unit_type}')
    plt.title(f"Vérification Lois de Lanchester (IA: {ai_name})")
    plt.xlabel("Taille de l'armée initiale N (vs 2N)")
    plt.ylabel("Nombre de survivants du vainqueur")
    plt.grid(True)
    plt.legend()
    
    plt.savefig("lanchester_comparison.png")
    print(f"\nGraphique comparatif sauvegardé: lanchester_comparison.png")
    plt.show()
