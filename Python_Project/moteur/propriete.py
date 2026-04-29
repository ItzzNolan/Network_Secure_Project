class Propriete:
    def __init__(self, player_id, ipc):
        self.player_id = player_id
        self.ipc = ipc
        self.table = {}  # {entity_id: owner_id}

    def suis_proprietaire(self, entity_id):
        return self.table.get(entity_id) == self.player_id
    
    def demander_propriete(self, entity_id):
        self.ipc.envoyer({
            "type": "REQUEST_PROP",
            "entity_id": entity_id,
            "requester_id": self.player_id
        })

        reponse = self.ipc.attendre_reponse_prop(entity_id)

        if not reponse:
            return None

        if reponse["type"] == "GRANT_PROP":
            self.table[entity_id] = self.player_id
            return reponse["state"]

        return None
    
    def ceder_propriete(self, entity_id, demandeur_id, unit):
        state = {
            "x": unit.coords[0],
            "y": unit.coords[1],
            "hp": unit.HP
        }

        self.ipc.envoyer({
            "type": "GRANT_PROP",
            "entity_id": entity_id,
            "state": state,
            "new_owner": demandeur_id
        })

        self.table[entity_id] = demandeur_id

    def refuser_propriete(self, entity_id, demandeur_id, raison):
        self.ipc.envoyer({
            "type": "DENY_PROP",
            "entity_id": entity_id,
            "reason": raison
        })

    