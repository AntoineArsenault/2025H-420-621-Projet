# Semaine 3 : Communication en temps réel (multijoueur)

Cette semaine, vous devez rendre votre jeu jouable en **mode multijoueur en temps réel** en utilisant **Socket.IO**. Deux utilisateurs doivent pouvoir se connecter et jouer ensemble sur des machines différentes, ou dans des onglets ou navigateurs différents.

---

## Objectifs de la semaine

1. Permettre à deux joueurs de se connecter et de jouer une partie ensemble.
    - Gérer l’alternance des tours.
    - Synchroniser l’échiquier entre les deux joueurs.
    - Bloquer les clics pour le joueur qui n’a pas le tour.
2. Permettre à d'autres utilisateurs de se connecter en tant que spectateurs.
3. Tester la solution sur le réseau local.

---

## Étape 1 : Connexion des joueurs et synchronisation

- Lorsqu’un utilisateur arrive sur la page, **demandez-lui d’entrer son nom**.
- Créez une **liste des joueurs connectés**, stockée par exemple dans un fichier `app.py` ou `websockets.py`. Associez chaque joueur à son `socket.id`. Utilisez le gestionnaire d’événement `@socketio.on("connect")` (et d'autres évéenments WebSocket si nécessaire) pour détecter l’arrivée d’un nouveau joueur. (**astuce**: vous aurez probablement besoin de `from flask import request` pour obtenir le socket id)
- Lorsqu'un nouveau joueur se connecte, il/elle se fait attribuer une couleur (blanc ou noir) et un adversaire (si disponible)

### Règles :
- **Les 2 premiers joueurs** connectés sont les **joueurs actifs** (blanc et noir).
- Les **informations** suivantes doivent être affichées:
    - Nom du joueur courant (ou mode spectateur le cas échéant)
    - Couleur du joueur courant (ou rien si mode spectateur)
    - Nom de l'adversaire (ou rien si mode spectateur)
    - Tour courant (blanc ou noir)

---

## Étape 2 : Tour par tour et clics désactivés

Assurez vous que les joueurs peuvent joueur tour par tour et qu'ils ne peuvent déplacer que leurs pièces.
Si un joueur tente de jouer mais que ce n'est pas son tour, un message d'erreur devrait apparaître **seulement pour ce joueur** (pas pour son adversaire ni les spectateurs).

- Si ce n’est pas le tour du joueur :
  - Bloquez les clics sur l’échiquier.
  - Affichez un message du style : *"En attente du coup de l’adversaire..."*

---

## Étape 3 : Tester le mode multijoueur

### Test sur une **seule machine** :

Pour simuler deux joueurs :
- Ouvrez un **onglet normal** et un **onglet de navigation privée**.
- Ou ouvrez le jeu dans **deux navigateurs différents** (ex : Chrome et Firefox).

> :warning: Un nouvel onglet dans la même session de navigateur ne déclenche pas toujours un nouveau `connect`.

### Test sur **réseau local** :

Vous pouvez accéder au jeu depuis un autre appareil connecté au même réseau (en utilisant le routeur en classe ou un réseau domestique, mais pas Eduroam) :

---

## Bonus (facultatif mais possibilité d'obtenir plus de points)
- Ajouter un bouton pour recommencer une partie.
- Permettre à un joueur de quitter la partie et revenir à l’accueil.
- Envoyer un message à son adversaire (chat)
- Autres idées bien implantées

---

## Rappel - Journal de bord
N'oubliez pas de remplir votre journal de bord pour la semaine 3, en expliquant ce que vous avez fait, ce qui a fonctionné, ce qui a été difficile, etc. 

---

## Semaine prochaine
La semaine prochaine (après le congé de Pâques) nous introduirons le mode solo, qui permettra à un joueur de jouer seul contre l'ordinateur. Ce sera la dernière semaine du projet. La semaine suivante sera l'évaluation du projet.
