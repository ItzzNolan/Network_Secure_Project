#!/bin/bash
cd ~/Network_project/Network_Secure_Project/Python_Project

PLAYER_ID=$1

if [ -z "$PLAYER_ID" ]; then
  echo "Erreur: Tu dois donner un numero de joueur !"
  echo "Exemples :"
  echo "  ./lancer_joueur.sh 0   (Joueur BLEU - Initialise le reseau)"
  echo "  ./lancer_joueur.sh 1   (Joueur ROUGE)"
  echo "  ./lancer_joueur.sh 2   (Joueur VERT)"
  echo "  ./lancer_joueur.sh 3   (Joueur JAUNE)"
  exit 1
fi

if [ "$PLAYER_ID" -eq 0 ]; then
  echo "Initialisation du reseau P2P par le Joueur 0..."
  killall main_reseau 2>/dev/null
  sleep 0.5
  ./réseau/main_reseau &
  sleep 1
fi
IA="daft"
if [ "$PLAYER_ID" -eq 0 ]; then IA="braindead"; fi
if [ "$PLAYER_ID" -eq 2 ]; then IA="turtle"; fi

python3 battle.py run standard $IA --network --player-id $PLAYER_ID
