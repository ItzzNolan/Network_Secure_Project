import socket

# Configuration : On écoute sur le port 9998 (défini dans ipc_spec.md)
UDP_IP = "127.0.0.1"
UDP_PORT = 9998

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Python : J'écoute sur le port {UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(1024) # Attente du message du C
<<<<<<< HEAD
    print(f"Python : Message reçu du C -> {data.decode('utf-8')}")
=======
    print(f"Python : Message reçu du C -> {data.decode('utf-8')}")
>>>>>>> b27404374e7cd2a70015c1e58bd1970f78831932
