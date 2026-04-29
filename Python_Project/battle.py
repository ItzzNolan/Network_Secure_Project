import sys, os, time, pygame
from threading import Thread
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.cli import parse_args
from backend.jeu import Jeu, get_team_name
from frontend.manager_vue import ManagerVue
running, paused = True, False
def cmd_run(args):
    global running, paused
    p = Jeu(args.map_size, args.map_size)
    p.player_id = args.player_id
    p.next_player_id = p.player_id
    p.ajouter_joueur(args.ais[0], {"Knight": 20})
    if args.network: p.envoyer_join()
    mv = ManagerVue(p)
    def tour_jeu():
        while running:
            if not paused: p.mettre_a_jour()
            time.sleep(0.1)
    def reception():
        ipc = p.get_ipc()
        while running:
            try:
                msgs = ipc.recevoir()
                for m in msgs: p.appliquer_message(m)
            except: pass
            time.sleep(0.01)
    Thread(target=tour_jeu, daemon=True).start()
    Thread(target=reception, daemon=True).start()
    c = pygame.time.Clock()
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
        mv.vue_pygame.gerer_camera(pygame.key.get_pressed())
        mv.afficher(partie_terminee=False)
        pygame.display.flip()
        c.tick(60)
    pygame.quit()
def main():
    args = parse_args()
    if args.command == "run": cmd_run(args)
if __name__ == "__main__": main()
