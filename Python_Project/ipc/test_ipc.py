import time
from ipc_python import IPCClient
def test():
    client = IPCClient(port_c=9999, port_python=9998)
    print("socket UDP prêt")

    msg = {"type": "UPDATE", "action": "MOVE", "entity_id": 1, "x": 5, "y": 3, "player_id": 1}
    client.envoyer(msg)
    print(f"envoyé : {msg}")

    time.sleep(0.5)

    reponses = client.recevoir()
    if reponses:
        for r in reponses:
            print(f"reçu : {r}")
    else:
        print("rien reçu (le processus C a peut-être pas renvoyé de réponse)")

    client.fermer()
    print("socket fermé")
    
if __name__ == "__main__":
    test()