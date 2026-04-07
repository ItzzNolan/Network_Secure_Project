# backend/save_manager.py

import json
import os
import webbrowser
from datetime import datetime


class SaveManager:
    """Gestionnaire de sauvegardes et exports pour le jeu"""
    
    SAVE_DIR = "saves"
    QUICKSAVE_FILE = "quicksave.json"
    HTML_FILE = "game_state.html"
    
    def __init__(self):
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)
    
    def _get_path(self, filename):
        return os.path.join(self.SAVE_DIR, filename)
    
    # ==================== SAVE / LOAD ====================
    
    def sauvegarder(self, jeu, filename=None):
        """Sauvegarde l'etat du jeu dans un fichier JSON"""
        if filename is None:
            filename = self.QUICKSAVE_FILE
        
        filepath = self._get_path(filename)
        
        try:
            data = {
                'tour': jeu._tour,
                'carte': {
                    'largeur': jeu.carte.largeur,
                    'hauteur': jeu.carte.hauteur
                },
                'unites': [
                    {
                        'id': getattr(u, 'id', i),
                        'type': u.Unit,
                        'equipe': u.equipe,
                        'coords': list(u.coords) if u.coords else None,
                        'HP': u.HP,
                        'alive': u.alive,
                    }
                    for i, u in enumerate(jeu.unites)
                ],
                'generaux': {
                    '0': type(jeu.generaux[0]).__name__ if 0 in jeu.generaux else 'unknown',
                    '1': type(jeu.generaux[1]).__name__ if 1 in jeu.generaux else 'unknown',
                },
                'metadata': {
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'version': '1.0'
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[SAVE] Partie sauvegardee: {filepath}")
            return True
            
        except Exception as e:
            print(f"[SAVE] Erreur: {e}")
            return False
    
    def charger(self, jeu, filename=None):
        """Charge l'etat du jeu depuis un fichier JSON"""
        from backend.carte import Carte
        from backend.Units import Unit
        
        if filename is None:
            filename = self.QUICKSAVE_FILE
        
        filepath = self._get_path(filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            jeu._tour = data['tour']
            jeu.carte = Carte(
                largeur=data['carte']['largeur'],
                hauteur=data['carte']['hauteur']
            )
            jeu.unites = []
            
            for u_data in data['unites']:
                unite = Unit(nomUnite=u_data['type'])
                unite.id = u_data.get('id', len(jeu.unites))
                unite.equipe = u_data['equipe']
                unite.coords = tuple(u_data['coords']) if u_data['coords'] else None
                unite.HP = u_data['HP']
                unite.alive = u_data['alive']
                jeu.unites.append(unite)
            
            date_str = data.get('metadata', {}).get('date', '?')
            print(f"[LOAD] Partie chargee: {filepath} ({date_str})")
            return True
            
        except FileNotFoundError:
            print(f"[LOAD] Aucune sauvegarde trouvee")
            return False
        except Exception as e:
            print(f"[LOAD] Erreur: {e}")
            return False
    
    def quicksave_existe(self):
        """Verifie si un quicksave existe"""
        return os.path.exists(self._get_path(self.QUICKSAVE_FILE))
    
    # ==================== HTML EXPORT ====================
    
    def generer_html_stats(self, jeu, filepath=None):
        """Genere une page HTML avec les stats de toutes les unites"""
        if filepath is None:
            filepath = self.HTML_FILE
        
        bleus = [u for u in jeu.unites if u.alive and u.equipe == 0]
        rouges = [u for u in jeu.unites if u.alive and u.equipe == 1]
        
        # Noms des generaux
        nom_general_bleu = jeu.generaux[0].name if 0 in jeu.generaux else "Inconnu"
        nom_general_rouge = jeu.generaux[1].name if 1 in jeu.generaux else "Inconnu"
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Etat du Jeu - Tour {jeu._tour}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
        h1 {{ color: #00ff88; border-bottom: 2px solid #00ff88; padding-bottom: 10px; }}
        h2 {{ cursor: pointer; padding: 10px; border-radius: 5px; margin-top: 20px; }}
        .bleu {{ background: #2040a0; }}
        .rouge {{ background: #a02020; }}
        .stats-box {{ background: #252545; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #444; }}
        th {{ background: #333355; }}
        .summary {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .summary-card {{ background: #252545; padding: 20px; border-radius: 10px; min-width: 150px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #888; }}
        .summary-card .value {{ font-size: 32px; font-weight: bold; }}
        .bleu-text {{ color: #6699ff; }}
        .rouge-text {{ color: #ff6666; }}
    </style>
</head>
<body>
    <h1>Etat du Champ de Bataille - Tour {jeu._tour}</h1>
    
    <div class="summary">
        <div class="summary-card"><h3>Tour</h3><div class="value">{jeu._tour}</div></div>
        <div class="summary-card"><h3>General Bleu</h3><div class="value bleu-text" style="font-size:16px">{nom_general_bleu}</div></div>
        <div class="summary-card"><h3>General Rouge</h3><div class="value rouge-text" style="font-size:16px">{nom_general_rouge}</div></div>
        <div class="summary-card"><h3>Bleus</h3><div class="value bleu-text">{len(bleus)}</div></div>
        <div class="summary-card"><h3>Rouges</h3><div class="value rouge-text">{len(rouges)}</div></div>
    </div>
    
    <h2 class="bleu" onclick="document.getElementById('bleu-section').style.display = document.getElementById('bleu-section').style.display === 'none' ? 'block' : 'none'">
        Equipe Bleue ({len(bleus)} unites)
    </h2>
    <div id="bleu-section" class="stats-box">
        <table>
            <tr><th>#</th><th>Type</th><th>HP</th><th>Position</th></tr>
"""
        for i, u in enumerate(bleus, 1):
            html += f'<tr><td>{i}</td><td>{u.Unit}</td><td>{u.HP:.0f}</td><td>({u.coords[0]:.1f}, {u.coords[1]:.1f})</td></tr>\n'
        
        html += f"""        </table>
    </div>
    
    <h2 class="rouge" onclick="document.getElementById('rouge-section').style.display = document.getElementById('rouge-section').style.display === 'none' ? 'block' : 'none'">
        Equipe Rouge ({len(rouges)} unites)
    </h2>
    <div id="rouge-section" class="stats-box">
        <table>
            <tr><th>#</th><th>Type</th><th>HP</th><th>Position</th></tr>
"""
        for i, u in enumerate(rouges, 1):
            html += f'<tr><td>{i}</td><td>{u.Unit}</td><td>{u.HP:.0f}</td><td>({u.coords[0]:.1f}, {u.coords[1]:.1f})</td></tr>\n'
        
        html += """        </table>
    </div>
</body>
</html>"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[HTML] Stats generees: {filepath}")
            return filepath
        except Exception as e:
            print(f"[HTML] Erreur: {e}")
            return None
    
    def ouvrir_stats_html(self, jeu):
        """Genere et ouvre la page HTML des stats dans le navigateur"""
        filepath = self.generer_html_stats(jeu)
        if filepath:
            webbrowser.open('file://' + os.path.abspath(filepath))
            return True
        return False