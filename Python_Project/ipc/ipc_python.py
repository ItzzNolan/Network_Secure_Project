import socket
import json

class IPCClient:
    def __init__(self, port_c=9999, port_python=9998): 
        self.addr_c = ("localhost", port_c)  

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sock.bind(("localhost", port_python))  
        self.sock.setblocking(False) 

    def envoyer(self, msg: dict):
        data = json.dumps(msg).encode("utf-8")
        self.sock.sendto(data, self.addr_c)

    def recevoir(self) -> list:
        messages = []
        while True:
            try:
                data, addr = self.sock.recvfrom(65535)
                msg = json.loads(data.decode("utf-8"))
                messages.append(msg)
            except BlockingIOError:
                break  
        return messages

    def fermer(self):
        self.sock.close()