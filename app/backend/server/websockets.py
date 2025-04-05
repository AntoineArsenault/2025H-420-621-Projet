from flask_socketio import emit
from game.game import Game
game = Game()

# Fonction d'enregistrement des événements
def register_websocket_events(socketio):
    """Enregistre les événements de WebSocket."""
    
    # Lorsqu'un client demande l'état du plateau
    @socketio.on('get_board')
    def handle_get_board():
        print("Envoi du plateau...")
        emit('update_board', game.get_board())  # Envoie l'état du plateau au frontend
