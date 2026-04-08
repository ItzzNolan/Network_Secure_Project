class FakeNetwork:
    def __init__(self):
        self.actions = [
            {"type": "move", "unit_id": 0, "x": 5, "y": 5},
            {"type": "move", "unit_id": 1, "x": 6, "y": 5},
        ]

    def receive(self):
        if self.actions:
            return [self.actions.pop(0)]
        return []

    def send(self, data):
        print("ETAT ENVOYÉ :", data)

    