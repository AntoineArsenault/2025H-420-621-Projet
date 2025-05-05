import os  # Permet de gérer les chemins de fichiers (ex : pour retrouver les dossiers du projet)
import socket  # Sert à connaître l'adresse IP locale de la machine
from flask import Flask, render_template  # Flask sert à créer des applications web simples
from game import Game  # Importe la classe Game (qui gère la logique du jeu d’échecs)
from flask_socketio import SocketIO  # SocketIO permet la communication en temps réel (WebSockets)
import atexit  # Permet d’exécuter du code à la fermeture de l’application (ex : pour arrêter Stockfish)
from .websockets import register_websocket_events, engine  # Importe la logique des sockets + le moteur d'échecs Stockfish

# Définir les chemins des dossiers du projet
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Donne le chemin du dossier actuel
TEMPLATES_DIR = os.path.join(BASE_DIR, "../../frontend/templates")  # Chemin vers les fichiers HTML
STATIC_DIR = os.path.join(BASE_DIR, "../../frontend/static")  # Chemin vers les fichiers CSS/JS/images

# Créer l'application Flask (site web)
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# Initialiser la communication WebSocket avec Flask
socketio = SocketIO(app)

# Route principale : quand l'utilisateur va sur le site ("/"), il reçoit la page HTML index.html
@app.route("/")
def home():
    """ Affiche la page principale du jeu. """
    return render_template("index.html")  # Flask va chercher le fichier dans frontend/templates/index.html

# Enregistre les événements WebSocket (définis dans websockets.py)
from .websockets import register_websocket_events
register_websocket_events(socketio)  # On transmet l’objet socketio pour qu’il soit utilisé dans websockets.py

# Ce qui suit ne s'exécute que si on lance ce fichier directement (pas si on l'importe)
if __name__ == "__main__":
    # Obtenir le nom de l’ordinateur et son adresse IP locale
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    # Affiche une adresse pour que d'autres appareils sur le même réseau puissent rejoindre le jeu
    print("🚀 Serveur lancé en local !")
    print(f"🌐 Adresse pour jouer sur un autre appareil : http://{local_ip}:5000\n")

    # Définir une fonction qui sera exécutée quand l'application s'arrête (fermeture du terminal par exemple)
    @atexit.register
    def shutdown_engine():
        """ Arrêter le moteur Stockfish proprement. """
        print("Arrêt du moteur Stockfish...")
        engine.quit()  # On demande à Stockfish de se fermer proprement

    # Démarre le serveur Flask avec SocketIO, accessible sur toutes les adresses IP de la machine
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
