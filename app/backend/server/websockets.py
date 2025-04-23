from flask_socketio import emit
from game.game import Game
import chess
from flask import request
import random
import eventlet

game = Game()

players = {}
order = []

def jouer_coup_ia(socketio):
    if game.board.turn == chess.BLACK:
        eventlet.sleep(0.5)  # Pause pour simuler le temps de réflexion de l'IA
        # IA simple : choisir un coup aléatoire parmi les coups légaux
        legal_moves = list(game.board.legal_moves)
        if legal_moves:
            coup = random.choice(legal_moves)
            game.board.push(coup)
            socketio.emit('board_update', game.get_fen())

            if game.is_game_over():
                socketio.emit('game_over', {'reason': game.is_game_over()})

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

        # Vérifier s’il y a une promotion demandée depuis le client
        promotion_code = data.get('promotion')
        promotion_piece = None
        if promotion_code:
            mapping = {
                'q': chess.QUEEN,
                'r': chess.ROOK,
                'b': chess.BISHOP,
                'n': chess.KNIGHT
            }
            promotion_piece = mapping.get(promotion_code)

        # Construire le coup (avec ou sans promotion)
        move = chess.Move(from_square, to_square, promotion=promotion_piece)

        if move in game.board.legal_moves:
            game.board.push(move)
            emit('board_update', game.get_fen())
            reason = game.is_game_over()
            if reason:
                emit('game_over', {'reason': reason})
        else:
            emit('illegal_move', {'message': 'Mouvement illégal!'})

        # Si on est en mode IA, faire jouer l'IA après le coup du joueur
        joueur = players.get(request.sid)
        if joueur and joueur.get("contre_ia"):
            jouer_coup_ia(socketio)


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
        mode = data.get('mode', 'multi')
        sid = request.sid

        if mode == "ia":
            # Mode IA : le joueur est blanc, l’IA est noire
            players[sid] = {"nom": nom, "couleur": "w", "contre_ia": True}
            order.append(sid)
            players["ia"] = {"nom": "IA", "couleur": "b"}
            emit('player_accepted', {'nom': nom, 'couleur': 'w'}, room=sid)
            send_players_info()
            print(f"{nom} joue contre l'IA.")

        elif len(order) < 2:
            couleur = 'w' if len(order) == 0 else 'b'
            players[sid] = {"nom": nom, "couleur": couleur, "contre_ia": False}
            order.append(sid)
            emit('player_accepted', {'nom': nom, 'couleur': couleur}, room=sid)
            print(f"{nom} a rejoint comme joueur {couleur}")
        else:
            emit('spectator', {'message': "Vous êtes spectateur."}, room=sid)
            print(f"{nom} a rejoint comme spectateur.")

        send_players_info()

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
