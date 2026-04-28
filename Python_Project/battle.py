"""
MedievAIl BAIttle GenerAIl - CLI Entry Point

Usage:
    battle run <scenario> [AI1 AI2 ... AIx] [-t] [-d DATAFILE] [-m SIZE]
    battle load <savefile>
    battle tourney [-G AI1 AI2 ...] [-S SCENARIO1 SCENARIO2] [-N=10] [-na]
    battle plot <AI> <plotter> <scenario_call> <range_arg> [-N=10]
"""

import sys
import os
import importlib
import json
from threading import Thread


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(parent_dir)
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
    from backend.jeu import get_team_name,Jeu
    
    global ipc, partie, running, paused, partie_terminee, game_tick,manager_vue, gagnant_label, gagnant_id, clock
    
    config = load_scenario_config(args.scenario)
    map_size = args.map_size 
    ais = args.ais if args.ais else []

    print(f"\n[SCENARIO] {args.scenario}: {config.get('description', '')}")
    print(f"[UNITES] {config['units']}")
    print(f"[MAP] {map_size}x{map_size}")
    print(f"[IAs] {ais if ais else 'Aucune (ajout en jeu avec A)'}")

    if ais:
        partie = initialiser(ais, config["units"], map_size=map_size)
    else:
        partie = Jeu(largeur=map_size, hauteur=map_size)
    
    ipc = partie.get_ipc()

    manager_vue = ManagerVue(partie)
    save_manager = SaveManager()
    if args.t:
        manager_vue.mode_actuel = "TERMINAL"
    
    clock = pygame.time.Clock()
    running = True
    paused = True
    game_tick = 0
    partie_terminee = False
    gagnant_id = None     #int (team id) ou -1 pour égalité
    gagnant_label = None  #str pour l'affichage

    print("\n" + "="*60)
    print("  MedievAIl BAIttle GenerAIl")
    print("="*60)
    print(f"Scenario : {args.scenario}")
    print("Joueurs :")
    if not partie.generaux:
        print("Aucun joueur (appuie sur A pour en ajouter)")
    else:
        for pid,gen in partie.generaux.items():
            print(f"[{get_team_name(pid)}] Player {pid}: {gen.name}")
    print("-"*60)
    print("  CONTROLES:")
    print("  P             = Pause/Play")
    print("  A             = Ajouter une IA")
    print("  F9            = Changer vue (Pygame/Terminal)")
    print("  F10           = Plein ecran")
    print("  F11           = Quicksave")
    print("  F12           = Quickload")
    print("  TAB           = Ouvrir stats HTML")
    print("  R             = Recommencer")
    print("  ESC           = Quitter")
    print("="*60 + "\n")

    def tour_jeu():
        global running, paused, partie_terminee, game_tick, partie, clock
        while running:
            if not paused and not partie_terminee:
                game_tick += 1
                if game_tick >= 10:
                    game_tick = 0
                    partie.mettre_a_jour()

                    result = partie.check_victory()
                    # if result is not None:
                    #     partie_terminee = True
                    #     if result==-1:
                    #         gagnant_id = -1
                    #         gagnant_label = "EGALITE"
                    #         print("\n=== EGALITE ===\n")
                    #     else:
                    #         gagnant_id = result
                    #         team_name = get_team_name(result)
                    #         gen_name = partie.generaux[result].name if result in partie.generaux else "?"
                    #         gagnant_label = f"{team_name} ({gen_name})"
                    #         print(f"\n=== VICTOIRE PLAYER {result} — {gagnant_label} ===\n")
            clock.tick(60)
        
    
    def reception_message():
        global ipc, running, partie
        message = []
        while running:
            message = ipc.recevoir()  # Traite les messages IPC en temps réel
            if len(message) > 0:
                partie.appliquer_message(message)
            print(f"[IPC] Message recu: {message}")
            message = []          
    
    def pygame_loop():
        global manager_vue, partie_terminee, paused, partie, partie_terminee, gagnant_label, gagnant_id, running, clock
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
                            manager_vue.vue_pygame.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                        else:
                            manager_vue.vue_pygame.screen = pygame.display.set_mode((manager_vue.vue_pygame.SCREEN_WIDTH, manager_vue.vue_pygame.SCREEN_HEIGHT))

                    elif event.key == pygame.K_F11:
                        save_manager.sauvegarder(partie)
                        print("Partie sauvegardee!")

                    elif event.key == pygame.K_F12:
                        if save_manager.charger(partie):
                            partie_terminee = False
                            gagnant_id = None
                            gagnant_label = None
                            print("Partie chargee!")

                    elif event.key == pygame.K_TAB:
                        paused = True
                        manager_vue.vue_pygame.paused = True
                        save_manager.ouvrir_stats_html(partie)
                        print("Stats HTML ouvertes")

                    elif event.key==pygame.K_a:
                        #Ajout dynamique d'une IA supp
                        paused = True
                        manager_vue.vue_pygame.paused = True
                        ia_name = choisir_ia_pygame(manager_vue.vue_pygame.screen)
                        if ia_name:
                            partie.ajouter_joueur(ia_name, config["units"])
                            print(f"IA '{ia_name}' ajoutee (joueur {partie.next_player_id - 1})")
                        paused = False
                        manager_vue.vue_pygame.paused = False

                    elif event.key == pygame.K_r:
                        partie = initialiser(ais, config["units"], map_size=map_size)
                        manager_vue.jeu = partie
                        partie_terminee = False
                        gagnant_id = None
                        gagnant_label = None
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

            manager_vue.afficher(partie_terminee=partie_terminee, gagnant=gagnant_label, gagnant_id=gagnant_id)
            pygame.display.flip()
            clock.tick(60)  

                
    
    # Create threads
    thread1 = Thread(target=tour_jeu)
    thread2 = Thread(target=reception_message)

    # Start threads
    thread1.start()
    thread2.start()
    
    pygame_loop()  # Utilisation du thread principal pour éviter les problèmes de Pygame

    pygame.quit()

    if args.d and gagnant_label:
        data = {
            "scenario": args.scenario,
            "ais": ais,
            "winner_id": gagnant_id,
            "winner_label": gagnant_label,
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
    gagnant_label = None
    gagnant_id = None
    game_tick = 0

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

        if not paused and not partie_terminee:
            game_tick += 1
            if game_tick >= 10:
                game_tick = 0
                partie.mettre_a_jour()
                result = partie.check_victory()
                if result is not None:
                    partie_terminee = True
                    from backend.jeu import get_team_name
                    if result==-1:
                        gagnant_id = -1
                        gagnant_label = "EGALITE"
                    else:
                        gagnant_id = result
                        gen_name = partie.generaux[result].name if result in partie.generaux else "?"
                        gagnant_label = f"{get_team_name(result)} ({gen_name})"

        manager_vue.afficher(partie_terminee=partie_terminee, gagnant=gagnant_label,
                             gagnant_id=gagnant_id)
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
        scenarios_configs = {
            "standard": {"units": {"Knight": 20, "Pikeman": 20, "Crossbowman": 20}, "map_size": 120}
        }

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
    except Exception:
        r_val = range(10, 60, 10)

    print(f"Unités testées : {unit_types}")
    print(f"Valeurs de N   : {list(r_val)}")
    print("-" * 60)
    lanchester.plot_lanchester(args.ai, unit_types, r_val, args.N)

def choisir_ia_pygame(screen):
    import pygame

    font = pygame.font.SysFont(None, 40)
    small_font = pygame.font.SysFont(None, 28)

    ia_list = ["braindead", "daft", "turtle"]
    selected = 0

    clock = pygame.time.Clock()

    while True:
        screen.fill((30, 30, 30))

        title = font.render("Choisir une IA", True, (255, 255, 255))
        screen.blit(title, (50, 50))

        for i, ia in enumerate(ia_list):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            txt = small_font.render(ia, True, color)
            screen.blit(txt, (60, 120 + i * 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(ia_list)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(ia_list)
                elif event.key == pygame.K_RETURN:
                    return ia_list[selected]
                elif event.key == pygame.K_ESCAPE:
                    return None

        clock.tick(60)

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