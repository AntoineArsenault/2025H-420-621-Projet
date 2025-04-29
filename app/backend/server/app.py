import os
import socket
from flask import Flask, render_template
from game import Game
from flask_socketio import SocketIO
import atexit
from .websockets import register_websocket_events, engine

# Définir les chemins des dossiers
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # backend/server/
TEMPLATES_DIR = os.path.join(BASE_DIR, "../../frontend/templates")
STATIC_DIR = os.path.join(BASE_DIR, "../../frontend/static")

# Créer l'application Flask
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# Initialiser SocketIO
socketio = SocketIO(app)

@app.route("/")
def home():
    """ Affiche la page principale du jeu. """
    return render_template("index.html")

# Importer et enregistrer les événements WebSocket
from .websockets import register_websocket_events
register_websocket_events(socketio)  # Passer l'objet socketio à la fonction

if __name__ == "__main__":
    # Obtenir l'adresse IP locale de la machine
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    # Afficher l'URL d'accès pour d'autres appareils sur le même réseau
    print("🚀 Serveur lancé en local !")
    print(f"🌐 Adresse pour jouer sur un autre appareil : http://{local_ip}:5000\n")

    # Arrêter le moteur Stockfish à la fermeture de l'application
    @atexit.register
    def shutdown_engine():
        """ Arrêter le moteur Stockfish proprement. """
        print("Arrêt du moteur Stockfish...")
        engine.quit()
        
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
