# Projet Jeu d'échecs – Semaine 4 : Mode solo et choix du mode de jeu

Cette semaine, vous devez rendre votre jeu capable de fonctionner dans **deux modes** :  
- **Mode multijoueur** : deux joueurs humains jouent l’un contre l’autre (déjà implémenté).
- **Mode solo** : un joueur humain joue contre **l'ordinateur** (mouvements aléatoires).

---

## Objectifs de la semaine

1. **Permettre à l'utilisateur de choisir** au lancement entre :
   - "Jouer contre un autre joueur"
   - "Jouer contre l'ordinateur (mode solo)"
2. **Implanter un mode solo** où l'adversaire joue des coups **aléatoires valides**.
3. **Maintenir la possibilité de jouer en mode multijoueur** comme implémenté précédemment.
4. **Gérer la boucle de jeu correctement** dans les deux modes :
   - Tour par tour
   - Mise à jour du plateau après chaque coup

---

## Ce que vous devez modifier cette semaine:

- **Affichage d'une interface de choix (frontend)** au début (bouton, menu ou popup).
- **Connexion au serveur (backend)** avec l'information du mode choisi (`solo` ou `multijoueur`).
- En mode **solo** :
  - Après que l'utilisateur joue son coup, l'ordinateur répond automatiquement avec un coup aléatoire.
  - Vous pouvez utiliser `random.choice(list(board.legal_moves))` pour choisir un mouvement.
- En mode **multijoueur** :
  - Le comportement reste celui mis en place à la semaine 3 : deux joueurs connectés jouent en alternance.

---

## Conseils techniques

- Sur le serveur (`app.py` ou `websockets.py`), gérez une différence entre les parties en mode `solo` et celles en `multijoueur`.
- Associez à chaque partie :
  - Le plateau d’échecs (`chess.Board()`).
  - Le mode (`solo` ou `multi`).
- Lors de la réception d'un coup (`move_piece`), si le mode est `solo`, **faites jouer l'ordinateur immédiatement après** le coup du joueur.

---

## Étapes suggérées

1. Ajouter un **écran de choix de mode** (solo ou multi) à l'ouverture du jeu.
2. Adapter la gestion des connexions (`start_game` ou équivalent) pour créer soit une partie solo, soit multijoueur.
3. Implémenter une fonction serveur qui joue un **coup aléatoire** lorsque c’est le tour de l’ordinateur.
4. Tester que :
   - En mode solo, l'ordinateur répond automatiquement après chaque coup du joueur.
   - En mode multi, tout fonctionne comme avant.

---

## Bonus (facultatif points bonus lors de l'évaluation)

- Permettre de **revenir à l'écran d'accueil** après une partie pour choisir un nouveau mode.
- Améliorer l’IA pour jouer un coup plus intelligent que totalement aléatoire (voir ci-dessous).
- Autres fonctionnalités qui rendent la navigation plus agréable et fluide.

### Bonus: Introduire IA avec Stockfish

Si vous voulez aller plus loin, vous pouvez remplacer l’IA aléatoire par une vraie intelligence artificielle en utilisant **Stockfish**.

### Instructions pour utiliser Stockfish :

1. **Téléchargez Stockfish**  
   - Allez sur [https://stockfishchess.org/download/](https://stockfishchess.org/download/)
   - Téléchargez la version correspondant à votre système (Linux, Windows, MacOS).
   - Placez le fichier exécutable (`stockfish` ou `stockfish.exe`) dans votre projet, par exemple dans un dossier `engine/`.

2. **Installer la bibliothèque nécessaire**  
   Dans votre environnement virtuel Python :
   ```bash
   pip install chess
   ```

3. **Implémenter Stockfish côté serveur**
```python
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci("./engine/stockfish")  # Adapter le chemin

def make_ai_move(board):
    result = engine.play(board, chess.engine.Limit(time=0.1))  # Cherche un coup en 100 ms
    return result.move
```

4. **Remplacer la fonction de coup aléatoire**
Dans votre fonction qui fait jouer l’IA, utilisez `make_ai_move(board)` pour obtenir un coup plus intelligent.

5. **Fermer correctionement l'engin à la fin**
```python
engine.quit()
```
---

## Journal de bord

N'oubliez pas de remplir votre **journal de bord pour la semaine 4** et de le remettre sur Léa.

---
