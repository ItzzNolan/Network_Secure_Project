#!/bin/bash
cd ~/Network_project/Network_Secure_Project/Python_Project

# lancer le processus C en arriere-plan
./réseau/main_reseau &
sleep 1

# lancer le jeu en tant que ROUGE (player 1, port 9997)
python3 battle.py run standard braindead --network --player-id 1
