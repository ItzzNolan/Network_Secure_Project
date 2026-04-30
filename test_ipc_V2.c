import socket
import json

# Configuration
DEST_IP = "127.0.0.1"
DEST_PORT = 9999 # Le port d'écoute de ton programme C

def envoyer_test(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = json.dumps(data).encode('utf-8')
    sock.sendto(message, (DEST_IP, DEST_PORT))
    print(f"Envoyé : {data['type']}")

# Test 1 : Broadcast
envoyer_test({"type": "UPDATE", "player_id": 0})

# Test 2 : Ciblé
envoyer_test({"type": "GRANT_PROP", "new_owner": 1})