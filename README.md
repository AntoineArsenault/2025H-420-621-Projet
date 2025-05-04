# 420-621-Projet : Jeu d'échecs multi-joueurs

## **Description**
Bienvenue dans le projet de jeu d'échecs multi-joueurs, développé dans le cadre du cours **420-621**. Ce projet s'étalera sur **4 semaines** et sera réalisé en **équipe de 2**. L'objectif est de concevoir un jeu d'échecs fonctionnel, jouable à deux ou contre une IA, avec une interface web interactive et une communication en temps réel via WebSockets.

Chaque semaine, des indications spécifiques seront fournies pour guider le développement. Un **journal de bord** devra être déposé sur Léa chaque dimanche avant minuit pour documenter vos progrès. La **présentation et l'évaluation** du projet auront lieu lors de la **5e semaine** (semaine 14).

## Évaluation
Lors de la 5e semaine du projet, chaque équipe devra présenter sa solution, en expliquant les choix de conception, en faisant une démonstration de l'application et en répondant aux questions du professeur.
Chaque équipe présentera à tour de rôle leur projet, selon un ordre pré-établi.
La grille d'évaluation du projet se trouve [ici](https://cmaisonneuveqcca-my.sharepoint.com/:x:/g/personal/eterriault_cmaisonneuve_qc_ca/EV6TFQNx_o1Ko-Jl604Wn28B9TnuOxS9cKd5_EG0wPLMjA?e=zBumxV) et l'horaire d'évaluation des équipes se trouve [ici](https://cmaisonneuveqcca-my.sharepoint.com/:x:/r/personal/eterriault_cmaisonneuve_qc_ca/Documents/H25/420-621-MA/Projet/horaire_evaluation.xlsx?d=wd4f2cd06f584428b8da11f8eb5b78e9c&csf=1&web=1&e=8rQqkd).

Chaque membre de l'équipe se verra attribué la même note **à moins qu'un débalancement dans la contribution de chaque membre** soit porté à l'attention du professeur. Dans le cas échéant, un ajustement à la note se fera de façon individuelle.

L'évaluation de chaque équipe prendra environ 15 min et se déroulera comme suit:
1. **Démonstration de votre projet**
   - Connexion du ou des joueur(s)
   - Choix du mode (solo ou multijoueur)
   - Connexion en tant que spectateur
   - Déplacement des pièces, tour par tour (ou réponse de l'ordinateur si mode solo)
   - Fin de partie
   - Gestion des erreurs: mauvais coup, mauvais joueur qui joue

2. **Présentation des fichiers, des choix de conception et de la structure du code**
   
3. **Questions du professeur sur l'implantation des fonctionnalités et la structure du code pour tester votre compréhension**
   
---
## **Technologies utilisées**
- **WebSockets** : Communication en temps réel entre les joueurs.
- **Flask** : Framework web pour le backend.
- **Python** : Langage principal pour la logique du jeu.
- **Pygame** : (Si applicable) pour des animations ou une interface graphique alternative.

---
## **Instructions pour démarrer**

1. Activer l'environnement virtuel (optionnel mais recommandé)
```bash
cd app/backend  # Aller dans le dossier backend
python -m venv .venv       # Créer un environnement virtuel
source .venv/bin/activate  # Activer sur macOS/Linux
.venv\Scripts\activate     # Activer sur Windows
```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancez le serveur Flask :
   ```bash
   cd backend
   python -m server.app
   ```
4. Ouvrez le jeu dans votre navigateur à l'adresse `http://<adresse_du_serveur>:5000`.

---

## **Gestion du projet avec Git (optionnel mais recommandé)**

Bien que l'utilisation de Git ne soit pas obligatoire, elle est fortement recommandée pour suivre les modifications de votre projet, collaborer efficacement avec votre coéquipier, et sauvegarder votre travail sur GitHub.

Pour des instructions détaillées sur la configuration de Git, la création d'un dépôt GitHub, et la gestion des commits et des pushs, consultez le fichier [git_setup.md](git_setup.md) à la racine du projet.

---

## **Fonctionnalités prévues**
### **Semaine 1 : Mise en place de la structure et des bases**
- Initialisation du projet et mise en place de la structure des fichiers.
- Création d'un échiquier statique affiché dans le navigateur.
- Développement de la logique de base pour les mouvements des pièces.

### **Semaine 2 : Implémentation de la logique de jeu**
- Implémentation des règles et de la logique de jeu.
- Gestion de la fin de jeu et du tour des joueurs.

### **Semaine 3 : Jeu mode multi-joueurs**
- Intégration du jeu multi-joueurs.
- Gestion des événements de connexion et de déconnexion des joueurs.
- Synchronisation des coups entre les clients.

### **Semaine 4 : Jeu mode solo**
- Implémentation d'une IA pour permettre le jeu en solo.
- Gestion des modes de jeu (multi-joueur ou contre l'IA).
- (Facultatif) Utilisation d'une bibliothèque comme `Stockfish` pour les mouvements de l'IA.

---

## Structure des fichiers

Voici une suggestion d'architecture pour organiser le projet :

```text
|📂 app/ (Racine du projet)
│
├──📂 backend/ (Serveur Flask et logique du jeu)
│ ├── 📂 game/ (Moteur du jeu)
│ │ ├── __init__.py → Initialise le module
│ │ ├── game.py → Contient la classe Game, qui gère l'état du jeu
│ │ ├── piece.py → Définit la classe Piece et ses sous-classes (Pawn, Rook, etc.)
│ │ ├── rules.py → Implémente la validation des mouvements
│ │ ├── board.py → Initialise et met à jour le plateau
│ │
│ ├── 📂 server/ (Serveur Flask)
│ │ ├── __init__.py → Initialise le serveur
│ │ ├── app.py → Gère l’application Flask et les routes
│ │ ├── websockets.py → Gère la communication WebSockets avec les clients
│ │
│ ├── 📂 tests/ (Tests unitaires)
│ │ ├── test_game.py → Vérifie la logique du jeu
│ │ ├── test_api.py → Vérifie les routes Flask
│ │
│ ├── requirements.txt → Dépendances du projet (Flask, Flask-SocketIO, python-chess, etc.)
│ ├── config.py → Configuration du projet (paramètres Flask, WebSockets)
│
├── 📂 frontend/ (Interface utilisateur)
│ ├── 📂 static/ (Fichiers statiques : CSS, JS, images)
│ | ├── 📂 assets/
│ | | ├── black_pawn.png
│ | | ├── white_pawn.png
│ | | └── ...
│ │ ├── style.css → Styles du plateau
│ │ ├── script.js → Gestion des interactions (mise à jour du plateau, WebSockets)
│ │
│ ├── 📂 templates/ (Templates HTML pour Flask)
│ │ ├── index.html → Interface principale du jeu
```
---

## Rôles des fichiers

### **Backend**
- `game.py` : Gère la logique du jeu.
- `rules.py` : Vérifie les règles des déplacements.
- `server/app.py` : Gère l’API Flask et sert le frontend.
- `websockets.py` : Envoie et reçoit les mises à jour des coups en temps réel.

### **Frontend**
- `index.html` : Affiche le plateau et gère l'affichage des pièces.
- `script.js` : Écoute les WebSockets et met à jour l'interface.
- `style.css` : Améliore le rendu visuel du jeu.

### **Tests**
- Vérification des règles et des API avec `test_game.py` et `test_api.py`.

---
