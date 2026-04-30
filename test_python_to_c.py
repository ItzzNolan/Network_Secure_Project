import socket
import json

# Configuration identique à ipc_spec.md
IP_C = "127.0.0.1" # Localhost
PORT_C = 9999      # Le port que ton serveur C écoute

# 1. Création du socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. Préparation d'un message de jeu (Format JSON)
message = {
    "type": "UPDATE",
    "player_id": 1,
    "entity_id": 101,
    "action": "MOVE",
    "data": {"x": 50, "y": 30}
}

# 3. Envoi du message
print(f"Python : Envoi du message à {IP_C}:{PORT_C}...")
json_data = json.dumps(message).encode('utf-8')
sock.sendto(json_data, (IP_C, PORT_C))

print("Python : Message envoyé !")