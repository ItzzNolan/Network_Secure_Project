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
    from ipc.ipc_python import IPCClient  # NOUVEAU

    config = load_scenario_config(args.scenario)
    map_size = args.map_size 
    print(f"\n[SCENARIO] {args.scenario}: {config.get('description', '')}")
    print(f"[UNITES] {config['units']}")
    print(f"[MAP] {map_size}x{map_size}")
    partie = initialiser([args.ai1, args.ai2], config["units"], map_size=map_size)
    manager_vue = ManagerVue(partie)
    save_manager = SaveManager()

    # NOUVEAU : connexion IPC
    ipc = None
    if hasattr(args, 'network') and args.network:
        player_id = args.player_id if hasattr(args, 'player_id') else 1
        ipc = IPCClient(port_c=9999, port_python=9998)
        print(f"[RESEAU] Mode réseau activé, joueur {player_id}")

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

                # NOUVEAU : envoyer les changements aux autres joueurs
                if ipc:
                    for unite in partie.unites:
                        if unite.alive and unite.a_bouge:  # si l'unité a bougé ce tour
                            ipc.envoyer({
                                "type": "UPDATE",
                                "action": "MOVE",
                                "entity_id": unite.id,
                                "x": unite.x,
                                "y": unite.y,
                                "player_id": player_id
                            })
                
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

        # NOUVEAU : recevoir les messages des autres joueurs
        if ipc:
            messages = ipc.recevoir()
            for msg in messages:
                msg_type = msg.get("type")
                action = msg.get("action")

                if msg_type == "UPDATE" and action == "MOVE":
                    for unite in partie.unites:
                        if unite.id == msg["entity_id"]:
                            partie.carte.retirer_unite(unite)
                            unite.x = msg["x"]
                            unite.y = msg["y"]
                            partie.carte.placer_unite(unite, msg["x"], msg["y"])
                            print(f"[RESEAU] Unité {unite.id} bouge en ({msg['x']}, {msg['y']})")
                            break

                elif msg_type == "UPDATE" and action == "ATTACK":
                    for unite in partie.unites:
                        if unite.id == msg["target_id"]:
                            unite.hp -= msg["damage"]
                            print(f"[RESEAU] Unité {unite.id} subit {msg['damage']} dégâts")
                            break

                elif msg_type == "UPDATE" and action == "DIE":
                    for unite in partie.unites:
                        if unite.id == msg["entity_id"]:
                            unite.alive = False
                            partie.carte.retirer_unite(unite)
                            print(f"[RESEAU] Unité {unite.id} meurt")
                            break
        
        manager_vue.afficher(partie_terminee=partie_terminee, gagnant=gagnant)
        pygame.display.flip()
        clock.tick(60)
    
    # NOUVEAU : déconnexion propre
    if ipc:
        ipc.envoyer({"type": "DISCONNECT", "player_id": player_id})
        ipc.fermer()

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