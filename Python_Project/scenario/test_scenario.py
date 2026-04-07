import unittest
from scenario_chevalier_piquier import scenario_piquiers_vs_chevaliers
from backend.jeu import Jeu
from backend.Units import Unit
from scenario.tournament_calcul import Tournament

class TestScenario(unittest.TestCase):
    def test_creation(self):
        mon_tournoi = Tournament(["Major DAFT", "Captain BRAINDEAD"], ["Piquiers vs Chevaliers"])
        main(mon_tournoi)
        mon_tournoi.generer_graphique("Evolution_Population")
        mon_tournoi.generer_rapport_html("rapport_scenario.html")
        # self.assertIsInstance(jeu, Jeu)
        # self.assertIsNotNone(jeu.carte)
        # #self.assertEqual(len(jeu.joueurs), 2)
        # self.assertGreater(len(jeu.unites), 0)

if __name__ == "__main__":
    unittest.main()
