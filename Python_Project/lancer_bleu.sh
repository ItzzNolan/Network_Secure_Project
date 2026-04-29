#!/bin/bash
cd ~/Network_project/Network_Secure_Project/Python_Project

# ON NETTOIE TOUJOURS AVANT DE LANCER LE BLEU
killall main_reseau
sleep 1

# ON LANCE LE RESEAU
./réseau/main_reseau &
sleep 1

# ON LANCE PYTHON
python3 battle.py run standard braindead --network --player-id 0