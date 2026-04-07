
import pygame
from frontend.vue_pygame import VuePygame
from frontend.vue_terminal import VueTerminal


class ManagerVue:
    def __init__(self, jeu):
        self.jeu = jeu
        self.vue_pygame = VuePygame(jeu.carte.largeur, jeu.carte.hauteur)
        self.vue_terminal = VueTerminal()
        self.mode_actuel = "PYGAME"

    def changer_mode(self):
        if self.mode_actuel == "PYGAME":
            self.mode_actuel = "TERMINAL"
            print("--- Passage en Vue Terminal ---")
        else:
            self.mode_actuel = "PYGAME"
            print("--- Passage en Vue Pygame ---")

    def afficher(self, partie_terminee=False, gagnant=None):
        if self.mode_actuel == "PYGAME":
            self.vue_pygame.afficher(self.jeu, partie_terminee, gagnant)
        else:
            self.vue_terminal.afficher(self.vue_pygame.screen, self.jeu, partie_terminee, gagnant)
