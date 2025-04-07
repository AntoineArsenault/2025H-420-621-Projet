from flask_socketio import emit
from game.game import Game
import chess
game = Game()

# Fonction d'enregistrement des événements
def register_websocket_events(socketio):
    """Enregistre les événements de WebSocket."""
    
    # Lorsqu'un client demande l'état du plateau
    @socketio.on('get_board')
    def handle_get_board():
        print("Envoi du plateau...")
        emit('update_board', game.get_fen())  # Envoie l'état du plateau au frontend

    # Lorsqu'un client effectue un mouvement
    @socketio.on('move_piece')
    def handle_move_piece(data):
        from_row = data['from']['row']
        from_col = data['from']['col']
        to_row = data['to']['row']
        to_col = data['to']['col']

        # Convertir les coordonnées de la grille en notations FEN
        from_square = chess.square(from_col, 7 - from_row)  # Inverser la ligne (7 - row)
        to_square = chess.square(to_col, 7 - to_row)

        # Tenter de réaliser le mouvement
        move = chess.Move(from_square, to_square)

        if move in game.board.legal_moves:
            game.board.push(move)  # Appliquer le mouvement à l'échiquier
            emit('board_update', game.get_fen())  # Envoyer l'état mis à jour du plateau
        else:
            # Si le mouvement est invalide
            emit('illegal_move', {'message': 'Mouvement illégal!'})