from flask_socketio import emit
from game.game import Game
import chess
from flask import request

game = Game()

players = {}
order = []

def send_players_info():
    emit('players_info', {
        'w': next((p['nom'] for p in players.values() if p['couleur'] == 'w'), None),
        'b': next((p['nom'] for p in players.values() if p['couleur'] == 'b'), None)
    }, broadcast=True)

def register_websocket_events(socketio):
    @socketio.on('get_board')
    def handle_get_board():
        print("Envoi du plateau...")
        emit('update_board', game.get_fen())

    @socketio.on('move_piece')
    def handle_move_piece(data):
        from_row = data['from']['row']
        from_col = data['from']['col']
        to_row = data['to']['row']
        to_col = data['to']['col']
        from_square = chess.square(from_col, 7 - from_row)
        to_square = chess.square(to_col, 7 - to_row)
        move = chess.Move(from_square, to_square)

        if move in game.board.legal_moves:
            game.board.push(move)
            emit('board_update', game.get_fen(), broadcast=True)
            reason = game.is_game_over()
            if reason:
                emit('game_over', {'reason': reason}, broadcast=True)
        else:
            emit('illegal_move', {'message': 'Mouvement illégal!'})

    @socketio.on('restart_game')
    def handle_restart_game():
        game.start_game()
        emit('update_board', game.get_fen(), broadcast=True)

    @socketio.on('get_legal_moves')
    def handle_get_legal_moves(data):
        row = data['row']
        col = data['col']
        legal_moves = game.get_legal_moves(row, col)
        emit('legal_moves', legal_moves)

    @socketio.on('register_player')
    def handle_register(data):
        nom = data['nom']
        sid = request.sid

        if len(order) < 2:
            couleur = 'w' if len(order) == 0 else 'b'
            players[sid] = {"nom": nom, "couleur": couleur}
            order.append(sid)
            emit('player_accepted', {'nom': nom, 'couleur': couleur}, room=sid)
            print(f"{nom} a rejoint comme joueur {couleur}")
        else:
            emit('spectator', {'message': "Vous êtes spectateur."}, room=sid)
            print(f"{nom} a rejoint comme spectateur.")
        
        send_players_info()  # mise à jour des noms

    @socketio.on('disconnect')
    def handle_disconnect():
        sid = request.sid
        if sid in players:
            nom = players[sid]['nom']
            order.remove(sid)
            del players[sid]
            print(f"{nom} s'est déconnecté")
            send_players_info()  # mise à jour des noms

    @socketio.on('chat_message')
    def handle_chat_message(data):
        emit('chat_message', data, broadcast=True)
