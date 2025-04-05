import os
from flask import Flask, render_template
from game import Game
from flask_socketio import SocketIO

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
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
