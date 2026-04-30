import datetime

class Tournament:
    def __init__(self, generals_names, scenarios):
        # On force les noms en minuscules pour éviter les erreurs de correspondance (0.0%)
        self.generals = [str(g).lower() for g in generals_names]
        # On récupère les noms des scénarios
        self.scenarios_list = list(scenarios.keys()) if isinstance(scenarios, dict) else scenarios
        
        # Structure de la matrice : {Scenario: {IA_A: {IA_B: [victoires, total]}}}
        self.matrix = {str(s).lower(): {g1: {g2: [0, 0] for g2 in self.generals} 
                       for g1 in self.generals} for s in self.scenarios_list}

    def enregistrer_resultat(self, scenario, ia_a, ia_b, vainqueur):
        """Enregistre proprement les résultats en forçant la casse."""
        s = str(scenario).lower()
        a = str(ia_a).lower()
        b = str(ia_b).lower()
        v = str(vainqueur).lower() if vainqueur else None

        if s in self.matrix:
            self.matrix[s][a][b][1] += 1
            self.matrix[s][b][a][1] += 1
            if v == a:
                self.matrix[s][a][b][0] += 1
            elif v == b:
                self.matrix[s][b][a][0] += 1

    def generer_rapport_html(self, filename="rapport_final.html"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # --- CALCULS PRÉALABLES POUR 5.a ---
        global_scores = {g: [0, 0] for g in self.generals}
        for s in self.matrix.keys():
            for g1 in self.generals:
                for g2 in self.generals:
                    global_scores[g1][0] += self.matrix[s][g1][g2][0]
                    global_scores[g1][1] += self.matrix[s][g1][g2][1]

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; margin: 30px; background-color: #f4f4f4; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; background: white; }}
                th {{ background-color: #27ae60; color: white; padding: 12px; border: 1px solid #ddd; }}
                td {{ padding: 10px; border: 1px solid #ddd; text-align: center; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                h1, h2 {{ color: #2c3e50; }}
                .reflexive {{ background-color: #eee; font-style: italic; }}
            </style>
        </head>
        <body>
            <h1>Rapport de Tournoi Automatisé</h1>
            <p>Généré le : {now}</p>

            <h2>5.a Score Général (Global)</h2>
            <table>
                <tr><th>Général</th><th>Taux de Victoire Global</th></tr>
        """
        for g in self.generals:
            wins, total = global_scores[g]
            rate = (wins / total * 100) if total > 0 else 0.0
            html += f"<tr><td>{g.upper()}</td><td style='font-weight:bold;'>{rate:.1f}%</td></tr>"

        # --- 5.b MATRICE GLOBALE (CORRIGÉE) ---
        html += """
            </table>
            <h2>5.b Matrice Général vs Général (Global)</h2>
            <p>Performances cumulées sur l'ensemble des scénarios.</p>
            <table>
                <tr><th>vs</th>
        """
        for g in self.generals: html += f"<th>{g.upper()}</th>"
        html += "</tr>"

        for g1 in self.generals:
            html += f"<tr><td><strong>{g1.upper()}</strong></td>"
            for g2 in self.generals:
                g_wins = 0
                g_total = 0
                for s in self.matrix.keys(): # On boucle sur les données réelles
                    g_wins += self.matrix[s][g1][g2][0]
                    g_total += self.matrix[s][g1][g2][1]
                rate = (g_wins / g_total * 100) if g_total > 0 else 0.0
                html += f"<td>{rate:.1f}%</td>"
            html += "</tr>"
        html += "</table>"

        # --- 5.c DÉTAILS PAR SCÉNARIO (SANS DOUBLONS) ---
        html += "<h2>5.c Détails par Scénario</h2>"
        # On utilise directement les clés de la matrice pour éviter les doublons de liste
        for s in sorted(self.matrix.keys()):
            html += f"<h3>Scénario : {s}</h3>"
            html += "<table><tr><th>vs</th>"
            for g in self.generals: html += f"<th>{g.upper()}</th>"
            html += "</tr>"
            for g1 in self.generals:
                html += f"<tr><td><strong>{g1.upper()}</strong></td>"
                for g2 in self.generals:
                    wins, total = self.matrix[s][g1][g2]
                    rate = (wins / total * 100) if total > 0 else 0.0
                    html += f"<td>{rate:.1f}%</td>"
                html += "</tr>"
            html += "</table>"

        # --- 5.d GÉNÉRAL VS SCÉNARIO ---
        html += "<h2>5.d Général vs Scénario</h2><table><tr><th>Général \ Scénario</th>"
        for s in sorted(self.matrix.keys()): html += f"<th>{s}</th>"
        html += "</tr>"
        for g in self.generals:
            html += f"<tr><td><strong>{g.upper()}</strong></td>"
            for s in sorted(self.matrix.keys()):
                s_wins = sum(self.matrix[s][g][opp][0] for opp in self.generals)
                s_total = sum(self.matrix[s][g][opp][1] for opp in self.generals)
                rate = (s_wins / s_total * 100) if s_total > 0 else 0.0
                html += f"<td>{rate:.1f}%</td>"
            html += "</tr>"

        html += "</table></body></html>"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
            
           
         
