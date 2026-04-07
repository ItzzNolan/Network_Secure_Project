# engine/game.py

import pygame
import sys

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Battle Run")

        self.clock = pygame.time.Clock()
        self.running = False
        self.paused = False

    def handle_global_inputs(self):
        """Gestion des touches globales : Esc = quitter, Espace = pause"""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            print("Quit requested by user.")
            self.running = False

        if keys[pygame.K_SPACE]:
            self.paused = not self.paused
            print("Pause toggled:", self.paused)
            pygame.time.wait(200)

    def game_loop(self):
        """Boucle principale du moteur"""
        self.running = True

        while self.running:
            dt = self.clock.tick(60)  # temps réel (60 FPS max)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_global_inputs()

            if not self.paused:
                self.update(dt)
                self.render()

        pygame.quit()
        sys.exit()

    def update(self, dt):
        """Logique de jeu (à compléter selon ton jeu)"""
        pass

    def render(self):
        """Dessin à l’écran (à compléter)"""
        self.screen.fill((30, 30, 30))
        pygame.display.flip()
