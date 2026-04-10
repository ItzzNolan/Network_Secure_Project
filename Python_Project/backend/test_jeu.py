# test_jeu.py
import socket
from datetime import datetime

class SimLogger:
    def __init__(self, filename:str = "simulation.log", echo:bool = True):
        self.filename = filename
        self.echo = echo
        
        with open(self.filename, "w", encoding="utf-8") as file:
            file.write(f"--- Simulation started {datetime.now()} ---\n\n")
    
    def log(self, msg:str = ""):
        if self.echo:
            print(msg)
        with open(self.filename, "a", encoding="utf-8") as file:
            file.write(msg+"\n")    

Logs = SimLogger("test.log") 

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("localhost", 9999))

print("Listening on 9999...")
Logs.log("Listening on 9999...")
while True:
    data, addr = sock.recvfrom(65535)
    print("RECU:", data.decode())
    Logs.log(f"RECU: {data.decode()}")

    