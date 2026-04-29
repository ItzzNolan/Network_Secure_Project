#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PLAYER_ID=$1
if [ -z "$PLAYER_ID" ]; then
  echo "[ERREUR] Donne un ID (0 ou 1)"
  exit 1
fi

# Chaque PC a besoin de son propre main_reseau pour le relais broadcast
echo "[SYSTEME] Init reseau par Joueur $PLAYER_ID"
killall main_reseau 2>/dev/null
sleep 0.5
./réseau/main_reseau &
sleep 1

IA="daft"
if [ "$PLAYER_ID" -eq 0 ]; then IA="braindead"; fi

# Port Python : J0=9998, J1=9997 (doit correspondre à ipc_c.c)
if [ "$PLAYER_ID" -eq 0 ]; then
  PY_PORT=9998
else
  PY_PORT=9997
fi

python3 battle.py run standard $IA --network --player-id $PLAYER_ID --py-port $PY_PORT
