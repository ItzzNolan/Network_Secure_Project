"""
MedievAIl BAIttle GenerAIl - CLI Entry Point

Usage:
    battle run <scenario> <AI1> <AI2> [-t] [-d DATAFILE]
    battle load <savefile>
    battle tourney [-G AI1 AI2 ...] [-S SCENARIO1 SCENARIO2] [-N=10] [-na]
    battle plot <AI> <plotter> <scenario_call> <range_arg> [-N=10]
"""

import sys
import os
import importlib
import json
parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(parent_dir)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.cli import parse_args
SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), "scénario")

def list_scenarios():
    scenarios = []
    if os.path.exists(SCENARIOS_DIR):
        for f in os.listdir(SCENARIOS_DIR):
            if f.startswith("scenario_") and f.endswith(".py"):
                name = f.replace("scenario_", "").replace(".py", "")
                scenarios.append(name)
    return scenarios


def load_scenario_config(scenario_name):
    SCENARIO_CONFIGS = {
        "standard": {
            "units": {"Knight": 20, "Pikeman": 20, "Crossbowman": 20},
            "map_size": 50,
            "description": "Bataille standard equilibree"
        },
        "Crossbowman_vs_Knight": {
            "units": {"Crossbowman": 30, "Knight": 30},
            "map_size": 50,
            "description": "Arbaletriers contre Chevaliers"
        },
        "Crossbowman_vs_Pikeman": {
            "units": {"Crossbowman": 30, "Pikeman": 30},
            "map_size": 50,
            "description": "Arbaletriers contre Piquiers"
        },
        "chevalier_piquier": {
            "units": {"Knight": 30, "Pikeman": 30},
            "map_size": 50,
            "description": "Chevaliers contre Piquiers"
        },
        "MajorDAFT_vs_CaptainBraindead": {
            "units": {"Knight": 20, "Pikeman": 20, "Crossbowman": 20},
            "map_size": 50,
            "description": "Test IA DAFT vs BRAINDEAD"
        },
        "small": {
            "units": {"Knight": 5, "Pikeman": 5},
            "map_size": 30,
            "description": "Petite bataille de test"
        },
        "large": {
            "units": {"Knight": 50, "Pikeman": 50, "Crossbowman": 50},
            "map_size": 80,
            "description": "Grande bataille"
        },
        "huge": {
            "units": {"Knight": 80, "Pikeman": 80, "Crossbowman": 80},
            "map_size": 120,
            "description": "Bataille massive (120x120)"
        },
        "lanchester": {
            "units": {"Knight": 50, "Pikeman": 100},
            "map_size": 120,
            "description": "Test lois de Lanchester (N vs 2N)"
        }
    }

    key = scenario_name.lower().replace("-", "_")
    for name, config in SCENARIO_CONFIGS.items():
        if name.lower() == key:
            return config

    return SCENARIO_CONFIGS["standard"]

