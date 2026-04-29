#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
PLAYER_ID=$1
if [ -z "$PLAYER_ID" ]; then echo "Donne un ID (0 ou 1)"; exit 1; fi
if [ "$PLAYER_ID" -eq 0 ]; then
  killall main_reseau 2>/dev/null
  ./réseau/main_reseau &
  sleep 1
fi
IA="daft"; if [ "$PLAYER_ID" -eq 0 ]; then IA="braindead"; fi
python3 battle.py run standard $IA --network --player-id $PLAYER_ID
