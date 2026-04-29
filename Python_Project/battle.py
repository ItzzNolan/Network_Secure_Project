"""
MedievAIl BAIttle GenerAIl - CLI Entry Point
"""
import sys, os, time, pygame
from threading import Thread
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(parent_dir)
from utils.cli import parse_args
running, paused, partie_terminee = True, True, False
game_tick, gagnant_id, gagnant_label = 0, None, None

def choisir_ia_pygame(screen):
    font = pygame.font.SysFont(None, 40)
    small_font = pygame.font.SysFont(None, 28)
    ia_list = ["braindead", "daft", "turtle"]
    selected = 0
    clock = pygame.time.Clock()
    while True:
        screen.fill((30, 30, 30))
        screen.blit(font.render("Choisir une IA", True, (255, 255, 255)), (50, 50))
        for i, ia in enumerate(ia_list):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            screen.blit(small_font.render(ia, True, color), (60, 120 + i * 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected = (selected - 1) % len(ia_list)
                elif event.key == pygame.K_DOWN: selected = (selected + 1) % len(ia_list)
                elif event.key == pygame.K_RETURN: return ia_list[selected]
                elif event.key == pygame.K_ESCAPE: return None
        clock.tick(60)

def cmd_run(args):
    from frontend.manager_vue import ManagerVue
    from backend.save_manager import SaveManager
    from backend.jeu import get_team_name, Jeu
    global running, paused, partie_terminee, game_tick, gagnant_label, gagnant_id

    partie = Jeu(largeur=args.map_size, hauteur=args.map_size)
    if hasattr(args, 'player_id'):
        partie.player_id = args.player_id
        partie.next_player_id = args.player_id
        if args.network:
            print(f"[RESEAU] Lancement joueur ID : {args.player_id} ({get_team_name(args.player_id)})")
            paused = False 

    if args.ais:
        partie.ajouter_joueur(args.ais[0], {"Knight": 15, "Pikeman": 15, "Crossbowman": 10})
        
    if hasattr(args, 'network') and args.network:
        partie.envoyer_join()

    manager_vue = ManagerVue(partie)
    save_manager = SaveManager()
    clock = pygame.time.Clock()

    def tour_jeu():
        global running, paused, partie_terminee, game_tick, gagnant_id, gagnant_label
        logic_clock = pygame.time.Clock()
        while running:
            if not paused and not partie_terminee:
                game_tick += 1
                if game_tick >= 10:
                    game_tick = 0
                    partie.mettre_a_jour()
                    if hasattr(partie, 'check_victory'):
                        res = partie.check_victory()
                        if res is not None:
                            partie_terminee = True
                            gagnant_id = res
                            gagnant_label = "EGALITE" if res == -1 else f"{get_team_name(res)}"
            logic_clock.tick(60)

    def reception_message():
        global running
        purge_time = time.time() + 0.5
        while time.time() < purge_time:
            if hasattr(partie, 'ipc'):
                try: partie.ipc.recevoir()
                except: pass
        
        while running:
            if hasattr(partie, 'ipc'):
                try:
                    msgs = partie.ipc.recevoir()
                    if msgs:
                        for m in msgs: partie.appliquer_message(m)
                except: pass
            time.sleep(0.01)
    Thread(target=tour_jeu, daemon=True).start()
    Thread(target=reception_message, daemon=True).start()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_p and not partie_terminee:
                    paused = not paused
                    manager_vue.vue_pygame.paused = paused
                elif event.key == pygame.K_a:
                    if hasattr(args, 'network') and args.network:
                        print("\n[RESEAU] En multi, les joueurs doivent rejoindre via le réseau !\n")
                    else:
                        paused = True
                        ia_name = choisir_ia_pygame(manager_vue.vue_pygame.screen)
                        if ia_name: partie.ajouter_joueur(ia_name, {"Knight": 15, "Pikeman": 15})
                        paused = False

        keys = pygame.key.get_pressed()
        manager_vue.vue_pygame.gerer_camera(keys)
        manager_vue.afficher(partie_terminee=partie_terminee, gagnant=gagnant_label)
        pygame.display.flip()
        clock.tick(60)

    if hasattr(args, 'network') and args.network: partie.disconnect()
    pygame.quit()

def main():
    args = parse_args()
    if args.command == "run": cmd_run(args)

if __name__ == "__main__":
    main()
