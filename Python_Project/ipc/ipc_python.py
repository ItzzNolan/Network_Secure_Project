import socket
import json
import time


PORT_PY_PAR_JOUEUR = {0: 9998, 1: 9997}

class IPCClient:
    def __init__(self, port_c=9999, port_python=9998, player_id=0):
        self.addr_c = ("localhost", port_c)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("localhost", port_python))
        self.sock.setblocking(False)
        self.file_attente = []

    def envoyer(self, msg: dict):
        data = json.dumps(msg).encode("utf-8")
        self.sock.sendto(data, self.addr_c)

    def recevoir(self) -> list:
        messages = []
        if self.file_attente:
            messages.extend(self.file_attente)
            self.file_attente.clear()
        while True:
            try:
                data, addr = self.sock.recvfrom(65535)
                msg = json.loads(data.decode("utf-8"))
                messages.append(msg)
            except BlockingIOError:
                break
        return messages

    def attendre_reponse_prop(self, entity_id, timeout=3):
        debut = time.time()
        while time.time() - debut < timeout:
            try:
                data, addr = self.sock.recvfrom(65535)
                msg = json.loads(data.decode("utf-8"))
                if msg.get("type") in ("GRANT_PROP", "DENY_PROP") and msg.get("entity_id") == entity_id:
                    return msg
                self.file_attente.append(msg)
            except BlockingIOError:
                time.sleep(0.01)
        return None   
    def fermer(self):
        self.sock.close()