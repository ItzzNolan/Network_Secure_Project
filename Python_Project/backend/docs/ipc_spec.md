# Spécification Technique de l'IPC (Inter-Process Communication)

## Présentation du Système

L'architecture logicielle repose sur deux processus distincts pour supporter l'IA et les mécanismes réseau :

* **Processus Python :** Gère la logique métier, l'IA et la visualisation.
* **Processus C :** Développé en C avec l'interface socket, il gère la répartition sans serveur.

## Mécanisme de Communication

* **Type de connexion :** Socket UDP (AF_INET, SOCK_DGRAM).
* **Hôte :** 127.0.0.1 (localhost).
* **Ports :**
    * Le processus **C** écoute sur le port **9999**.
    * Le processus **Python** écoute sur le port **9998**.
* **Modèle :** Mode datagramme (pas de connexion persistante).

## Format des Messages

* En UDP, chaque `sendto()` contient un message JSON brut complet.
* **Limite :** Les messages doivent rester inférieurs à ~1400 octets pour éviter la fragmentation.

## Format des Données (JSON)

Les échanges utilisent le format JSON pour assurer la mise à jour immédiate de la scène.
