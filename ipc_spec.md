# Spécification Technique de l'IPC (Inter-Process Communication)

## 1. Présentation du Système
L'architecture logicielle repose sur deux processus distincts pour supporter l'IA et les mécanismes réseau :
* [cite_start]**Processus Python :** Gère la logique métier, l'IA et la visualisation[cite: 146, 147].
* [cite_start]**Processus C :** Développé en C avec l'interface socket, il gère la répartition sans serveur.

## 2. Mécanisme de Communication
* [cite_start]**Type de connexion :** Socket UDP (AF_INET, SOCK_DGRAM).
* **Hôte :** 127.0.0.1 (localhost).
* **Ports :** * Le processus **C** écoute sur le port **9999**.
    * Le processus **Python** écoute sur le port **9998**.
* **Modèle :** Mode datagramme (pas de connexion persistante).

## 3. Format des Messages
* En UDP, chaque `sendto()` contient un message JSON brut complet.
* **Limite :** Les messages doivent rester inférieurs à ~1400 octets pour éviter la fragmentation.

## 4. Format des Données (JSON)
[cite_start]Les échanges utilisent le format JSON pour assurer la mise à jour immédiate de la scène[cite: 9, 157].

### Exemple : Mise à jour de position (UPDATE)
```json
{
  "type": "UPDATE",
  "player_id": 1,
  "entity_id": 101,
  "action": "MOVE",
  "data": { "x": 45, "y": 20 }
}