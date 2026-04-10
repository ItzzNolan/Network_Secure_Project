# Network_Secure_Project
Il s'agit d'une continuation du projet initial pour ajouter des interfaces reseaux et systemes.

Le [projet "MedievAIl BAIttle GenerAIl"](https://github.com/ItzzNolan/Project_Python) est un simulateur de batailles médiévales en 2.5D développé en Python.

L’objectif de la première version du projet est de mettre en place un jeu multi-participants réparti où chaque IA dispose d’une copie locale de la bataille et peut interagir avec ses propres éléments ainsi qu’avec ceux des autres IA. Cette version vise à tester la répartition sans serveur central, en permettant la mise à jour en quasi temps réel des actions, la gestion de la concurrence via des propriétés réseau transmissibles, et la participation dynamique de nouveaux joueurs qui peuvent placer leurs ressources en parallèle. L’accent est mis sur la simulation de batailles à deux participants, avec des interactions visibles et des incohérences tolérées, afin de valider le fonctionnement de la communication et de la coordination entre les IA dans un environnement réparti.

Ce projet est réalisé par une équipe de 8 étudiants -INSA CVL

## Équipe

- Fatiha
- Nolan
- Léo
- Imen
- Ines
- Clélie
- Romain
- Hippolyte


Technologies Utilisées

- **Langage :** Python 3.x
- **Graphisme :** Pygame (pour le frontend graphique)
- **Tests :** Pytest
- **Collaboration :** Git & GitHub

## Comment Installer et Lancer le Projet

Pour mettre en place l'environnement de développement et lancer le simulateur:

**1. Cloner le reposit**

Pour toute modification du code, on utilise...
```bash
git clone https://github.com/ItzzNolan/Network_Secure_Project
```
...Ou pour toute version alternative juste du main :
```bash
git clone --branch projet_python_main --single-branch --depth 1 https://github.com/ItzzNolan/Network_Secure_Project.git
```

**2. Lancer la simulation**

Au préalable, il est fortement recommandé d'installer le dernier package python pour pouvoir lancer la simulation.
Pour lancer la simulation, on vous encourage à utiliser cette syntaxe suivante et vous situer dans le repertoire locale dans lequel vous avez fait le clonage :

>   python3 battle.py run [type-scenario] [ia1] [ia2]

Par exemple :
```bash
python3 battle.py run standard braindead daft
```