def cmd_run(args):
    import pygame
    from scenario.play_tournament import initialiser
    from frontend.manager_vue import ManagerVue
    from backend.save_manager import SaveManager

    config = load_scenario_config(args.scenario)
    map_size = args.map_size 
    print(f"\n[SCENARIO] {args.scenario}: {config.get('description', '')}")
    print(f"[UNITES] {config['units']}")
    print(f"[MAP] {map_size}x{map_size}")
    partie = initialiser([args.ai1, args.ai2], config["units"], map_size=map_size)
    manager_vue = ManagerVue(partie)
    save_manager = SaveManager()
    if args.t:
        manager_vue.mode_actuel = "TERMINAL"
    
    clock = pygame.time.Clock()
    running = True
    paused = True
    game_tick = 0
    partie_terminee = False
    gagnant = None
    
    print("\n" + "="*60)
    print("  MedievAIl BAIttle GenerAIl")
    print("="*60)
    print(f"  Scenario:      {args.scenario}")
    print(f"  General Bleu:  {partie.generaux[0].name}")
    print(f"  General Rouge: {partie.generaux[1].name}")
    print("-"*60)
    print("  CONTROLES:")
    print("  P             = Pause/Play")
    print("  F9            = Changer vue (Pygame/Terminal)")
    print("  F10           = Plein ecran")
    print("  F11           = Quicksave")
    print("  F12           = Quickload")
    print("  TAB           = Ouvrir stats HTML")
    print("  R             = Recommencer")
    print("  ESC           = Quitter")
    print("="*60 + "\n")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_p and not partie_terminee:
                    paused = not paused
                    manager_vue.vue_pygame.paused = paused
                    print("PAUSE" if paused else "EN JEU")
                
                elif event.key == pygame.K_F9:
                    manager_vue.changer_mode()
                
                elif event.key == pygame.K_F10:
                    manager_vue.vue_pygame.fullscreen = not manager_vue.vue_pygame.fullscreen
                    if manager_vue.vue_pygame.fullscreen:
                        manager_vue.vue_pygame.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        manager_vue.vue_pygame.screen = pygame.display.set_mode(
                            (manager_vue.vue_pygame.SCREEN_WIDTH, manager_vue.vue_pygame.SCREEN_HEIGHT))
                
                elif event.key == pygame.K_F11:
                    save_manager.sauvegarder(partie)
                    print("Partie sauvegardee!")
                
                elif event.key == pygame.K_F12:
                    if save_manager.charger(partie):
                        partie_terminee = False
                        gagnant = None
                        print("Partie chargee!")
                
                elif event.key == pygame.K_TAB:
                    paused = True
                    manager_vue.vue_pygame.paused = True
                    save_manager.ouvrir_stats_html(partie)
                    print("Stats HTML ouvertes")
                
                elif event.key == pygame.K_r:
                    partie = initialiser([args.ai1, args.ai2], config["units"], map_size=map_size)
                    manager_vue.jeu = partie
                    partie_terminee = False
                    gagnant = None
                    paused = True
                    manager_vue.vue_pygame.paused = True
                    print("Nouvelle partie!")
                
                elif event.key == pygame.K_SPACE:
                    if manager_vue.mode_actuel == "TERMINAL":
                        auto = manager_vue.vue_terminal.toggle_auto_follow()
                        print(f"Auto-follow: {'ON' if auto else 'OFF'}")
        
        keys = pygame.key.get_pressed()
        shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        if manager_vue.mode_actuel == "PYGAME":
            manager_vue.vue_pygame.gerer_camera(keys)
        else:
            manager_vue.vue_terminal.gerer_touches(keys, shift)

        if not paused and not partie_terminee:
            game_tick += 1
            if game_tick >= 10:
                game_tick = 0
                partie.mettre_a_jour()
                
                result = partie.check_victory()
                if result == 1:
                    partie_terminee = True
                    gagnant = "ROUGE"
                    print(f"\n{'='*40}")
                    print(f"  VICTOIRE {partie.generaux[1].name}!")
                    print(f"  (Equipe Rouge)")
                    print(f"{'='*40}\n")
                elif result == 2:
                    partie_terminee = True
                    gagnant = "BLEU"
                    print(f"\n{'='*40}")
                    print(f"  VICTOIRE {partie.generaux[0].name}!")
                    print(f"  (Equipe Bleu)")
                    print(f"{'='*40}\n")
                elif result == 0:
                    partie_terminee = True
                    gagnant = "EGALITE"
                    print(f"\n{'='*40}")
                    print(f"  EGALITE!")
                    print(f"{'='*40}\n")
        
        manager_vue.afficher(partie_terminee=partie_terminee, gagnant=gagnant)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
  
    if args.d and gagnant:
        data = {
            "scenario": args.scenario,
            "ai1": args.ai1,
            "ai2": args.ai2,
            "winner": gagnant,
            "turns": partie._tour,
            "units_remaining": len([u for u in partie.unites if u.alive])
        }
        with open(args.d, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Donnees sauvegardees dans {args.d}")

def cmd_load(args):
    import pygame
    from backend.jeu import Jeu
    from backend.save_manager import SaveManager
    from frontend.manager_vue import ManagerVue
    
    partie = Jeu()
    save_manager = SaveManager()
    
    if not save_manager.charger(partie, args.savefile):
        print(f"Erreur: impossible de charger {args.savefile}")
        return
    
    print(f"Partie chargee depuis {args.savefile}")
    
    manager_vue = ManagerVue(partie)
    clock = pygame.time.Clock()
    running = True
    paused = True
    partie_terminee = False
    gagnant = None
    game_tick = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    manager_vue.vue_pygame.gerer_clic_minimap(event.pos)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p and not partie_terminee:
                    paused = not paused
                    manager_vue.vue_pygame.paused = paused
                elif event.key == pygame.K_F9:
                    manager_vue.changer_mode()
                elif event.key == pygame.K_F10:
                    manager_vue.vue_pygame.fullscreen = not manager_vue.vue_pygame.fullscreen
                    if manager_vue.vue_pygame.fullscreen:
                        manager_vue.vue_pygame.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        manager_vue.vue_pygame.screen = pygame.display.set_mode(
                            (manager_vue.vue_pygame.SCREEN_WIDTH, manager_vue.vue_pygame.SCREEN_HEIGHT))
                elif event.key == pygame.K_F11:
                    save_manager.sauvegarder(partie)
                elif event.key == pygame.K_F12:
                    save_manager.charger(partie)
                elif event.key == pygame.K_TAB:
                    paused = True
                    save_manager.ouvrir_stats_html(partie)
        
        keys = pygame.key.get_pressed()
        manager_vue.vue_pygame.gerer_camera(keys)
        
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            mouse_pos = pygame.mouse.get_pos()
            manager_vue.vue_pygame.gerer_clic_minimap(mouse_pos)
        
        if not paused and not partie_terminee:
            game_tick += 1
            if game_tick >= 10:
                game_tick = 0
                partie.mettre_a_jour()
                
                result = partie.check_victory()
                if result == 1:
                    partie_terminee = True
                    gagnant = "ROUGE"
                elif result == 2:
                    partie_terminee = True
                    gagnant = "BLEU"
                elif result == 0:
                    partie_terminee = True
                    gagnant = "EGALITE"
        
        manager_vue.afficher(partie_terminee=partie_terminee, gagnant=gagnant)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


def cmd_tourney(args):
    from scenario.play_tournament import tournoi
    from scenario.tournament_calcul import Tournament
    
    generaux = args.G if args.G else ["braindead", "daft"]
    if args.S:
        scenarios_configs = {}
        for s in args.S:
            config = load_scenario_config(s)
            scenarios_configs[s] = {"units": config["units"], "map_size": config.get("map_size", 120)}
    else:
        scenarios_configs = {"standard": {"units": {"Knight": 20, "Pikeman": 20, "Crossbowman": 20}, "map_size": 120}}
    
    print("\n" + "="*60)
    print("  TOURNOI MedievAIl BAIttle GenerAIl")
    print("="*60)
    print(f"  Generaux: {', '.join(generaux)}")
    print(f"  Scenarios: {', '.join(scenarios_configs.keys())}")
    print(f"  Combats par matchup: {args.N}")
    print(f"  Alternance positions: {'Non' if args.na else 'Oui'}")
    print("="*60 + "\n")
    all_scenarios = {name: config["units"] for name, config in scenarios_configs.items()}
    tournament = Tournament(generaux, all_scenarios)
    for scenario_name, config in scenarios_configs.items():
        print(f"\n>>> Scenario: {scenario_name} (map {config['map_size']}x{config['map_size']})")
        tournoi(generaux, config["units"], args.N, not_alternate=args.na, 
                map_size=config["map_size"], scenario_name=scenario_name, tournament=tournament)
    tournament.generer_rapport_html()

def cmd_plot(args):
    import scenario.lanchester as lanchester
    import re

    print("\n" + "="*60)
    print("  MODE ANALYSE : COMPARAISON LANCHESTER")
    print("="*60)
    match_list = re.search(r"\[(.*?)\]", args.scenario_call)
    
    if match_list:
        raw_list = match_list.group(1)
        unit_types = [u.strip().strip("'").strip('"') for u in raw_list.split(',')]
    else:
        match_single = re.search(r"'(.*?)'", args.scenario_call)
        unit_types = [match_single.group(1)] if match_single else ["Knight"]
    try:
        r_val = eval(args.range_arg)
    except:
        r_val = range(10, 60, 10)

    print(f"  Unités testées    : {unit_types}")
    print(f"  Valeurs de N      : {list(r_val)}")
    print("-" * 60)
    lanchester.plot_lanchester(args.ai, unit_types, r_val, args.N)

def main():
    args = parse_args()
    
    if args.command == "run":
        cmd_run(args)
    elif args.command == "load":
        cmd_load(args)
    elif args.command == "tourney":
        cmd_tourney(args)
    elif args.command == "plot":
        cmd_plot(args)
    else:
        print("Commande inconnue. Utilisez --help pour l'aide.")


if __name__ == "__main__":
    main()
