#!/bin/bash
#cd ~/Network_project/Network_Secure_Project/Python_Project

# lancer le processus C en arrière-plan
./réseau/main_reseau &
sleep 1

# lancer le jeu
python3 battle.py run standard --network --player-id 1