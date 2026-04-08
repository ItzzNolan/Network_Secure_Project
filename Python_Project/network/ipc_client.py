class IPCClient:
    def __init__(self):
        print("[IPC] Client initialisé")

    def envoyer(self, message):
        print("[IPC SEND]", message)