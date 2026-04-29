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
import socket
import time
import uuid
from threading import Lock
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
    from backend.carte import Carte
    from ia.general import make_general
    
    global ipc, partie, running, paused, partie_terminee, game_tick,manager_vue, gagnant_label, gagnant_id, clock
    
    config = load_scenario_config(args.scenario)
    map_size = args.map_size 
    ais = args.ais if args.ais else []
    lan_mode = not bool(ais)

    print(f"\n[SCENARIO] {args.scenario}: {config.get('description', '')}")
    print(f"[UNITES] {config['units']}")
    print(f"[MAP] {map_size}x{map_size}")
    print(f"[IAs] {ais if ais else ('Aucune (LAN)' if lan_mode else 'Aucune (ajout en jeu avec A)')}")

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
        print("Aucun joueur (en attente LAN...)" if lan_mode else "Aucun joueur (appuie sur A pour en ajouter)")
    else:
        for pid,gen in partie.generaux.items():
            print(f"[{get_team_name(pid)}] Player {pid}: {gen.name}")
    print("-"*60)
    print("  CONTROLES:")
    if lan_mode:
        print("(LAN) Lancement auto à 2 joueurs")
    else:
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

    if lan_mode:
        LAN_PORT = 27105
        BROADCAST_ADDR = "255.255.255.255"
        DISCOVERY_TIMEOUT_SEC = 2.0
        HOST_ANNOUNCE_INTERVAL_SEC = 0.5
        STATE_SYNC_MIN_INTERVAL_SEC = 0.05

        state_lock = Lock()

        def get_local_ipv4():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("1.1.1.1", 80))
                return s.getsockname()[0]
            except Exception:
                return "127.0.0.1"
            finally:
                s.close()
        
        def send_udp(payload:dict, addr):
            data = json.dumps(payload).encode("utf-8")
            sock.sendto(data, addr)
        
        def build_state():
            with state_lock:
                return build_state_unlocked()
            
        def build_state_unlocked():
            units_data = []
            for unit in partie.unites:
                if not getattr(unit, "alive", False) or not unit.coords:
                    continue
                x,y = unit.coords
                units_data.append({
                    "unit_type":unit.unit_type,
                    "equipe":unit.equipe,
                    "x":round(float(x),2),
                    "y":round(float(y),2),
                    "hp":int(getattr(unit, "HP", 0)),
                })
            
            generaux_data = {str(pid):gen.name for pid,gen in partie.generaux.items()}

            return {
                "type": "STATE",
                "scenario": args.scenario,
                "map_size": map_size,
                "tick": int(getattr(partie, "_tour", 0)),
                "generaux": generaux_data,
                "units": units_data,
            }
        
        def apply_state(state):
            with state_lock:
                partie._tour = int(state.get("tick",0))
                #reset map+state
                partie.carte = Carte(largeur=map_size, hauteur=map_size)
                partie.unites = []
                partie.generaux = {}
                generaux = state.get("generaux", {}) or {}
                for pid, ia_name in generaux.items():
                    try:
                        pid = int(pid)
                    except Exception:
                        continue
                    partie.generaux[pid] = make_general(ia_name, id_player=pid)
                
                if partie.generaux:
                    partie.next_player_id = max(partie.generaux.keys()) + 1
                else:
                    partie.next_player_id = 0

                for unit in state.get("units", []) or []:
                    unit_type = unit.get("unit_type")
                    equipe = int(unit.get("equipe",0))
                    x = float(unit.get("x",0))
                    y = float(unit.get("y",0))
                    hp = int(unit.get("hp",0))

                    ix = int(round(x))
                    iy = int(round(y))

                    if not partie.carte.est_dans_grille(ix, iy):
                        continue

                    partie.ajouter_unite(unit_type, ix, iy, equipe)
                    created = partie.unites[-1] if partie.unites else None

                    if created:
                        created.coords = (x,y)
                        created.HP = hp
                        created.alive = True
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.2)
        sock.bind(("", LAN_PORT))

        device_id = uuid.uuid4().hex[:10]
        local_ip = get_local_ipv4()

        host_info = None
        discover_payload = {
            "type":"DISCOVER",
            "device_id":device_id,
            "scenario":args.scenario,
            "map_size":map_size,
        }

        #broadcast
        try:
            sock.sendto(json.dumps(discover_payload).encode("utf-8"), (BROADCAST_ADDR, LAN_PORT))
        except Exception:
            pass

        t = time.time()
        while time.time() - t < DISCOVERY_TIMEOUT_SEC and host_info is None:
            try:
                data,addr = sock.recvfrom(65535)
                msg = json.loads(data.decode("utf-8"))
                if msg.get("type") == "HOST_ANNOUNCE":
                    if msg.get("scenario") == args.scenario and int(msg.get("map_size", -1)) == map_size:
                        host_info = {
                            "host_device_id":msg.get("host_device_id"),
                            "host_ip":msg.get("host_ip"),
                        }
                        break
            except socket.timeout:
                continue
            except Exception:
                continue
        
        is_host = host_info is None
        cli_addrs = []
        host_addr = None
        host_device_id = None
        host_ready = False
        game_started = False
        lan_msg = "Initialisation LAN..."

        def host_announce_loop():
            nonlocal host_device_id,lan_msg
            host_device_id = device_id
            while running:
                payload = {
                    "type": "HOST_ANNOUNCE",
                    "host_device_id": host_device_id,
                    "host_ip": local_ip,
                    "scenario": args.scenario,
                    "map_size": map_size,
                }

                try:
                    sock.sendto(json.dumps(payload).encode("utf-8"), (BROADCAST_ADDR,LAN_PORT))
                except Exception:
                    pass

                if host_ready and not game_started and not partie_terminee:
                    lan_msg = "En attente d'un 2e joueur..."

                time.sleep(HOST_ANNOUNCE_INTERVAL_SEC)
        
        #start host
        if is_host:
            thread_announce = Thread(target=host_announce_loop, daemon=True)
            thread_announce.start()

        pygame_init = True
        host_ia_name = None

        if is_host:
            lan_msg = "Choix IA (Joueur 1)"
            manager_vue.vue_pygame.paused = True
            paused = True
            host_ia_name = choisir_ia_pygame(manager_vue.vue_pygame.screen)
            if not host_ia_name:
                running = False
                pygame.quit()
                try:
                    sock.close()
                except Exception:
                    pass
                return 
            
            partie.ajouter_joueur(host_ia_name,config["units"])
            host_ready = True
            lan_msg = "En attente d'un 2e joueur..."
            manager_vue.vue_pygame.paused = True
            paused = True
        
        else:
            host_device_id = host_info.get("host_device_id")
            host_ip = host_info.get("host_ip")
            host_addr = (host_ip,LAN_PORT)
            lan_msg = "Connexion en cours..."
            manager_vue.vue_pygame.paused = True
            paused = True

            cli_ia_name = choisir_ia_pygame(manager_vue.vue_pygame.screen)
            if not cli_ia_name:
                running = False
                pygame.quit()
                try:
                    sock.close()
                except Exception:
                    pass
                return
            
            join_payload = {
                "type": "JOIN_REQ",
                "device_id": device_id,
                "scenario": args.scenario,
                "map_size": map_size,
                "ai": cli_ia_name,
            }

            try:
                send_udp(join_payload,host_addr)
            except Exception:
                #host dispawn
                pass
            
        def send_state_to_clients():
            if not cli_addrs:
                return
            
            payload = build_state()

            for addr in cli_addrs:
                try:
                    sock.sendto(json.dumps(payload).encode("utf-8"),addr)
                except Exception:
                    pass

        def send_game_over_to_clients(winner_pid):
            payload = {
                "type": "GAME_OVER",
                "scenario": args.scenario,
                "map_size": map_size,
                "winner_pid": winner_pid,
            }

            for addr in cli_addrs:
                try:
                    sock.sendto(json.dumps(payload).encode("utf-8"),addr)
                except Exception:
                    pass

        def lan_listener_loop():
            global paused, partie_terminee, gagnant_label, gagnant_id
            nonlocal game_started, cli_addrs, host_ready, host_addr, lan_msg
            connected_cli_ips = set()

            while running:
                try:
                    data,addr = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                except Exception:
                    continue

                try:
                    msg = json.loads(data.decode("utf-8"))
                except Exception:
                    continue

                m_type = (msg.get("type") or "").upper()

                if is_host and m_type == "JOIN_REQ":
                    if not host_ready or game_started:
                        continue

                    if msg.get("scenario") != args.scenario or int(msg.get("map_size",-1)) != map_size:
                        continue

                    cli_ip = addr[0]
                    if cli_ip in connected_cli_ips:
                        continue

                    if len(partie.generaux)>=2:
                        continue

                    connected_cli_ips.add(cli_ip)
                    cli_addrs.append(addr)

                    cli_ia_name = msg.get("ai")
                    if not cli_ia_name:
                        continue

                    with state_lock:
                        partie.ajouter_joueur(str(cli_ia_name),config["units"])

                    #combat started
                    game_started = True
                    paused = False
                    manager_vue.vue_pygame.paused = False
                    lan_msg = ""

                    try:
                        sock.sendto(json.dumps(build_state()).encode("utf-8"),addr)
                    except Exception:
                        pass

                if not is_host and m_type == "STATE":
                    if msg.get("scenario") != args.scenario or int(msg.get("map_size",-1)) != map_size:
                        continue
                    if not game_started:
                        game_started = True
                        paused = False
                        manager_vue.vue_pygame.paused = False
                        lan_msg = ""
                    
                    apply_state(msg)
                
                if not is_host and m_type == "GAME_OVER":
                    winner_pid = int(msg.get("winner_pid",-1))
                    partie_terminee = True
                    paused = True
                    manager_vue.vue_pygame.paused = True
                    gagnant_id = winner_pid
                    
                    if winner_pid == -1:
                        gagnant_label = "EGALITE"

                    else:
                        gen_name = partie.generaux[winner_pid].name if winner_pid in partie.generaux else "?"
                        gagnant_label = f"{get_team_name(winner_pid)} ({gen_name})"
                    
                    lan_msg = "Combat termine!"

        thread_lan = Thread(target=lan_listener_loop, daemon=True)
        thread_lan.start()

        last_state_sent = 0.0

        def tour_jeu_lan():
            nonlocal last_state_sent, game_started
            global running, paused, partie_terminee, game_tick, partie, clock, gagnant_label, gagnant_id

            while running:
                if is_host and (not paused) and (not partie_terminee) and game_started:
                    game_tick+=1
                    if game_tick>=10:
                        game_tick=0
                        with state_lock:
                            partie.mettre_a_jour()

                        result = partie.check_victory()
                        if result is not None:
                            partie_terminee = True
                            paused = True
                            manager_vue.vue_pygame.paused = True
                            gagnant_id = result
                            if result==-1:
                                gagnant_label = "EGALITE"
                            else:
                                gen_name = partie.generaux[result].name if result in partie.generaux else "?"
                                gagnant_label = f"{get_team_name(result)} ({gen_name})"
                            send_game_over_to_clients(result)

                        now = time.time()
                        if now - last_state_sent>=STATE_SYNC_MIN_INTERVAL_SEC:
                            last_state_sent = now
                            payload = build_state_unlocked()

                            for addr in cli_addrs:
                                try:
                                    sock.sendto(json.dumps(payload).encode("utf-8"), addr)
                                except Exception:
                                    pass

                time.sleep(1/60)

        thread_sim = Thread(target=tour_jeu_lan, daemon=True) #hostonly
        thread_sim.start()

        def draw_lan_overlay():
            if manager_vue.mode_actuel != "PYGAME":
                return
            if game_started and not partie_terminee:
                #pas dark screen
                return
            if not lan_msg:
                return
            screen = manager_vue.vue_pygame.screen
            w,h = screen.get_size()
            overlay = pygame.Surface((w,h), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            screen.blit(overlay, (0,0))

            font_big = pygame.font.SysFont("Segoe UI", 38, bold=True)
            font_sub = pygame.font.SysFont("Segoe UI", 20)
            box_w,box_h = 600,150
            box_x = (w-box_w) // 2
            box_y = (h-box_h) // 2

            pygame.draw.rect(screen, (20, 20, 30), (box_x, box_y, box_w, box_h))
            pygame.draw.rect(screen, (255,255,255), (box_x, box_y, box_w, box_h), 3)
            title = font_big.render(lan_msg, True, (255, 255, 255))
            sub = font_sub.render("Le combat démarrera à partir de 2 joueurs...", True, (200, 200, 200))
            screen.blit(title, (w // 2-title.get_width() // 2, h // 2-40))
            screen.blit(sub, (w // 2-sub.get_width() // 2, h // 2+10))

        thread2 = Thread(target=reception_message, daemon=True) if 'reception_message' in locals() else None

        def reception_message_lan():
            global ipc, running, partie
            liste_message = []

            while running:
                try:
                    liste_message = ipc.recevoir()
                except Exception:
                    liste_message = []

                if len(liste_message) > 0:
                    for msg in liste_message:
                        print(f"[IPC] Message recu: {msg}")
                        partie.appliquer_message(msg)

                liste_message = []

        thread_ipc = Thread(target=reception_message_lan, daemon=True)
        thread_ipc.start()

        def pygame_loop_lan():
            global manager_vue, partie_terminee, paused, partie, gagnant_label, gagnant_id, running, clock, game_tick
            
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

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
                            if save_manager.charger(partie):
                                partie_terminee = False
                                gagnant_id = None
                                gagnant_label = None

                        elif event.key == pygame.K_TAB:
                            paused = True
                            manager_vue.vue_pygame.paused = True
                            save_manager.ouvrir_stats_html(partie)

                        elif event.key == pygame.K_r:
                            #Reset local ne work pas e LAN
                            manager_vue.jeu = partie
                            partie_terminee = False
                            gagnant_id = None
                            gagnant_label = None
                            paused = True
                            manager_vue.vue_pygame.paused = True

                keys = pygame.key.get_pressed()
                shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

                if manager_vue.mode_actuel == "PYGAME":
                    manager_vue.vue_pygame.gerer_camera(keys)
                else:
                    manager_vue.vue_terminal.gerer_touches(keys, shift)

                with state_lock:
                    manager_vue.afficher(partie_terminee=partie_terminee, gagnant=gagnant_label, gagnant_id=gagnant_id)
                
                draw_lan_overlay()
                pygame.display.flip()
                clock.tick(60)

        try:
            pygame_loop_lan()
        finally:
            try:
                sock.close()
            except Exception:
                pass
            pygame.quit()
        return

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
        liste_message = []
        while running:
            liste_message = ipc.recevoir()  # Traite les messages IPC en temps réel
            if len(liste_message) > 0:
                for msg in liste_message:
                    print(f"[IPC] Message recu: {msg}")
                    partie.appliquer_message(msg)
                
            liste_message = []          
    
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