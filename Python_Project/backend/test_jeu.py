# test_jeu.py
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("localhost", 9999))

print("Listening on 9999...")

while True:
    data, addr = sock.recvfrom(65535)
    print("RECU:", data.decode())

    